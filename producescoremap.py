# Purpose of script: 
#Script input to the tool called 'Calculate Score Map'. 
#It outputs the total score of all pairwise combinations per cell.

#The output can either be for:
## all scores of marine uses where a specific inputted marine use is included
## all positive scores of marine uses where a specific inputted marine use is included
## all negative scores of marine uses where a specific inputted marine use is included
## all scores, or only negative or positive scores, of marine uses with a conflict-synergy input where a specific inputted marine use is included 

# It is voluntary to include a polygon for the area that both contain conflicts and synergies. This options is only enabled if a pairwise statistics map-based table is chosen to be outputted. 

# It is voluntary to only include a specific number of polygons of the highest score pairwise combinations. 

# It is voluntary to include 1-3 statistics tables that will be outputted in the result folder.   

# The output is cut after an inputted ocean raster dataset. 


# DATE OF CREATION: 28-10-2019
# AUTHOR: Ida Maria Bonnevie

#All the Python modules in the import statement needs to be installed. 
#An ESRI ArcMap license with Spatial Analyst extension activated is required for the tool to run as a script tool in ArcMap. 


# Toolvalidator script inputted in tool: 
#import arcpy
#import pandas as pd
#import numpy as np
#class ToolValidator(object):
#    """Class for validating a tool's parameter values 
#    and controlling the behavior of the tool's dialog."""
#    def __init__(self):
#        """Setup arcpy and the list of tool parameters."""
#        self.params = arcpy.GetParameterInfo()
#
#    def initializeParameters(self):
#        """Refine the properties of a tool's parameters. 
#        This method is called when the tool is opened."""
#        return
#
#    def updateParameters(self):
#        """Modify the values and properties of parameters before 
#        internal validation is performed. This method 
#        is called whenever a parameter has been changed."""
#
#        if self.params[10].altered and self.params[10].value == True:		
#            self.params[11].enabled = True
#        else: 
#            self.params[11].enabled = False
#            self.params[11].value = False
#        if self.params[11].value == True:
#            self.params[12].enabled = True
#            self.params[12].parameterType = "Required"
#        else: 
#            self.params[12].enabled = False
#            self.params[12].parameterType = "Optional"
#        if self.params[13].value == True:
#            self.params[14].enabled = True
#            excelfile_with_path = (self.params[1].value.value).replace("\a","\\a").replace("\b","\\b")
#            df = pd.read_excel(excelfile_with_path)
#            list_options = list(df['full_marine_use_category_name'])
#            self.params[14].filter.list = list_options
#        else:
#            self.params[14].enabled = False
#        return
#
#    def updateMessages(self):
#        """Modify the messages created by internal validation for each tool
#        parameter.  This method is called after internal validation."""
#        return
    

# import modules: 
import arcpy
import os
import pandas as pd
import numpy as np 
from collections import OrderedDict
import time
from datetime import datetime


# functions: 
def addField1(outputpath, fieldtype, fieldname = "valuefield", precision = "", decimals = "", field_length = ""): 
    if fieldtype == "TEXT":
        arcpy.AddField_management(outputpath, fieldname, fieldtype, precision, decimals, field_length, "", "NULLABLE", "NON_REQUIRED", "")        
    else: 
        arcpy.AddField_management(outputpath, fieldname, fieldtype, precision, decimals, "", "", "NULLABLE", "NON_REQUIRED", "")

def addLayerToMxd(mxd, df, inputname_inkl_folder, inputname_excl_folder, lyrfile, place, mode, inputfolder):
    if mode == "pairwise_polygon" or mode == "both_synergies_and_conflicts":
        rlayer1 = arcpy.mapping.Layer(os.path.join(os.path.dirname(__file__),inputfolder,inputname_excl_folder))
    elif mode == "mainmap":
        result = arcpy.MakeRasterLayer_management(inputname_inkl_folder, inputname_excl_folder[:-4]) 
        rlayer1 = result.getOutput(0)
    if mode == "both_synergies_and_conflicts": 
        rlayer1.transparency = 0 #here it is possible to set transparency of synergy-and-conflict-at-once.shp layer
    if lyrfile == "NotExisting": 
        lyrfile = "NotExisting"
    else: 
        arcpy.ApplySymbologyFromLayer_management(rlayer1, lyrfile)
        if mode == "pairwise_polygon": 
            if rlayer1.symbologyType == "UNIQUE_VALUES":
                rlayer1.symbology.addAllValues()
    arcpy.mapping.AddLayer(df, rlayer1, place)
    del mxd, df

def addScoreToDictPerMarineUseInMatrix(columnnumb, column, dictScoreMatrixPerMarineUse, spec_score_or_count, listOfLongMarineUseNames, iterator2):
    dictScoreMatrixPerMarineUse[column][columnnumb] = dictScoreMatrixPerMarineUse[column][columnnumb]+spec_score_or_count                    
    dictScoreMatrixPerMarineUse[listOfLongMarineUseNames[iterator2]][columnnumb] = dictScoreMatrixPerMarineUse[listOfLongMarineUseNames[iterator2]][columnnumb]+spec_score_or_count

def calculateField1(outputpath, valuefield, valueToInput, expression_type="VB"): 
    arcpy.CalculateField_management(outputpath, valuefield, valueToInput, expression_type, "")

def calculatePairwiseAndTotalScoreRasters(dictMarineUses, matrixexcelfile, scoretypeToCalculate, inputfolder, pairwise_output_folder, finalfoldername, scoreSumMarineUseMatrixTableIsTrue, scoreSumMarineUseMatrixTable, scoreSumMarineUseMapTableIsTrue, scoreSumMarineUseMapTable, scoreSumPairwiseMapTableIsTrue, scoreSumPairwiseMapTable, somePolygonsIsTrue, numbOfSome, onlyOneMarineUseInFocusIsTrue, marineUseInFocus, includeSynergyAndConflictAtOnceAreaIsTrue, lower_left_corner, dsc, spatial_ref, scoreraster_finaloutputname_only_ocean, oceanrastername_with_path, calculationtype):
    # import ocean array: 
    ocean_array = arcpy.RasterToNumPyArray(oceanrastername_with_path)
    ocean_array = ocean_array.astype(float)
    # preset parameters: 
    dfdesc = pd.read_excel(matrixexcelfile)    
    listOfLongMarineUseNames = dictMarineUses.keys()
    listpairwisescorerastername = []
    listpairwisescorepolygon = []
    listpairwisescorepolygonname = []
    dictpairwisescorerastername = {}
    dictScoreMatrixPerMarineUse = {}
    dictScoreMapPerMarineUse = {}
    dfScoreMapPerPairwise = "false" # false as default but might change
    for longname_marine_use in listOfLongMarineUseNames: 
        # table 1 inputs:
        if scoreSumMarineUseMatrixTableIsTrue == "true":
            if scoretypeToCalculate == "all":
                dictScoreMatrixPerMarineUse[longname_marine_use] = [0]*4 
            elif scoretypeToCalculate == "positive":
                dictScoreMatrixPerMarineUse[longname_marine_use] = [0]*2 
            elif scoretypeToCalculate == "negative":
                dictScoreMatrixPerMarineUse[longname_marine_use] = [0]*2 
        # table 2 inputs:
        if scoreSumMarineUseMapTableIsTrue == "true":         
            dictScoreMapPerMarineUse[longname_marine_use]=[0,0,0,0,0,0,0] 
            dictScoreMapPerMarineUse[longname_marine_use][3]=np.zeros_like(ocean_array, dtype=bool)
    # table 3 inputs:
    if scoreSumPairwiseMapTableIsTrue == "true":
        dfScoreMapPerPairwise = pd.DataFrame(columns=listOfLongMarineUseNames,index=listOfLongMarineUseNames)
        dfScoreMapPerPairwise.index.name = 'Idcolumn'
        dfScoreMapPerPairwise = dfScoreMapPerPairwise.reset_index()        
    firstraster = True
    firstsynergyandconflictarray = True 
    firstbasicarray = True 
    iterator1 = 0
    iterator2 = 1
    # main code: create total scores:  
    for column in listOfLongMarineUseNames: 
        inputrastername1 = dictMarineUses.get(column) 
        while iterator2 in range((iterator1+1),len(listOfLongMarineUseNames)):
            alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongMarineUseNames[iterator2], column].values
            if len(alldesc_nparray) > 0:
                alldesc = alldesc_nparray.item(0)
                if len(str(alldesc)) >= 4: 
                    if alldesc[:1] == "-": #1:2
                        spec_score = float(alldesc[:5].replace(",",".")) #1:6
                    else: 
                        spec_score = float(alldesc[:4].replace(",","."))             
                    inputrastername2 = dictMarineUses.get(listOfLongMarineUseNames[iterator2]) #get raster2
                    inputmarineuselongname1 = column
                    inputmarineuselongname2 = listOfLongMarineUseNames[iterator2]
                    # make pairwise score rasters for all, synergies (positive), or conflicts (negative) --->:
                    if (scoretypeToCalculate == "all") or ((scoretypeToCalculate == "positive") and (spec_score > 0)) or ((scoretypeToCalculate == "negative") and (spec_score < 0)):
                        # ---> either for all marine uses or a specific marine use: 
                        if ((onlyOneMarineUseInFocusIsTrue == "false") or ((onlyOneMarineUseInFocusIsTrue == "true") and (marineUseInFocus == "false")) or ((onlyOneMarineUseInFocusIsTrue == "true") and ((column == marineUseInFocus) or (listOfLongMarineUseNames[iterator2] == marineUseInFocus)))): 
                            (score_outras_array, dictScoreMapPerMarineUse, dfScoreMapPerPairwise, dictpairwisescorerastername, listpairwisescorerastername) = scoresToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisescorerastername, calculationtype, scoreSumMarineUseMapTableIsTrue, dictScoreMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, scoreSumPairwiseMapTableIsTrue, dfScoreMapPerPairwise, "true", listpairwisescorerastername, somePolygonsIsTrue, numbOfSome)
                            if firstraster == True:         
                                cummulated_score_outras_array = score_outras_array
                                firstraster = False
                                # make synergy-and-conflict area polygon - part 1:
                                if (includeSynergyAndConflictAtOnceAreaIsTrue == "true") and (firstsynergyandconflictarray == True):
                                    synergies_and_or_conflicts_array = np.copy(score_outras_array)
                                    synergies_and_or_conflicts_array[synergies_and_or_conflicts_array>0.] = 2 #2 is code for synergies
                                    synergies_and_or_conflicts_array[synergies_and_or_conflicts_array<0.] = 1 #1 is code for conflicts
                                    synergies_and_or_conflicts_array = synergies_and_or_conflicts_array.astype(int)
                                    firstsynergyandconflictarray = False
                                # make basic raster for extent - part 1: 
                                elif (firstbasicarray == True):
                                    cells_with_score_array = np.copy(score_outras_array)                                    
                                    cells_with_score_array[cells_with_score_array>0.] = 1 #1 is code for score
                                    cells_with_score_array[cells_with_score_array<0.] = 1 #1 is code for score
                                    cells_with_score_array = cells_with_score_array.astype(int)
                                    firstbasicarray = False
                            else: 
                                cummulated_score_outras_array += score_outras_array
                                # make synergy-and-conflict area polygon - part 2:
                                if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
                                    synergies_and_or_conflicts_array = updateSynergyAndConflictInCellKnowledge(score_outras_array, synergies_and_or_conflicts_array, spec_score)                                    
                                # make basic raster for extent - part 2: 
                                else: 
                                    cells_with_score_array = updateScoreCellCount(score_outras_array, cells_with_score_array)
                        # table 1 inputs:
                        if (scoreSumMarineUseMatrixTableIsTrue == "true"):
                            if ((scoretypeToCalculate == "all") and (spec_score > 0)) or (
                                (scoretypeToCalculate == "positive") and (spec_score > 0))  or (
                                (scoretypeToCalculate == "negative") and (spec_score < 0)):
                                addScoreToDictPerMarineUseInMatrix(0, column, dictScoreMatrixPerMarineUse, spec_score, listOfLongMarineUseNames, iterator2)
                                addScoreToDictPerMarineUseInMatrix(1, column, dictScoreMatrixPerMarineUse, 1, listOfLongMarineUseNames, iterator2)
                            elif ((scoretypeToCalculate == "all") and (spec_score < 0)):
                                addScoreToDictPerMarineUseInMatrix(2, column, dictScoreMatrixPerMarineUse, spec_score, listOfLongMarineUseNames, iterator2)
                                addScoreToDictPerMarineUseInMatrix(3, column, dictScoreMatrixPerMarineUse, 1, listOfLongMarineUseNames, iterator2)
                    # make synergy-and-conflict area polygon - part 3: 
                    if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
                        if ((spec_score > 0) and (scoretypeToCalculate == "negative")):
                            (score_outras_array, dictScoreMapPerMarineUse, dfScoreMapPerPairwise, dictpairwisescorerastername, listpairwisescorerastername) = scoresToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisescorerastername, calculationtype, scoreSumMarineUseMapTableIsTrue, dictScoreMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, scoreSumPairwiseMapTableIsTrue, dfScoreMapPerPairwise, "false", listpairwisescorerastername, somePolygonsIsTrue, numbOfSome)
                            if (firstsynergyandconflictarray == True):
                                synergies_and_or_conflicts_array = np.copy(score_outras_array)
                                synergies_and_or_conflicts_array[synergies_and_or_conflicts_array>0.] = 2 #2 is code for synergies
                                synergies_and_or_conflicts_array = synergies_and_or_conflicts_array.astype(int)
                                firstsynergyandconflictarray = False
                            else: 
                                synergies_and_or_conflicts_array = updateSynergyAndConflictInCellKnowledge(score_outras_array, synergies_and_or_conflicts_array, spec_score)
                        elif ((spec_score < 0) and (scoretypeToCalculate == "positive")):
                            (score_outras_array, dictScoreMapPerMarineUse, dfScoreMapPerPairwise, dictpairwisescorerastername, listpairwisescorerastername) = scoresToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisescorerastername, calculationtype, scoreSumMarineUseMapTableIsTrue, dictScoreMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, scoreSumPairwiseMapTableIsTrue, dfScoreMapPerPairwise, "false", listpairwisescorerastername, somePolygonsIsTrue, numbOfSome)
                            if (firstsynergyandconflictarray == True):
                                synergies_and_or_conflicts_array = np.copy(score_outras_array)
                                synergies_and_or_conflicts_array[synergies_and_or_conflicts_array<0.] = 1 #1 is code for conflicts
                                synergies_and_or_conflicts_array = synergies_and_or_conflicts_array.astype(int)
                                firstsynergyandconflictarray = False
                            else: 
                                synergies_and_or_conflicts_array = updateSynergyAndConflictInCellKnowledge(score_outras_array, synergies_and_or_conflicts_array, spec_score)
                    # make basic raster for extent - part 3:
                    else:
                        if ((spec_score > 0) and (scoretypeToCalculate == "negative")):
                            (score_outras_array, dictScoreMapPerMarineUse, dfScoreMapPerPairwise, dictpairwisescorerastername, listpairwisescorerastername) = scoresToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisescorerastername, calculationtype, scoreSumMarineUseMapTableIsTrue, dictScoreMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, scoreSumPairwiseMapTableIsTrue, dfScoreMapPerPairwise, "false", listpairwisescorerastername, somePolygonsIsTrue, numbOfSome)
                            if (firstbasicarray == True): 
                                cells_with_score_array = np.copy(score_outras_array)                                    
                                cells_with_score_array[cells_with_score_array>0.] = 1 #1 is code for score
                                cells_with_score_array = cells_with_score_array.astype(int)
                                firstbasicarray = False
                            else: 
                                cells_with_score_array = updateScoreCellCount(score_outras_array, cells_with_score_array)
                        elif ((spec_score < 0) and (scoretypeToCalculate == "positive")):
                            (score_outras_array, dictScoreMapPerMarineUse, dfScoreMapPerPairwise, dictpairwisescorerastername, listpairwisescorerastername) = scoresToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisescorerastername, calculationtype, scoreSumMarineUseMapTableIsTrue, dictScoreMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, scoreSumPairwiseMapTableIsTrue, dfScoreMapPerPairwise, "false", listpairwisescorerastername, somePolygonsIsTrue, numbOfSome)
                            if (firstbasicarray == True): 
                                cells_with_score_array = np.copy(score_outras_array)                                    
                                cells_with_score_array[cells_with_score_array<0.] = 1 #1 is code for score
                                cells_with_score_array = cells_with_score_array.astype(int)
                                firstbasicarray = False
                            else: 
                                cells_with_score_array = updateScoreCellCount(score_outras_array, cells_with_score_array)                                    
            iterator2 += 1 #iterate through all rasters that are after raster1 (to iteratively be raster2)
        iterator1 += 1 #new raster1
        iterator2 = iterator1+1 #start again by iterating through rasters to be raster2 (now the number of following rasters has decreased by 1)
    # make total score raster with land area as NoData: 
    ocean_array_land = ocean_array == 0
    # make synergy-and-conflict area polygon - part 4:
    if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
        cells_with_no_output = synergies_and_or_conflicts_array == 0
    # make basic raster for extent - part 4:
    else: 
        cells_with_no_output = cells_with_score_array == 0
    np.place(cummulated_score_outras_array, ocean_array_land & cells_with_no_output, np.nan)   
    scoreRaster = arcpy.NumPyArrayToRaster(cummulated_score_outras_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    createNewPath(finalfoldername)
    output_tif_incl_folder = finalfoldername+"\\"+scoreraster_finaloutputname_only_ocean
    scoreRaster.save(output_tif_incl_folder)
    arcpy.DefineProjection_management(output_tif_incl_folder, spatial_ref)
    # table 1 inputs:
    if scoreSumMarineUseMatrixTableIsTrue == "true":
        getTotalMatrixSumCountPerMarineUse(dictScoreMatrixPerMarineUse, scoretypeToCalculate, finalfoldername, scoreSumMarineUseMatrixTable)       
    # table 2 inputs:
    if scoreSumMarineUseMapTableIsTrue == "true":
        getTotalMapSumCountAndAveragePerMarineUse(listOfLongMarineUseNames, dictScoreMapPerMarineUse, finalfoldername, scoretypeToCalculate, scoreSumMarineUseMapTable)
    # table 3 inputs:
    if scoreSumPairwiseMapTableIsTrue == "true":
        getTotalMapSumPerPairwiseCombination(finalfoldername, dfScoreMapPerPairwise, scoreSumPairwiseMapTable)        
    # if is chosen to only add polygons to map with highest and lowest scores:
    if ((scoreSumPairwiseMapTableIsTrue == "true") and (somePolygonsIsTrue == "true") and (numbOfSome != "all") and (numbOfSome != 0)):
        # add numbOfSome lowest negative pairwise score polygons:
        if (scoretypeToCalculate == "all") or (scoretypeToCalculate == "negative"):  
            dictpairwisescorerastername_conflictsfirst = OrderedDict(sorted(dictpairwisescorerastername.items()))
            (listpairwisescorepolygon, listpairwisescorepolygonname) = getNumbOfSomePolygonElementsFromOrderedDict(dictpairwisescorerastername_conflictsfirst, numbOfSome, listpairwisescorepolygon, listpairwisescorepolygonname, pairwise_output_folder)        
        # add numbOfSome highest positive pairwise score polygons:
        if (scoretypeToCalculate == "all") or (scoretypeToCalculate == "positive"):
            dictpairwisescorerastername_synergiesfirst = OrderedDict(sorted(dictpairwisescorerastername.items(), reverse=True))
            (listpairwisescorepolygon, listpairwisescorepolygonname) = getNumbOfSomePolygonElementsFromOrderedDict(dictpairwisescorerastername_synergiesfirst, numbOfSome, listpairwisescorepolygon, listpairwisescorepolygonname, pairwise_output_folder)
    elif (numbOfSome != 0): 
        (listpairwisescorepolygon, listpairwisescorepolygonname) = getNumbOfAllPolygonElementsFromOrderedList(listpairwisescorerastername, listpairwisescorepolygon, listpairwisescorepolygonname, pairwise_output_folder)
    if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
        return (output_tif_incl_folder, listpairwisescorepolygon, listpairwisescorepolygonname, synergies_and_or_conflicts_array)
    else:
        return (output_tif_incl_folder, listpairwisescorepolygon, listpairwisescorepolygonname, cells_with_score_array)
 
def createNewPath(outputpath):
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

def getDictionaryFromExcelTwoColumns(excelsheet, first_column_name):
    df = pd.read_excel(excelsheet)
    df.set_index(first_column_name)
    dictdraft = df.to_dict('split')
    dictdraft['data']  
    listfromdict = dictdraft['data']
    dictfinal = OrderedDict()
    for pair in listfromdict:
        dictfinal[pair[0]] = pair[1]
    return dictfinal

def getNumbOfAllPolygonElementsFromOrderedList(listpairwisescorerastername, listpairwisescorepolygon, listpairwisescorepolygonname, pairwise_output_folder):
    for i in range(len(listpairwisescorerastername)):
        if i%3 == 0:
            (listpairwisescorepolygon, listpairwisescorepolygonname) = pairwiseScoreRasterToPolygon(listpairwisescorerastername[i], listpairwisescorerastername[i+1], listpairwisescorerastername[i+2], pairwise_output_folder, listpairwisescorepolygon, listpairwisescorepolygonname)
    return (listpairwisescorepolygon, listpairwisescorepolygonname)

def getNumbOfSomePolygonElementsFromOrderedDict(dictpairwisescorerastername, numbOfSome, listpairwisescorepolygon, listpairwisescorepolygonname, pairwise_output_folder):
    dictiterator=0
    for sum_of_all_scores, raster_element_list in dictpairwisescorerastername.items():
        if dictiterator >= numbOfSome: 
            break
        for i in range(len(raster_element_list)/3):
            if i%3 == 0: 
                (listpairwisescorepolygon, listpairwisescorepolygonname) = pairwiseScoreRasterToPolygon(raster_element_list[i], raster_element_list[i+1], raster_element_list[i+2], pairwise_output_folder, listpairwisescorepolygon, listpairwisescorepolygonname)
                dictiterator+=1      
    return (listpairwisescorepolygon, listpairwisescorepolygonname)

# table 2 inputs:
def getTotalMapSumCountAndAveragePerMarineUse(listOfLongMarineUseNames, dictScoreMapPerMarineUse, finalfoldername, scoretypeToCalculate, scoreSumMarineUseMapTable):
    # average per score cell:
    for longname in listOfLongMarineUseNames:
        # calculate average score per pairwise overlap in map  
        if dictScoreMapPerMarineUse[longname][1] != 0.:
            dictScoreMapPerMarineUse[longname][2] = float(dictScoreMapPerMarineUse[longname][0])/float(dictScoreMapPerMarineUse[longname][1])
        else: 
            dictScoreMapPerMarineUse[longname][2] = 0
        # get sum of boolean array to get contributing cells  
        dictScoreMapPerMarineUse[longname][3] = np.sum(dictScoreMapPerMarineUse[longname][3])
        # calculate average score per contributing raster cell 
        if dictScoreMapPerMarineUse[longname][3] == 0.:
            dictScoreMapPerMarineUse[longname][4] = 0
        else: 
            dictScoreMapPerMarineUse[longname][4] = float(dictScoreMapPerMarineUse[longname][0])/float(dictScoreMapPerMarineUse[longname][3])
        # calculate percent score contribution area
        if dictScoreMapPerMarineUse[longname][5] == 0.:
            dictScoreMapPerMarineUse[longname][6] = 0
        else: 
            dictScoreMapPerMarineUse[longname][6] = float(dictScoreMapPerMarineUse[longname][3])/float(dictScoreMapPerMarineUse[longname][5])*100
    df = pd.DataFrame.from_dict(dictScoreMapPerMarineUse, orient='index')
    columnF = "Count of individual marine use raster cells for each marine use"
    if (scoretypeToCalculate == "all"): 
        columnA = "Total score in map for each marine use"
        columnB = "Total count of spatial pairwise conflict-synergy combinations in map for each marine use"
        columnC = "Average score per pairwise conflict-synergy combination in map for each marine use"
        columnD = "Total count of raster cells that each marine use contribute conflict-synergy scores to in map"
        columnE = "Average score per raster cell that each marine use contribute conflict-synergy scores to in map"
        columnG = "Percent area with conflict-synergy scores out of the area for each marine use"      
    elif (scoretypeToCalculate == "positive"): 
        columnA = "Total positive score in map for each marine use"
        columnB = "Total count of spatial positive pairwise conflict-synergy combinations in map for each marine use"
        columnC = "Average score per positive pairwise conflict-synergy combination in map for each marine use"
        columnD = "Total count of raster cells that each marine use contribute synergy scores to in map"
        columnE = "Average score per raster cell that each marine use contribute synergy scores to in map"
        columnG = "Percent area with synergy scores out of the area for each marine use"      
    elif (scoretypeToCalculate == "negative"): 
        columnA = "Total negative score in map for each marine use"
        columnB = "Total count of spatial negative pairwise conflict-synergy combinations in map for each marine use"
        columnC = "Average score per negative pairwise conflict-synergy combination in map for each marine use"
        columnD = "Total count of raster cells that each marine use contribute conflict scores to in map"
        columnE = "Average score per raster cell that each marine use contribute conflict scores to in map"
        columnG = "Percent area with conflict scores out of the area for each marine use"      
    df.columns = [columnA, columnB, columnC, columnD, columnE, columnF, columnG]  
    if (scoretypeToCalculate == "all") or (scoretypeToCalculate == "positive"):
        df = df.sort_values(by=[columnA], ascending=False)
    elif (scoretypeToCalculate == "negative"):
        df = df.sort_values(by=[columnA], ascending=True)
    createNewPath(os.path.join(os.path.dirname(__file__),finalfoldername))
    df.to_excel(os.path.join(os.path.dirname(__file__),finalfoldername,scoreSumMarineUseMapTable))  

# table 3 inputs:
def getTotalMapSumPerPairwiseCombination(finalfoldername, dfScoreMapPerPairwise, scoreSumPairwiseMapTable):
    createNewPath(os.path.join(os.path.dirname(__file__),finalfoldername))
    dfScoreMapPerPairwise.to_excel(os.path.join(os.path.dirname(__file__),finalfoldername,scoreSumPairwiseMapTable), index=False)  

# table 1 inputs:
def getTotalMatrixSumCountPerMarineUse(dictScoreMatrixPerMarineUse, scoretypeToCalculate, finalfoldername, scoreSumMarineUseMatrixTable):
    dfScoreMatrixPerMarineUse = pd.DataFrame.from_dict(dictScoreMatrixPerMarineUse, orient='index')  
    if (scoretypeToCalculate == "all"):
        columnA = "Sum of inputted synergy scores"
        columnB = "Count of inputted synergy scores"
        columnC = "Sum of inputted conflict scores"
        columnD = "Count of inputted conflict scores"
        dfScoreMatrixPerMarineUse.columns = [columnA, columnB, columnC, columnD] 
    elif (scoretypeToCalculate == "positive"):
        columnA = "Sum of inputted synergy scores"
        columnB = "Count of inputted synergy scores"
        dfScoreMatrixPerMarineUse.columns = [columnA, columnB] 
    elif (scoretypeToCalculate == "negative"):
        columnA = "Sum of inputted conflict scores"
        columnB = "Count of inputted conflict scores"
        dfScoreMatrixPerMarineUse.columns = [columnA, columnB] 
    if (scoretypeToCalculate == "all") or (scoretypeToCalculate == "positive"):
        dfScoreMatrixPerMarineUse = dfScoreMatrixPerMarineUse.sort_values(by=[columnA], ascending=False)
    elif scoretypeToCalculate == "negative":
        dfScoreMatrixPerMarineUse = dfScoreMatrixPerMarineUse.sort_values(by=[columnA], ascending=True)
    createNewPath(os.path.join(os.path.dirname(__file__),finalfoldername))
    dfScoreMatrixPerMarineUse.to_excel(os.path.join(os.path.dirname(__file__),finalfoldername,scoreSumMarineUseMatrixTable))

def pairwiseScoreRasterToPolygon(rastername, score, matrixinput, pairwise_output_folder, listpairwisescorepolygon, listpairwisescorepolygonname):
    createNewPath(pairwise_output_folder)
    marineuseoutput_shp_excl_folder = rastername[:-4]+".shp"
    marineuseoutput_shp_incl_folder = pairwise_output_folder+"\\"+marineuseoutput_shp_excl_folder
    arcpy.RasterToPolygon_conversion(arcpy.sa.Raster(pairwise_output_folder+"\\"+rastername), marineuseoutput_shp_incl_folder, "NO_SIMPLIFY","VALUE","MULTIPLE_OUTER_PART")             
    addField1(marineuseoutput_shp_incl_folder, "TEXT", fieldname = "finalvalue", precision = "", decimals = "", field_length = 20)
    calculateField1(marineuseoutput_shp_incl_folder, "finalvalue", str(score), expression_type="PYTHON")
    if type(matrixinput) == float: 
        matrixinput=''
    elif len(matrixinput)%254 == 0: 
        numberroundsneeded = ((len(matrixinput)/254)+1)
    else: 
        numberroundsneeded = ((len(matrixinput)/254)+2)
    matrixstart=0
    matrixend=254
    if len(matrixinput) > 0: 
        for fieldcount in range(1,numberroundsneeded):
            addField1(marineuseoutput_shp_incl_folder, "TEXT", "full_desc"+str(fieldcount), precision = "", decimals = "", field_length = 254)
            calculateField1(marineuseoutput_shp_incl_folder, "full_desc"+str(fieldcount), "'"+matrixinput[matrixstart:matrixend]+"'", expression_type="PYTHON")
            matrixstart=matrixstart+254
            matrixend=matrixend+254
            if matrixend > len(matrixinput):
                matrixend = len(matrixinput)
    arcpy.DeleteField_management(marineuseoutput_shp_incl_folder, "Id")
    listpairwisescorepolygon.append(marineuseoutput_shp_incl_folder)
    listpairwisescorepolygonname.append(marineuseoutput_shp_excl_folder)
    return (listpairwisescorepolygon, listpairwisescorepolygonname)

def pairwiseScoreRasterToSave(array_input, lower_left_corner, dsc, spatial_ref, pairwise_output_folder, inputrastername1, inputrastername2, calculationtype, score, matrixinput, dictpairwisescorerastername, sum_of_all_cells, listpairwisescorerastername, scoreSumPairwiseMapTableIsTrue, somePolygonsIsTrue, numbOfSome):
    if (numbOfSome != 0): 
        pairwise_marine_use_array = np.copy(array_input)
        pairwise_marine_use_array = pairwise_marine_use_array.astype(int)
        pairwise_marine_use_array[pairwise_marine_use_array!=0.] = 1.
        pairwiseScoreRaster = arcpy.NumPyArrayToRaster(pairwise_marine_use_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight, 0)
        raster_outputname = returnRasterFilename(inputrastername1, inputrastername2, calculationtype)
        createNewPath(pairwise_output_folder)
        pairwiseScoreRaster.save(pairwise_output_folder+"\\"+raster_outputname)
        arcpy.DefineProjection_management(pairwise_output_folder+"\\"+raster_outputname, spatial_ref)
        # if it is chosen to only add polygons to map with highest and lowest scores:
        if ((scoreSumPairwiseMapTableIsTrue == "true") and (somePolygonsIsTrue == "true") and (numbOfSome != "all")):
            if sum_of_all_cells in dictpairwisescorerastername: 
                dictpairwisescorerastername[sum_of_all_cells].append(raster_outputname)
                dictpairwisescorerastername[sum_of_all_cells].append(score)
                dictpairwisescorerastername[sum_of_all_cells].append(matrixinput)
            else: 
                dictpairwisescorerastername[sum_of_all_cells] = [raster_outputname, score, matrixinput]
        # if it is chosen to add all polygons to map:
        else:
            listpairwisescorerastername.append(raster_outputname)
            listpairwisescorerastername.append(score)
            listpairwisescorerastername.append(matrixinput)
    return (dictpairwisescorerastername, listpairwisescorerastername)    

def populateCurrentMapDocument(outputrastername_tif_incl_folder, outputrastername_tif_excl_folder, listpairwisescorepolygon, listpairwisescorepolygonname, output_shp_incl_folder, output_shp_excl_folder, score_lyrfile, pairwise_lyrfile, conflict_and_synergy_lyrfile, final_folder, pairwise_output_folder, includeSynergyAndConflictAtOnceAreaIsTrue):
    try: 
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        addLayerToMxd(mxd, df, outputrastername_tif_incl_folder, outputrastername_tif_excl_folder, score_lyrfile, 'TOP', "mainmap", final_folder)
        if includeSynergyAndConflictAtOnceAreaIsTrue == "true":        
            addLayerToMxd(mxd, df, output_shp_incl_folder, output_shp_excl_folder, conflict_and_synergy_lyrfile, 'BOTTOM', "both_synergies_and_conflicts", final_folder)            
        for pairwisescorepolygon, pairwisescorepolygonname in zip(listpairwisescorepolygon, listpairwisescorepolygonname):
            addLayerToMxd(mxd, df, pairwisescorepolygon, pairwisescorepolygonname, pairwise_lyrfile, 'BOTTOM', "pairwise_polygon", pairwise_output_folder) #raster parameter does not matter when not mainmap
    except: 
        arcpy.AddMessage("ERROR: You cannot have opened more than one MXD document in the same session for this tool to work")

def printTime(starttime, starttimetobeupdated):
    overallminutes = int(time.time()-starttime)/60
    overallseconds = int((((time.time()-starttime)/60)-(int(time.time()-starttime)/60))*60)
    procminutes = int(time.time()-starttimetobeupdated)/60
    procseconds = int((((time.time()-starttimetobeupdated)/60)-(int(time.time()-starttimetobeupdated)/60))*60) 
    dateTimeObj = datetime.now()
    timestamp = str(dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)
    printline = "with processing time {}min {}sec, out of cumulated passed {}min {}sec, timestamp:{} \n".format(procminutes,procseconds,overallminutes,overallseconds,timestamp)
    starttimetobeupdated = time.time()
    return (printline, starttimetobeupdated) 

def resetTime(starttimetobeupdated):
    starttimetobeupdated = time.time()
    dateTimeObj = datetime.now()
    timestamp = str(dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)
    print("starting process, timestamp:{}".format(timestamp))
    return (starttimetobeupdated) 

def returnRasterFilename(inputrastername1, inputrastername2, calculationtype):
    if len(inputrastername1[:-4]) >= 7 and len(inputrastername2[:-4]) >= 7:  
        finalrastername = calculationtype+inputrastername1[:-4][:7]+"_"+inputrastername2[:-4][:7]+".tif"   
    elif len(inputrastername1) >= 7: 
        finalrastername = calculationtype+inputrastername1[:-4][:7]+"_"+inputrastername2[:-4]+".tif"   
    elif len(inputrastername2) >= 7: 
        finalrastername = calculationtype+inputrastername1[:-4]+"_"+inputrastername2[:-4][:7]+".tif"   
    else: 
        finalrastername = calculationtype+inputrastername1[:-4]+"_"+inputrastername2[:-4]+".tif"    
    return finalrastername                       

def scoresToRasters(inputfoldername, inputrastername1, inputrastername2, score, lower_left_corner, dsc, matrixinput, pairwise_output_folder, dictpairwisescorerastername, calculationtype, scoreSumMarineUseMapTableIsTrue, dictScoreMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, scoreSumPairwiseMapTableIsTrue, dfScoreMapPerPairwise, getStatisticsAndPolygons, listpairwisescorerastername, somePolygonsIsTrue, numbOfSome):
    # create pairwise marine use score raster
    inputname1 = inputfoldername+"\\"+inputrastername1
    array_input1 = arcpy.RasterToNumPyArray(inputname1)
    array_input1 = array_input1.astype(float)
    inputname2 = inputfoldername+"\\"+inputrastername2
    array_input2 = arcpy.RasterToNumPyArray(inputname2)
    array_input2 = array_input2.astype(float)
    ifOverlaps = array_input1+array_input2==2.   
    # table 2 inputs:
    if ((scoreSumMarineUseMapTableIsTrue == "true") and (getStatisticsAndPolygons == "true")):
        dictScoreMapPerMarineUse[inputmarineuselongname1][5]=np.count_nonzero(array_input1)
        dictScoreMapPerMarineUse[inputmarineuselongname2][5]=np.count_nonzero(array_input2)
        dictScoreMapPerMarineUse[inputmarineuselongname1][3] += ifOverlaps
        dictScoreMapPerMarineUse[inputmarineuselongname2][3] += ifOverlaps
    array_input1[array_input1+array_input2!=2.] = 0.    
    array_input1[ifOverlaps] = score
    # table 2 inputs:
    if ((scoreSumMarineUseMapTableIsTrue == "true") and (getStatisticsAndPolygons == "true")):
        # sum of score cells: 
        dictScoreMapPerMarineUse[inputmarineuselongname1][0]+= np.sum(array_input1)
        dictScoreMapPerMarineUse[inputmarineuselongname2][0]+= np.sum(array_input1)
        # count of score cells:
        dictScoreMapPerMarineUse[inputmarineuselongname1][1]+= np.count_nonzero(array_input1)
        dictScoreMapPerMarineUse[inputmarineuselongname2][1]+= np.count_nonzero(array_input1)
    # table 3 inputs:
    if ((scoreSumPairwiseMapTableIsTrue == "true") and (getStatisticsAndPolygons == "true")):
        (dfScoreMapPerPairwise.loc[dfScoreMapPerPairwise['Idcolumn'] == inputmarineuselongname2, inputmarineuselongname1]) = np.sum(array_input1)   
    # create pairwise marine use polygon:
    if ((len(np.unique(array_input1)) > 1) and (getStatisticsAndPolygons == "true") and (numbOfSome != 0)): # if there is more than one value in the array (meaning more values than just zero) 
        (dictpairwisescorerastername, listpairwisescorerastername) = pairwiseScoreRasterToSave(array_input1, lower_left_corner, dsc, spatial_ref, pairwise_output_folder, inputrastername1, inputrastername2, calculationtype, score, matrixinput, dictpairwisescorerastername, np.sum(array_input1), listpairwisescorerastername, scoreSumPairwiseMapTableIsTrue, somePolygonsIsTrue, numbOfSome)
    return (array_input1, dictScoreMapPerMarineUse, dfScoreMapPerPairwise, dictpairwisescorerastername, listpairwisescorerastername)

def synergyAndConflictAtOnceRasterToPolygon(synergies_and_or_conflicts_array, lower_left_corner, dsc, spatial_ref, final_folder, conflict_and_synergy_shapefile):
    synergies_and_or_conflicts_array[synergies_and_or_conflicts_array!=3]=0 
    synergies_and_or_conflicts_array[synergies_and_or_conflicts_array==3]=1 #3 is code for synergies-and-conflicts-at-once
    if np.sum(synergies_and_or_conflicts_array) > 0: 
        synergiesAndConflictsAtOnceRaster = arcpy.NumPyArrayToRaster(synergies_and_or_conflicts_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
        createNewPath(final_folder)
        output_shp_draft_incl_folder = final_folder+"\\"+conflict_and_synergy_shapefile[:-4]+"_draft.shp"
        output_shp_draft_excl_folder = conflict_and_synergy_shapefile[:-4]+"_draft.shp"
        output_shp_incl_folder = final_folder+"\\"+conflict_and_synergy_shapefile
        output_shp_excl_folder = conflict_and_synergy_shapefile
        arcpy.RasterToPolygon_conversion(synergiesAndConflictsAtOnceRaster, output_shp_draft_incl_folder, "NO_SIMPLIFY","VALUE","MULTIPLE_OUTER_PART")             
        arcpy.MakeFeatureLayer_management(output_shp_draft_incl_folder, output_shp_draft_excl_folder[:-4], '"gridcode" = 1')
        arcpy.CopyFeatures_management(output_shp_draft_excl_folder[:-4], output_shp_incl_folder)
        arcpy.DefineProjection_management(output_shp_incl_folder, spatial_ref)
        addField1(output_shp_incl_folder, "TEXT", fieldname = "finalvalue", precision = "", decimals = "", field_length = 20)
        calculateField1(output_shp_incl_folder, "finalvalue", str(1), expression_type="PYTHON")
        arcpy.DeleteField_management(output_shp_incl_folder, "Id")
        return (output_shp_incl_folder, output_shp_excl_folder)
    else: 
        return ("no_output", "no_output")

def updateScoreCellCount(score_outras_array, basic_array):
    positive_to_update = score_outras_array > 0    
    np.place(basic_array, positive_to_update, 1) #1 is code for score
    negative_to_update = score_outras_array < 0    
    np.place(basic_array, negative_to_update, 1) #1 is code for score
    return basic_array

def updateSynergyAndConflictInCellKnowledge(score_outras_array, synergies_and_or_conflicts_array, spec_score):
    array_can_be_updated = synergies_and_or_conflicts_array == 0 # where array has no values 
    if spec_score > 0:
        synergies_specific_instance_array = score_outras_array > 0    
        np.place(synergies_and_or_conflicts_array, synergies_specific_instance_array & array_can_be_updated, 2) #2 is code for synergies
        conflicts_array = synergies_and_or_conflicts_array == 1 #1 is code for conflicts
        np.place(synergies_and_or_conflicts_array, synergies_specific_instance_array & conflicts_array, 3) #3 is code for both conflicts and synergies
    if spec_score < 0:
        conflicts_specific_instance_array = score_outras_array < 0
        np.place(synergies_and_or_conflicts_array, conflicts_specific_instance_array & array_can_be_updated, 1) #1 is code for conflicts    
        synergies_array = synergies_and_or_conflicts_array == 2 #2 is code for synergies
        np.place(synergies_and_or_conflicts_array, conflicts_specific_instance_array & synergies_array, 3) #3 is code for both conflicts and synergies
    return synergies_and_or_conflicts_array
    

# start timing: 
starttime = time.time()
starttimetobeupdated = starttime


# parameters: 
#paramter0 = folder_with_rasterinputs
inputfolder = arcpy.GetParameterAsText(0)

#parameter1 = marine_uses_linked_to_rasternames excelsheet
marine_uses_linked_to_rasternames_excel = arcpy.GetParameterAsText(1)
dictMarineUses = getDictionaryFromExcelTwoColumns(marine_uses_linked_to_rasternames_excel, 'full_marine_use_category_name')

#parameter2 = matrix excelsheet
inputexcelsheet = arcpy.GetParameterAsText(2)

#parameter3 = pos, neg, all strings
scoretypeToCalculate = arcpy.GetParameterAsText(3)

#parameter4 = scoreraster_finaloutputname_only_ocean
scoreraster_finaloutputname_only_ocean = arcpy.GetParameterAsText(4)

#parameter5 = oceanrastername_with_path
oceanrastername_with_path = arcpy.GetParameterAsText(5)

#parameter6 = score_lyrfile
try: 
    score_lyrfile = arcpy.GetParameterAsText(6)
    if score_lyrfile == "": 
        score_lyrfile = "NotExisting"
except: 
    score_lyrfile = "NotExisting"

#parameter7 = pairwise_lyrfile
try: 
    pairwise_lyrfile = arcpy.GetParameterAsText(7)
    if pairwise_lyrfile == "": 
        pairwise_lyrfile = "NotExisting"
except: 
    pairwise_lyrfile = "NotExisting"

#parameter8 = score sum per marine use based on matrix (checked or unchecked) 
scoreSumMarineUseMatrixTableIsTrue = arcpy.GetParameterAsText(8) 

#parameter9 = score sum per marine use based on map (checked or unchecked) 
scoreSumMarineUseMapTableIsTrue = arcpy.GetParameterAsText(9) 

#parameter10 = score sum per pairwise combination based on map (checked or unchecked)  
scoreSumPairwiseMapTableIsTrue = arcpy.GetParameterAsText(10) 

#parameter11 = only highest and/or lowest pairwise combinations (checked or unchecked)
try: 
    somePolygonsIsTrue = arcpy.GetParameterAsText(11)
    if somePolygonsIsTrue == "": 
        somePolygonsIsTrue = "false"
except: 
    somePolygonsIsTrue = "false"

#parameter12 = the max number of pos and/or neg pairwise marine use polygons to include
try: 
    numbOfSome = int(arcpy.GetParameterAsText(12))
    if numbOfSome == "": 
        numbOfSome = "all"
    elif ((numbOfSome == 0) and (somePolygonsIsTrue == "false")): 
        numbOfSome = "all"
except: 
    numbOfSome = "all" #parameter is irrelevant if not activated 

#parameter13 = only pairwise combinations that include a specific marine use (checked or unchecked)
try: 
    onlyOneMarineUseInFocusIsTrue = arcpy.GetParameterAsText(13)
    if onlyOneMarineUseInFocusIsTrue == "": 
        onlyOneMarineUseInFocusIsTrue = "false"
except: 
    onlyOneMarineUseInFocusIsTrue = "false"

#parameter14 = the marine use to focus on
try:
    marineUseInFocus = arcpy.GetParameterAsText(14)
    if marineUseInFocus == "": 
        marineUseInFocus = "false"
except: 
    marineUseInFocus = "false"

#parameter15 = include synergy-and-conflict area (checked or unchecked)
try: 
    includeSynergyAndConflictAtOnceAreaIsTrue = arcpy.GetParameterAsText(15)
    if includeSynergyAndConflictAtOnceAreaIsTrue == "": 
        includeSynergyAndConflictAtOnceAreaIsTrue = "false"
except: 
    includeSynergyAndConflictAtOnceAreaIsTrue = "false"

#extra script parameters: 
pairwise_output_folder = "pairwise_outputs"
final_folder = "final_results"
scoreSumMarineUseMatrixTable = "table1_"+scoretypeToCalculate+"_"+"total_score_per_marineuse_matrix.xlsx"
scoreSumMarineUseMapTable = "table2_"+scoretypeToCalculate+"_"+"total_score_per_marineuse_map.xlsx"
scoreSumPairwiseMapTable = "table3_"+scoretypeToCalculate+"_"+"total_score_per_pairwise_combination_map.xlsx"
conflict_and_synergy_shapefile = "conflict_and_synergy_at_once.shp"
conflict_and_synergy_lyrfile = "NotExisting"
calculationtype = "score_"


# environment:
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput=True
os.chdir(os.path.dirname(__file__))
rasterToSnapTo = arcpy.sa.Raster(oceanrastername_with_path)
dsc = arcpy.Describe(rasterToSnapTo)
spatial_ref = dsc.SpatialReference
spatial_extent = dsc.Extent
lower_left_corner = arcpy.Point(spatial_extent.XMin, spatial_extent.YMin)
arcpy.env.outCoordinateSystem = spatial_ref


# main code: 
arcpy.AddMessage("\n")
starttimetobeupdated = resetTime(starttimetobeupdated)
(output_tif_incl_folder, listpairwisescorepolygon, listpairwisescorepolygonname, synergies_and_or_conflicts_array) = calculatePairwiseAndTotalScoreRasters(dictMarineUses, inputexcelsheet, scoretypeToCalculate, inputfolder, pairwise_output_folder, final_folder, scoreSumMarineUseMatrixTableIsTrue, scoreSumMarineUseMatrixTable, scoreSumMarineUseMapTableIsTrue, scoreSumMarineUseMapTable, scoreSumPairwiseMapTableIsTrue, scoreSumPairwiseMapTable, somePolygonsIsTrue, numbOfSome, onlyOneMarineUseInFocusIsTrue, marineUseInFocus, includeSynergyAndConflictAtOnceAreaIsTrue, lower_left_corner, dsc, spatial_ref, scoreraster_finaloutputname_only_ocean, oceanrastername_with_path, calculationtype)
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Pairwise score rasters and total score raster have been calculated, {}\n".format(printline))

# make synergy-and-conflict area polygon - part 5:
if includeSynergyAndConflictAtOnceAreaIsTrue == "true":
    starttimetobeupdated = resetTime(starttimetobeupdated)
    (output_shp_incl_folder, output_shp_excl_folder) = synergyAndConflictAtOnceRasterToPolygon(synergies_and_or_conflicts_array, lower_left_corner, dsc, spatial_ref, final_folder, conflict_and_synergy_shapefile)
    (printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
    arcpy.AddMessage("Synergy-and-conflict-at-once-raster has been calculated, {}\n".format(printline))
else: 
    output_shp_incl_folder = "false"
    output_shp_excl_folder = "false"

starttimetobeupdated = resetTime(starttimetobeupdated)
populateCurrentMapDocument(output_tif_incl_folder, scoreraster_finaloutputname_only_ocean, listpairwisescorepolygon, listpairwisescorepolygonname, output_shp_incl_folder, output_shp_excl_folder, score_lyrfile, pairwise_lyrfile, conflict_and_synergy_lyrfile, final_folder, pairwise_output_folder, includeSynergyAndConflictAtOnceAreaIsTrue)
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("If data exist, it has been added to current MXD document, {}\n".format(printline))
