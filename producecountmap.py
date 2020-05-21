# Purpose of script: 
#Script input to the tool called 'Calculate Count Map'. 
#It outputs the number of pairwise combinations per cell.

#The output can either be for:
## all overlaps of marine uses 
## all overlaps of marine uses where a specific inputted marine use is included
## all overlaps of marine uses with a conflict-synergy input (it can be further specified whether the inputs should consist of positive scores, negative scores, or all scores)
## all overlaps of marine uses with a conflict-synergy input where a specific inputted marine use is included 
## all overlaps of marine uses with a specific conflict-synergy category
## all overlaps of mobile marine uses with a conflict-synergy input
## all overlaps of marine uses with a conflict-synergy input and with different vertical scales 
## all overlaps of marine uses with a conflict-synergy input and with overlapping vertical scales 
## all overlaps of marine uses with a conflict-synergy that could potentially be included in a multi-use constellation

# It is voluntary to include a polygon for the area that both contain conflicts and synergies. This options is only enabled if a pairwise map-based statistics table is chosen to be outputted. 

# It is voluntary to only include a specific number of polygons of the highest count pairwise combinations. 

# It is voluntary to include 1-3 statistics tables that will be outputted in the result folder.   

# The output is cut after an inputted ocean raster dataset. 


# DATE OF CREATION: 28-10-2019
# AUTHOR: Ida Maria Bonnevie

#All the Python modules in the import statement needs to be installed. 
#An ESRI ArcMap license with Spatial Analyst extension activated is required for the tool to run as a script tool in ArcMap. 


# Toolvalidator script inputted in tool: 
#import arcpy
#import pandas as pd
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
#        if (self.params[13].value == "count all combinations with a specific marine use") or (self.params[13].value == "count combinations with a specific marine use where synergy-conflict inputs exist"):
#            self.params[15].enabled = True
#            self.params[14].enabled = False
#            self.params[16].enabled = False
#            excelfile_with_path = (self.params[1].value.value).replace("\a","\\a").replace("\b","\\b")
#            df = pd.read_excel(excelfile_with_path)
#            list_options = list(df['full_marine_use_category_name'])
#            self.params[15].filter.list = list_options
#        else:
#            self.params[15].enabled = False
#        if self.params[13].value == "count combinations for a specific conflict-synergy category":
#            self.params[14].enabled = True ## the category options should be added to the tool 
#            self.params[15].enabled = False
#            self.params[16].enabled = False
#        else:
#            self.params[14].enabled = False
#        if (self.params[13].value == "count vertically different overlaps") or (self.params[13].value == "count vertically same overlaps") or (self.params[13].value == "count pairwise overlaps where both marine uses are mobile"):
#            self.params[16].enabled = True ## the category options should be added to the tool 
#            self.params[14].enabled = False
#            self.params[15].enabled = False
#        else:
#            self.params[16].enabled = False
#        if self.params[3].altered:
#    	    if (self.params[3].value == "all"):
#                list_options2 = []
#                list_options2.append("count all")
#                list_options2.append("count combinations where synergy-conflict inputs exist")
#                list_options2.append("count combinations for a specific conflict-synergy category")
#                list_options2.append("count all combinations with a specific marine use")
#                list_options2.append("count combinations with a specific marine use where synergy-conflict inputs exist")
#                list_options2.append("count multiuse-options mentioned in the MUSES project")
#                list_options2.append("count vertically different overlaps")
#                list_options2.append("count vertically same overlaps")
#                list_options2.append("count pairwise overlaps where both marine uses are mobile")
#                self.params[13].filter.list = list_options2
#            elif (self.params[3].value == "positive") or (self.params[3].value == "negative"):
#                list_options2 = []
#                list_options2.append("count combinations where synergy-conflict inputs exist")
#                list_options2.append("count combinations for a specific conflict-synergy category")
#                list_options2.append("count combinations with a specific marine use where synergy-conflict inputs exist")
#                list_options2.append("count multiuse-options mentioned in the MUSES project")
#                list_options2.append("count vertically different overlaps")
#                list_options2.append("count vertically same overlaps")
#                list_options2.append("count pairwise overlaps where both marine uses are mobile")
#                self.params[13].filter.list = list_options2
#                if self.params[13].value not in list_options2:
#                    self.params[13].value = "count combinations where synergy-conflict inputs exist"
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
def addCountToDictPerMarineUseInMatrix(columnnumb, column, dictCountMatrixPerMarineUse, spec_score_or_count, listOfLongMarineUseNames, iterator2):    
    dictCountMatrixPerMarineUse[column][columnnumb] = dictCountMatrixPerMarineUse[column][columnnumb]+spec_score_or_count # add to marine use pairwise input 1                   
    dictCountMatrixPerMarineUse[listOfLongMarineUseNames[iterator2]][columnnumb] = dictCountMatrixPerMarineUse[listOfLongMarineUseNames[iterator2]][columnnumb]+spec_score_or_count # add to marine use pairwise input 2

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

def calculateField1(outputpath, valuefield, valueToInput, expression_type="VB"): 
    arcpy.CalculateField_management(outputpath, valuefield, valueToInput, expression_type, "")

def calculatePairwiseAndTotalCountRasters(dictMarineUses, matrixexcelfile, scoretypeToCalculateCountFor, inputfoldernamewithpath, pairwise_output_folder, finalfoldername, countMarineUseMatrixTableIsTrue, countMarineUseMatrixTable, countMarineUseMapTableIsTrue, countMarineUseMapTable, countPairwiseMapTableIsTrue, countPairwiseMapTable, somePolygonsIsTrue, numbOfSome, countChoice, chosen_category, chosen_category_score, marineUseInFocus, attribute_excelsheet, includeSynergyAndConflictAtOnceAreaIsTrue, lower_left_corner, dsc, spatial_ref, countraster_finaloutputname_only_ocean, oceanrastername_with_path, calculationtype):
    # import ocean array: 
    ocean_array = arcpy.RasterToNumPyArray(oceanrastername_with_path)
    ocean_array = ocean_array.astype(float)
    # table 2 inputs:
    if countMarineUseMapTableIsTrue == "true": 
        ocean_cell_number = np.count_nonzero(ocean_array)
    # preset parameters: 
    dfdesc = pd.read_excel(matrixexcelfile)
    listOfLongMarineUseNames = dictMarineUses.keys()
    listpairwisecountrastername = []
    listpairwisecountpolygon = []
    listpairwisecountpolygonname = []
    dictpairwisecountrastername = {}
    dictCountMatrixPerMarineUse = {}
    dictCountMapPerMarineUse = {}
    dfCountMapPerPairwise = "false" # false as default but might change
    array_synergy_and_conflicts_at_once = "false" # false as default but might change
    for longname_marine_use in listOfLongMarineUseNames: 
        # table 1 inputs:
        if countMarineUseMatrixTableIsTrue == "true":
            if scoretypeToCalculateCountFor == "all":
                dictCountMatrixPerMarineUse[longname_marine_use] = [0]*3 
            elif scoretypeToCalculateCountFor == "positive":
                dictCountMatrixPerMarineUse[longname_marine_use] = [0] #*2+["DataNotCalculated"] 
            elif scoretypeToCalculateCountFor == "negative":
                dictCountMatrixPerMarineUse[longname_marine_use] = [0] #+["DataNotCalculated"]+[0] 
        # table 2 inputs:
        if countMarineUseMapTableIsTrue == "true": 
            dictCountMapPerMarineUse[longname_marine_use]=[0]*7 
            dictCountMapPerMarineUse[longname_marine_use][1] = ocean_cell_number
            dictCountMapPerMarineUse[longname_marine_use][5]=np.zeros_like(ocean_array, dtype=bool)
    # table 3 inputs:
    if countPairwiseMapTableIsTrue == "true":
        dfCountMapPerPairwise = pd.DataFrame(columns=listOfLongMarineUseNames,index=listOfLongMarineUseNames)
        dfCountMapPerPairwise.index.name = 'Idcolumn'
        dfCountMapPerPairwise = dfCountMapPerPairwise.reset_index()        
    firstcountraster = True
    firstsynergyandconflictarray = True 
    firstbasicarray = True 
    iterator1 = 0
    iterator2 = 1     
    # main code: create total counts: 
    for column in listOfLongMarineUseNames: 
        inputrastername1 = dictMarineUses.get(column) 
        while iterator2 in range((iterator1+1),len(listOfLongMarineUseNames)):            
            inputrastername2 = dictMarineUses.get(listOfLongMarineUseNames[iterator2]) #get raster2
            inputmarineuselongname1 = column
            inputmarineuselongname2 = listOfLongMarineUseNames[iterator2]
            # make pairwise count rasters: set score=0 if score is never needed and alldesc:
            if (scoretypeToCalculateCountFor == "all") and ((countChoice == "count all") or (countChoice == "count all combinations with a specific marine use")) and (countMarineUseMatrixTableIsTrue == "false") and (includeSynergyAndConflictAtOnceAreaIsTrue == "false"):
                spec_score = 0 
                # set alldesc = '' if no pairwise polygons should be created and added: 
                if ((somePolygonsIsTrue == "true") and (numbOfSome == 0)): 
                    alldesc = ''
                else: 
                    # set alldesc if pairwise polygons should be created and added:
                    try: 
                        alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongMarineUseNames[iterator2], column].values
                        alldesc = str(alldesc_nparray.item(0))
                    # set alldesc = '' if no description can be found: 
                    except: 
                        alldesc = 'nan'
            # make pairwise count rasters: set score if score is needed and addesc:
            else: 
                try: 
                    # set alldesc:
                    alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongMarineUseNames[iterator2], column].values
                    alldesc = alldesc_nparray.item(0)
                    # set score if it exists:
                    if (len(str(alldesc)) > 3):                         
                        if str(alldesc)[:1] == "-": 
                            spec_score = float(alldesc[:5].replace(",",".")) #get the score
                        else: 
                            spec_score = float(alldesc[:4].replace(",",".")) #get the score   
                    # if score do not exist, score is set to 0:
                    else: 
                        spec_score = 0
                # if alldesc and score do not exist, they are set to '' and 0 respectively:
                except: 
                    spec_score = 0
                    alldesc = 'nan'
            # make pairwise count rasters: get spatial and temporal attributes if that is needed for the count type:
            if ((countChoice == "count vertically different overlaps") or (countChoice == "count vertically same overlaps") or (countChoice == "count pairwise overlaps where both marine uses are mobile")):
                if attribute_excelsheet == "false": 
                    arcpy.AddMessage("ERROR: Excelfile with spatial and temporal attributes has not been inputted")
                    quit()
                else:
                    try: 
                        dfattributes = pd.read_excel(attribute_excelsheet)
                    except: 
                        arcpy.AddMessage("ERROR: Problems regarding reading excelfile with spatial and temporal attributes")
                        quit()
                raster1long = dictMarineUses.keys()[dictMarineUses.values().index(inputrastername1)]
                raster2long = dictMarineUses.keys()[dictMarineUses.values().index(inputrastername2)]
                if ((countChoice == "count vertically different overlaps") or (countChoice == "count vertically same overlaps")):
                    act1_vertical = ((dfattributes[dfattributes["Idcolumn"] == raster1long]['Vertical information']).to_string(index=False)) #gather vertical attribute of pairwise marine use 1
                    act2_vertical = ((dfattributes[dfattributes["Idcolumn"] == raster2long]['Vertical information']).to_string(index=False)) #gather vertical attribute of pairwise marine use 2
                    if (act1_vertical == "BENTHIC" or act2_vertical == "BENTHIC") and (act1_vertical == "SURFACE" or act2_vertical == "SURFACE"):
                        notActualOverlapping = "true"
                    elif (act1_vertical == "BENTHIC" and act2_vertical == "BENTHIC") or (act1_vertical == "BENTHIC" and act2_vertical == "WHOLE WATER COLUMN") or (act1_vertical == "WHOLE WATER COLUMN" and act2_vertical == "BENTHIC") or (act1_vertical == "SURFACE" and act2_vertical == "SURFACE") or (act1_vertical == "SURFACE" and act2_vertical == "WHOLE WATER COLUMN") or (act1_vertical == "WHOLE WATER COLUMN" and act2_vertical == "SURFACE"): 
                        notActualOverlapping = "false"
                    else: 
                        notActualOverlapping = "" 
                else: 
                    notActualOverlapping = "" 
                if (countChoice == "count pairwise overlaps where both marine uses are mobile"):
                    act1_temporal = ((dfattributes[dfattributes["Idcolumn"] == raster1long]['Temporal information']).to_string(index=False)) # gather temporal attribute of pairwise marine use 1
                    act2_temporal = ((dfattributes[dfattributes["Idcolumn"] == raster2long]['Temporal information']).to_string(index=False)) # gather temporal attribute of pairwise marine use 2                    
                    if (act1_temporal == "MOBILE" and act2_temporal == "MOBILE"):
                        bothTemporal = "true"
                    else: 
                        bothTemporal = "" 
                else: 
                    bothTemporal = "" 
            else: 
                notActualOverlapping = "" 
                bothTemporal = "" 
            # make pairwise count rasters for the chosen count type:
            if (scoretypeToCalculateCountFor == "all") or ((scoretypeToCalculateCountFor == "positive") and (spec_score > 0)) or ((scoretypeToCalculateCountFor == "negative") and (spec_score < 0)):                
                if (countChoice == "count all") or (
                    (countChoice == "count all combinations with a specific marine use") and ((marineUseInFocus == listOfLongMarineUseNames[iterator2]) or (marineUseInFocus == column))) or (
                    (countChoice == "count combinations with a specific marine use where synergy-conflict inputs exist") and ((spec_score > 0) or (spec_score < 0)) and ((marineUseInFocus == listOfLongMarineUseNames[iterator2]) or (marineUseInFocus == column))) or (
                    (countChoice == "count combinations where synergy-conflict inputs exist") and ((spec_score > 0) or (spec_score < 0))) or (
                    (countChoice == "count combinations for a specific conflict-synergy category") and ((spec_score > 0) or (spec_score < 0)) and (spec_score == float(chosen_category_score))) or (
                    (countChoice == "count multiuse-options mentioned in the MUSES project") and ('MUSES' in str(alldesc)) and ((spec_score > 0) or (spec_score < 0))) or (
                    (countChoice == "count vertically different overlaps") and (notActualOverlapping == "true") and ((spec_score > 0) or (spec_score < 0))) or (
                    (countChoice == "count vertically same overlaps") and (notActualOverlapping == "false") and ((spec_score > 0) or (spec_score < 0))) or (
                    (countChoice == "count pairwise overlaps where both marine uses are mobile") and (bothTemporal == "true") and ((spec_score > 0) or (spec_score < 0))):                
                    (outras_count_array, array_score_array, dictCountMapPerMarineUse, dfCountMapPerPairwise, dictpairwisecountrastername, listpairwisecountrastername) = countsToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisecountrastername, calculationtype, countMarineUseMapTableIsTrue, dictCountMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, countPairwiseMapTableIsTrue, dfCountMapPerPairwise, "true", listpairwisecountrastername, somePolygonsIsTrue, numbOfSome, includeSynergyAndConflictAtOnceAreaIsTrue)
                    if firstcountraster == True:         
                        # make synergy-and-conflict-at-once area polygon - part 1:
                        if (includeSynergyAndConflictAtOnceAreaIsTrue == "true") and (firstsynergyandconflictarray == True):
                            array_synergy_and_conflicts_at_once = np.copy(array_score_array)
                            array_synergy_and_conflicts_at_once[array_synergy_and_conflicts_at_once>0] = 2 #2 is code for synergies
                            array_synergy_and_conflicts_at_once[array_synergy_and_conflicts_at_once<0] = 1 #1 is code for conflicts
                            array_synergy_and_conflicts_at_once = array_synergy_and_conflicts_at_once.astype(int)
                            firstsynergyandconflictarray = False
                        # make basic raster for extent - part 1: 
                        elif (firstbasicarray == True):
                            cells_with_score_array = np.copy(array_score_array)                                    
                            cells_with_score_array[cells_with_score_array>0.] = 1 #1 is code for score
                            cells_with_score_array[cells_with_score_array<0.] = 1 #1 is code for score
                            cells_with_score_array = cells_with_score_array.astype(int)
                            firstbasicarray = False
                        # make cummulated count rasters for the chosen count type:
                        cummulated_count_outras_array = np.copy(outras_count_array)
                        firstcountraster = False
                    else: 
                        # make synergy-and-conflict-at-once area polygon - part 2:
                        if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
                            array_synergy_and_conflicts_at_once = updateSynergyAndConflictInCellKnowledge(array_score_array, array_synergy_and_conflicts_at_once, spec_score)                                    
                        # make basic raster for extent - part 2: 
                        else: 
                            cells_with_score_array = updateScoreCellCount(array_score_array, cells_with_score_array)
                        # make cummulated count rasters for the chosen count type:
                        cummulated_count_outras_array += outras_count_array
                # table 1 inputs:
                if (countMarineUseMatrixTableIsTrue == "true"):
                    addCountToDictPerMarineUseInMatrix(0, column, dictCountMatrixPerMarineUse, 1, listOfLongMarineUseNames, iterator2)
                    if (scoretypeToCalculateCountFor == "all") and (spec_score > 0):
                        addCountToDictPerMarineUseInMatrix(1, column, dictCountMatrixPerMarineUse, 1, listOfLongMarineUseNames, iterator2)
                    elif (scoretypeToCalculateCountFor == "all") and (spec_score < 0):
                        addCountToDictPerMarineUseInMatrix(2, column, dictCountMatrixPerMarineUse, 1, listOfLongMarineUseNames, iterator2)
            # make synergy-and-conflict-at-once area polygon - part 3: 
            if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
                if ((spec_score > 0) and (scoretypeToCalculateCountFor == "negative")):
                    (outras_count_array, array_score_array, dictCountMapPerMarineUse, dfCountMapPerPairwise, dictpairwisecountrastername, listpairwisecountrastername) = countsToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisecountrastername, calculationtype, countMarineUseMapTableIsTrue, dictCountMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, countPairwiseMapTableIsTrue, dfCountMapPerPairwise, "false", listpairwisecountrastername, somePolygonsIsTrue, numbOfSome, includeSynergyAndConflictAtOnceAreaIsTrue)
                    if (firstsynergyandconflictarray == True):
                        array_synergy_and_conflicts_at_once = np.copy(array_score_array)
                        array_synergy_and_conflicts_at_once[array_synergy_and_conflicts_at_once>0.] = 2 #2 is code for synergies
                        array_synergy_and_conflicts_at_once = array_synergy_and_conflicts_at_once.astype(int)
                        firstsynergyandconflictarray = False
                    else: 
                        array_synergy_and_conflicts_at_once = updateSynergyAndConflictInCellKnowledge(array_score_array, array_synergy_and_conflicts_at_once, spec_score)
                elif ((spec_score < 0) and (scoretypeToCalculateCountFor == "positive")):
                    (outras_count_array, array_score_array, dictCountMapPerMarineUse, dfCountMapPerPairwise, dictpairwisecountrastername, listpairwisecountrastername) = countsToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisecountrastername, calculationtype, countMarineUseMapTableIsTrue, dictCountMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, countPairwiseMapTableIsTrue, dfCountMapPerPairwise, "false", listpairwisecountrastername, somePolygonsIsTrue, numbOfSome, includeSynergyAndConflictAtOnceAreaIsTrue)
                    if (firstsynergyandconflictarray == True):
                        array_synergy_and_conflicts_at_once = np.copy(array_score_array)
                        array_synergy_and_conflicts_at_once[array_synergy_and_conflicts_at_once<0.] = 1 #1 is code for conflicts
                        array_synergy_and_conflicts_at_once = array_synergy_and_conflicts_at_once.astype(int)
                        firstsynergyandconflictarray = False
                    else: 
                        array_synergy_and_conflicts_at_once = updateSynergyAndConflictInCellKnowledge(array_score_array, array_synergy_and_conflicts_at_once, spec_score)
            # make basic raster for extent - part 3:
            else:
                if ((spec_score > 0) and (scoretypeToCalculateCountFor == "negative")):
                    (outras_count_array, array_score_array, dictCountMapPerMarineUse, dfCountMapPerPairwise, dictpairwisecountrastername, listpairwisecountrastername) = countsToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisecountrastername, calculationtype, countMarineUseMapTableIsTrue, dictCountMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, countPairwiseMapTableIsTrue, dfCountMapPerPairwise, "false", listpairwisecountrastername, somePolygonsIsTrue, numbOfSome, includeSynergyAndConflictAtOnceAreaIsTrue)
                    if (firstbasicarray == True): 
                        cells_with_score_array = np.copy(array_score_array)                                    
                        cells_with_score_array[cells_with_score_array>0.] = 1 #1 is code for score
                        cells_with_score_array = cells_with_score_array.astype(int)
                        firstbasicarray = False
                    else: 
                        cells_with_score_array = updateScoreCellCount(array_score_array, cells_with_score_array)
                elif ((spec_score < 0) and (scoretypeToCalculateCountFor == "positive")):
                    (outras_count_array, array_score_array, dictCountMapPerMarineUse, dfCountMapPerPairwise, dictpairwisecountrastername, listpairwisecountrastername) = countsToRasters(inputfolder, inputrastername1, inputrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, dictpairwisecountrastername, calculationtype, countMarineUseMapTableIsTrue, dictCountMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, countPairwiseMapTableIsTrue, dfCountMapPerPairwise, "false", listpairwisecountrastername, somePolygonsIsTrue, numbOfSome, includeSynergyAndConflictAtOnceAreaIsTrue)
                    if (firstbasicarray == True): 
                        cells_with_score_array = np.copy(array_score_array)                                    
                        cells_with_score_array[cells_with_score_array<0.] = 1 #1 is code for score
                        cells_with_score_array = cells_with_score_array.astype(int)
                        firstbasicarray = False
                    else: 
                        cells_with_score_array = updateScoreCellCount(array_score_array, cells_with_score_array)                                    
            iterator2 += 1 #iterate through all rasters that are after raster1 (to iteratively be raster2)
        iterator1 += 1 #new raster1
        iterator2 = iterator1+1 #start again by iterating through rasters to be raster2 (now the number of following rasters has decreased by 1)
    # make total count raster with land area as NoData: 
    ocean_array_land = ocean_array == 0
    # make synergy-and-conflict area polygon - part 4:
    if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
        cells_with_no_output = array_synergy_and_conflicts_at_once == 0
    # make basic raster for extent - part 4:
    else: 
        cells_with_no_output = cells_with_score_array == 0
    np.place(cummulated_count_outras_array, ocean_array_land & cells_with_no_output, np.nan)   
    countRaster = arcpy.NumPyArrayToRaster(cummulated_count_outras_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    createNewPath(finalfoldername)
    output_tif_incl_folder = finalfoldername+"\\"+countraster_finaloutputname_only_ocean
    countRaster.save(output_tif_incl_folder)
    arcpy.DefineProjection_management(output_tif_incl_folder, spatial_ref)
    # table 1 inputs:
    if countMarineUseMatrixTableIsTrue == "true":
        getTotalMatrixCountPerMarineUse(dictCountMatrixPerMarineUse, scoretypeToCalculateCountFor, finalfoldername, countMarineUseMatrixTable)       
    # table 2 inputs:
    if countMarineUseMapTableIsTrue == "true":
        getTotalMapCountPerMarineUse(dictCountMapPerMarineUse, finalfoldername, scoretypeToCalculateCountFor, countMarineUseMapTable, listOfLongMarineUseNames)
    # table 3 inputs:
    if countPairwiseMapTableIsTrue == "true":
        getTotalMapCountPerPairwiseCombination(finalfoldername, dfCountMapPerPairwise, countPairwiseMapTable)        
    # if is chosen to only add polygons to map with highest and lowest scores:
    if ((countPairwiseMapTableIsTrue == "true") and (somePolygonsIsTrue == "true") and (numbOfSome != "all")):
        # add numbOfSome highest positive pairwise count score polygons:
        dictpairwisecountrastername_synergiesfirst = OrderedDict(sorted(dictpairwisecountrastername.items(), reverse=True))
        (listpairwisecountpolygon, listpairwisecountpolygonname) = getNumbOfSomePolygonElementsFromOrderedDict(dictpairwisecountrastername_synergiesfirst, numbOfSome, listpairwisecountpolygon, listpairwisecountpolygonname, pairwise_output_folder)
    elif (numbOfSome != 0):
        (listpairwisecountpolygon, listpairwisecountpolygonname) = getNumbOfAllPolygonElementsFromOrderedList(listpairwisecountrastername, listpairwisecountpolygon, listpairwisecountpolygonname, pairwise_output_folder)
    return (output_tif_incl_folder, listpairwisecountpolygon, listpairwisecountpolygonname, array_synergy_and_conflicts_at_once)

def countsToRasters(inputfoldername, inputrastername1, inputrastername2, score, lower_left_corner, dsc, matrixinput, pairwise_output_folder, dictpairwisecountrastername, calculationtype, countSumMarineUseMapTableIsTrue, dictCountMapPerMarineUse, inputmarineuselongname1, inputmarineuselongname2, countSumPairwiseMapTableIsTrue, dfCountMapPerPairwise, getStatisticsAndPolygons, listpairwisecountrastername, somePolygonsIsTrue, numbOfSome, includeSynergyAndConflictAtOnceAreaIsTrue):
    # create pairwise marine use score raster
    array_pairwise_score = "NoDataAsDefault"
    inputname1 = inputfoldername+"\\"+inputrastername1
    array_input1_becoming_pairwise_count_array = arcpy.RasterToNumPyArray(inputname1)
    array_input1_becoming_pairwise_count_array = array_input1_becoming_pairwise_count_array.astype(float)
    inputname2 = inputfoldername+"\\"+inputrastername2
    array_input2 = arcpy.RasterToNumPyArray(inputname2)
    array_input2 = array_input2.astype(float)
    ifOverlaps = array_input1_becoming_pairwise_count_array+array_input2==2.   
    # table 2 inputs:
    if ((countSumMarineUseMapTableIsTrue == "true") and (getStatisticsAndPolygons == "true")):
        # count of individual marine use raster cells: 
        dictCountMapPerMarineUse[inputmarineuselongname1][0]=np.count_nonzero(array_input1_becoming_pairwise_count_array)
        dictCountMapPerMarineUse[inputmarineuselongname2][0]=np.count_nonzero(array_input2)
        dictCountMapPerMarineUse[inputmarineuselongname1][5] += ifOverlaps
        dictCountMapPerMarineUse[inputmarineuselongname2][5] += ifOverlaps
    array_input1_becoming_pairwise_count_array[array_input1_becoming_pairwise_count_array+array_input2!=2.] = 0.
    # if polygon with synergies-and-conflicts-at-once should be included, get score array to count synergies and conflicts:
    if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):      
        array_pairwise_score = np.copy(array_input1_becoming_pairwise_count_array)    
        array_pairwise_score[array_pairwise_score+array_input2==2.] = score
    # count everything matching the count type: 
    array_input1_becoming_pairwise_count_array[ifOverlaps] = 1
    #array_input1_becoming_pairwise_count_array = array_input1_becoming_pairwise_count_array.astype(int)
    # table 2 inputs:
    if ((countSumMarineUseMapTableIsTrue == "true") and (getStatisticsAndPolygons == "true")):
        # count of score cells:
        dictCountMapPerMarineUse[inputmarineuselongname1][3]+= np.count_nonzero(array_input1_becoming_pairwise_count_array)
        dictCountMapPerMarineUse[inputmarineuselongname2][3]+= np.count_nonzero(array_input1_becoming_pairwise_count_array)
    # table 3 inputs:
    if ((countSumPairwiseMapTableIsTrue == "true") and (getStatisticsAndPolygons == "true")):
        (dfCountMapPerPairwise.loc[dfCountMapPerPairwise['Idcolumn'] == inputmarineuselongname2, inputmarineuselongname1]) = np.count_nonzero(array_input1_becoming_pairwise_count_array)   
    # create pairwise marine use polygon:
    #len(np.unique(array_input1_becoming_pairwise_count_array)) > 1
    if ((np.count_nonzero(array_input1_becoming_pairwise_count_array) > 1) and (getStatisticsAndPolygons == "true") and (numbOfSome != 0)): # if there is more than one unique value in the array (meaning more values than just zero) 
        (dictpairwisecountrastername, listpairwisecountrastername) = pairwiseCountRasterToSave(array_input1_becoming_pairwise_count_array, lower_left_corner, dsc, spatial_ref, pairwise_output_folder, inputrastername1, inputrastername2, calculationtype, matrixinput, dictpairwisecountrastername, np.count_nonzero(array_input1_becoming_pairwise_count_array), listpairwisecountrastername, countPairwiseMapTableIsTrue, somePolygonsIsTrue, numbOfSome)
    return (array_input1_becoming_pairwise_count_array, array_pairwise_score, dictCountMapPerMarineUse, dfCountMapPerPairwise, dictpairwisecountrastername, listpairwisecountrastername)

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

def getNumbOfAllPolygonElementsFromOrderedList(listpairwisecountrastername, listpairwisecountpolygon, listpairwisecountpolygonname, pairwise_output_folder):
    for i in range(len(listpairwisecountrastername)):
        if i%2 == 0:
            (listpairwisecountpolygon, listpairwisecountpolygonname) = pairwiseCountRasterToPolygon(listpairwisecountrastername[i], listpairwisecountrastername[i+1], pairwise_output_folder, listpairwisecountpolygon, listpairwisecountpolygonname)
    return (listpairwisecountpolygon, listpairwisecountpolygonname)

def getNumbOfSomePolygonElementsFromOrderedDict(dictpairwisecountrastername, numbOfSome, listpairwisecountpolygon, listpairwisecountpolygonname, pairwise_output_folder):
    dictiterator=0
    for sum_of_all_scores, raster_element_list in dictpairwisecountrastername.items():
        if dictiterator >= numbOfSome: 
            break
        for i in range(len(raster_element_list)/2):
            if i%2 == 0: 
                (listpairwisecountpolygon, listpairwisecountpolygonname) = pairwiseCountRasterToPolygon(raster_element_list[i], raster_element_list[i+1], pairwise_output_folder, listpairwisecountpolygon, listpairwisecountpolygonname)
                dictiterator+=1      
    return (listpairwisecountpolygon, listpairwisecountpolygonname)

# table 2 inputs: 
def getTotalMapCountPerMarineUse(dictCountMapPerMarineUse, finalfoldername, scoretypeToCalculateCountFor, countMarineUseMapTable, listOfLongMarineUseNames):
    # get count of contributing marine use raster cells:
    for longname in listOfLongMarineUseNames:
        dictCountMapPerMarineUse[longname][5] = np.sum(dictCountMapPerMarineUse[longname][5])
    df = pd.DataFrame.from_dict(dictCountMapPerMarineUse, orient='index')
    columnA = "Count of individual marine use raster cells for each marine use"    
    columnB = "Count of ocean raster cells"  
    columnC = "Ocean coverage percentage of data"
    columnF = "Count of each marine use raster cells that contain at least one overlap (overlap as defined by the count setting)"            
    if (countChoice == "count all combinations with a specific marine use") or (countChoice == "count all"):       
        columnD = "Total count of spatial pairwise combinations in map for each marine use (including the combinations that do not have a synergy-conflict score)"
        columnE = "Average count of spatial pairwise combinations per raster cell in map for each marine use (including the combinations that do not have a synergy-conflict score)"
        columnG = "Average count of spatial pairwise combinations per raster cell with overlaps in map for each marine use (including the combinations that do not have a synergy-conflict score)"            
    elif (scoretypeToCalculateCountFor == "all"):
        columnD = "Total count of spatial pairwise combinations in map for each marine use (only the combinations that have a synergy-conflict score)"
        columnE = "Average count of spatial pairwise combinations per raster cell in map for each marine use (only the combinations that have a synergy-conflict score)"
        columnG = "Average count of spatial pairwise combinations per raster cell with conflict-synergy overlaps in map for each marine use (only the combinations that have a synergy-conflict score)"
    elif (scoretypeToCalculateCountFor == "positive"):
        columnD = "Total count of spatial positive pairwise combinations in map for each marine use"
        columnE = "Average count of spatial positive pairwise combinations per raster cell in map for each marine use"
        columnG = "Average count of spatial positive pairwise combinations per raster cell with synergy overlaps in map for each marine use"
    elif (scoretypeToCalculateCountFor == "negative"):
        columnD = "Total count of spatial negative pairwise combinations in map for each marine use"
        columnE = "Average count of spatial negative pairwise combinations per raster cell in map for each marine use"
        columnG = "Average count of spatial negative pairwise combinations per raster cell with conflict overlaps in map for each marine use"
    df.columns = [columnA, columnB, columnC, columnD, columnE, columnF, columnG]  
    if (scoretypeToCalculateCountFor == "all") or (scoretypeToCalculateCountFor == "positive"):
        df = df.sort_values(by=[columnD], ascending=False)
    elif (scoretypeToCalculateCountFor == "negative"):
        df = df.sort_values(by=[columnD], ascending=True)
    # count coverage percentage:
    df[columnC] = df[columnA]/df[columnB]*100
    # count average count per marine use raster cell:
    df[columnE] = df[columnD]/df[columnA]
    # count average count per contributing marine use raster cell:
    df[columnG] = df[columnD]/df[columnF]
    createNewPath(os.path.join(os.path.dirname(__file__),finalfoldername))
    df.to_excel(os.path.join(os.path.dirname(__file__),finalfoldername,countMarineUseMapTable))  

# table 3 inputs: 
def getTotalMapCountPerPairwiseCombination(finalfoldername, dfCountMapPerPairwise, countPairwiseMapTable):
    createNewPath(os.path.join(os.path.dirname(__file__),finalfoldername))
    dfCountMapPerPairwise.to_excel(os.path.join(os.path.dirname(__file__),finalfoldername,countPairwiseMapTable), index=False)  

# table 1 inputs: 
def getTotalMatrixCountPerMarineUse(dictCountMatrixPerMarineUse, scoretypeToCalculateCountFor, finalfoldername, countMarineUseMatrixTable):
    dfCountMatrixPerMarineUse = pd.DataFrame.from_dict(dictCountMatrixPerMarineUse, orient='index')
    if (scoretypeToCalculateCountFor == "all"):        
        columnA = "Count of all combinations including empty outputs"
        columnB = "Count of inputted synergy scores"
        columnC = "Count of inputted conflict scores"
        dfCountMatrixPerMarineUse.columns = [columnA, columnB, columnC] 
    elif scoretypeToCalculateCountFor == "positive":
        columnA = "Count of inputted synergy scores"
        dfCountMatrixPerMarineUse.columns = [columnA] 
    elif scoretypeToCalculateCountFor == "negative":
        columnA = "Count of inputted conflict scores"
        dfCountMatrixPerMarineUse.columns = [columnA] 
    if (scoretypeToCalculateCountFor == "all") or (scoretypeToCalculateCountFor == "positive"):
        dfCountMatrixPerMarineUse = dfCountMatrixPerMarineUse.sort_values(by=[columnA], ascending=False)
    elif scoretypeToCalculateCountFor == "negative":
        dfCountMatrixPerMarineUse = dfCountMatrixPerMarineUse.sort_values(by=[columnA], ascending=False)
    createNewPath(os.path.join(os.path.dirname(__file__),finalfoldername))
    dfCountMatrixPerMarineUse.to_excel(os.path.join(os.path.dirname(__file__),finalfoldername,countMarineUseMatrixTable))

def pairwiseCountRasterToPolygon(rastername, matrixinput, pairwise_output_folder, listpairwisecountpolygon, listpairwisecountpolygonname):
    createNewPath(pairwise_output_folder)
    marineuseoutput_shp_excl_folder = rastername[:-4]+".shp"
    marineuseoutput_shp_incl_folder = pairwise_output_folder+"\\"+marineuseoutput_shp_excl_folder
    arcpy.RasterToPolygon_conversion(arcpy.sa.Raster(pairwise_output_folder+"\\"+rastername), marineuseoutput_shp_incl_folder, "NO_SIMPLIFY","VALUE","MULTIPLE_OUTER_PART")             
    addField1(marineuseoutput_shp_incl_folder, "TEXT", fieldname = "finalvalue", precision = "", decimals = "", field_length = 20)
    calculateField1(marineuseoutput_shp_incl_folder, "finalvalue", str(1), expression_type="PYTHON")
    if type(matrixinput) == float: 
        matrixinput = str(matrixinput)  
    if len(matrixinput)%254 == 0: # len(matrixinput) == 0 or len(matrixinput) == 254 or len(matrixinput) == 2*254 etc. ---- # i stedet for elif
        numberroundsneeded = int((len(matrixinput)/254)+1) #if len(matrixinput) == 0 numberroundsneeded is 1 but never used; if len(matrixinput) == 254 will numberroundsneeded = 2; if len(matrixinput) == 2*254 will numberroundsneeded = 3 etc.
    else: # len(matrixinput) != 0 and len(matrixinput) != 254 and len(matrixinput) != 2*254 etc.
        numberroundsneeded = int((len(matrixinput)/254)+2) #if len(matrix) >= 1 and <= 253 then numberroundsneeded is 2; if len(matrix) >= 255 and <= 2*253 then numberroundsneeded is 3 etc.
    matrixstart=0
    matrixend=254
    if len(matrixinput) > 0: #if matrixinput is not an empty string 
        for fieldcount in range(1,numberroundsneeded): #if numberroundsneeded == 1 will be added 0 matrix-attribute full_desc; if numberroundsneeded == 2 will be added 1 matrix-attribute full_desc; if numberroundsneeded == 3 will be added 2 matrix-attribute full_desc etc.
            addField1(marineuseoutput_shp_incl_folder, "TEXT", "full_desc"+str(fieldcount), precision = "", decimals = "", field_length = 254)
            calculateField1(marineuseoutput_shp_incl_folder, "full_desc"+str(fieldcount), "'"+matrixinput[matrixstart:matrixend]+"'", expression_type="PYTHON")
            matrixstart=matrixstart+254
            matrixend=matrixend+254
            if matrixend > len(matrixinput):
                matrixend = len(matrixinput)
    arcpy.DeleteField_management(marineuseoutput_shp_incl_folder, "Id")
    listpairwisecountpolygon.append(marineuseoutput_shp_incl_folder)
    listpairwisecountpolygonname.append(marineuseoutput_shp_excl_folder)
    return (listpairwisecountpolygon, listpairwisecountpolygonname)

def pairwiseCountRasterToSave(array_input, lower_left_corner, dsc, spatial_ref, pairwise_output_folder, inputrastername1, inputrastername2, calculationtype, matrixinput, dictpairwisecountrastername, count_of_all_score_cells, listpairwisecountrastername, countSumPairwiseMapTableIsTrue, somePolygonsIsTrue, numbOfSome):
    if (numbOfSome != 0):
        pairwise_marine_use_array = np.copy(array_input)
        pairwise_marine_use_array = pairwise_marine_use_array.astype(int)
        pairwise_marine_use_array[pairwise_marine_use_array!=0.] = 1
        pairwiseCountRaster = arcpy.NumPyArrayToRaster(pairwise_marine_use_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight, 0)
        createNewPath(pairwise_output_folder)
        raster_outputname = returnRasterFilename(inputrastername1, inputrastername2, calculationtype)
        pairwiseCountRaster.save(pairwise_output_folder+"\\"+raster_outputname)
        arcpy.DefineProjection_management(pairwise_output_folder+"\\"+raster_outputname, spatial_ref)
    # if is chosen to only add polygons to map with highest and lowest scores:
    if ((countSumPairwiseMapTableIsTrue == "true") and (somePolygonsIsTrue == "true") and (numbOfSome != "all")):
        if count_of_all_score_cells in dictpairwisecountrastername: 
            dictpairwisecountrastername[count_of_all_score_cells].append(raster_outputname)
            dictpairwisecountrastername[count_of_all_score_cells].append(matrixinput)
        else: 
            dictpairwisecountrastername[count_of_all_score_cells] = [raster_outputname, matrixinput]
    # if it is chosen to add all polygons to map:
    else:
        listpairwisecountrastername.append(raster_outputname)
        listpairwisecountrastername.append(matrixinput)
    return (dictpairwisecountrastername, listpairwisecountrastername)    

def populateCurrentMapDocument(outputrastername_tif_incl_folder, outputrastername_tif_excl_folder, listpairwisecountpolygon, listpairwisecountpolygonname, output_shp_incl_folder, output_shp_excl_folder, count_lyrfile, pairwise_marine_use_lyrfile, conflict_and_synergy_lyrfile, final_folder, pairwise_output_folder, includeSynergyAndConflictAtOnceAreaIsTrue):
    try: 
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        addLayerToMxd(mxd, df, outputrastername_tif_incl_folder, outputrastername_tif_excl_folder, count_lyrfile, 'TOP', "mainmap", final_folder)
        if includeSynergyAndConflictAtOnceAreaIsTrue == "true":        
            addLayerToMxd(mxd, df, output_shp_incl_folder, output_shp_excl_folder, conflict_and_synergy_lyrfile, 'BOTTOM', "both_synergies_and_conflicts", final_folder)            
        for pairwisecountpolygon, pairwisecountpolygonname in zip(listpairwisecountpolygon, listpairwisecountpolygonname):
            addLayerToMxd(mxd, df, pairwisecountpolygon, pairwisecountpolygonname, pairwise_marine_use_lyrfile, 'BOTTOM', "pairwise_polygon", pairwise_output_folder) #raster parameter does not matter when not mainmap
    except: 
        arcpy.AddMessage("ERROR: You cannot have two MXD documents open for this tool to work")

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
scoretypeToCalculateCountFor = arcpy.GetParameterAsText(3)
    
#parameter4 = countraster_finaloutputname_only_ocean
countraster_finaloutputname_only_ocean = arcpy.GetParameterAsText(4)

#parameter5 = oceanrastername_with_path 
oceanrastername_with_path = arcpy.GetParameterAsText(5)

#parameter6 = count_lyrfile 
try: 
    count_lyrfile = arcpy.GetParameterAsText(6)
    if count_lyrfile == "": 
        count_lyrfile = "NotExisting"
except: 
    count_lyrfile = "NotExisting"

#parameter7 = pairwise_marine_use_lyrfile 
try: 
    pairwise_marine_use_lyrfile = arcpy.GetParameterAsText(7)
    if pairwise_marine_use_lyrfile == "": 
        pairwise_marine_use_lyrfile = "NotExisting"
except: 
    pairwise_marine_use_lyrfile = "NotExisting"

#parameter8 = score sum per marine use based on matrix (checked or unchecked)  
countMarineUseMatrixTableIsTrue = arcpy.GetParameterAsText(8) 

#parameter9 = score sum per marine use based on map (checked or unchecked)  
countMarineUseMapTableIsTrue = arcpy.GetParameterAsText(9) 

#parameter10 = score sum per pairwise combination based on map (checked or unchecked)  
countPairwiseMapTableIsTrue = arcpy.GetParameterAsText(10) 

#parameter11 = only highest pairwise marine use counts polygons (checked or unchecked) 
try: 
    somePolygonsIsTrue = arcpy.GetParameterAsText(11)
    if somePolygonsIsTrue == "": 
        somePolygonsIsTrue = "false"
except: 
    somePolygonsIsTrue = "false"

#parameter12 = the maximum number of pairwise marine use polygons to include 
try: 
    numbOfSome = int(arcpy.GetParameterAsText(12))
    if numbOfSome == "": 
        numbOfSome = "all"
    elif ((numbOfSome == 0) and (somePolygonsIsTrue == "false")): 
        numbOfSome = "all"
except: 
    numbOfSome = "all" #parameter is irrelevant if not activated 

#parameter13 = selected lists of count options 
##countChoice = "count all" #all [default choice]
##countChoice = "count combinations for a specific conflict-synergy category" #inputs
##countChoice = "count all combinations with a specific marine use" #all
##countChoice = "count combinations with a specific marine use where synergy-conflict inputs exist" #inputs
##countChoice = "count combinations where synergy-conflict inputs exist" #inputs
##countChoice = "count multiuse-options mentioned in the MUSES project" #inputs
##countChoice = "count vertically different overlaps" #specific inputs
##countChoice = "count vertically same overlaps" #specific inputs
##countChoice = "count pairwise overlaps where both marine uses are mobile" #specific inputs
countChoice = arcpy.GetParameterAsText(13)

#parameter14 = chosen category
try:
    chosen_category = arcpy.GetParameterAsText(14)
    if chosen_category == "Class 1: Compatible synergy overlaps level 1: Compatible spatial overlaps with synergies and no conflicts (suggested score: 3).":
        chosen_category_score = "3.00" #"Compatible synergy overlaps"
    elif chosen_category == "Class 2: Compatible synergy overlaps level 2: Compatible spatial overlaps with more synergies than conflicts (suggested score: 2.75).":
        chosen_category_score = "2.75" #"Compatible synergy overlaps"
    elif chosen_category == "Class 3: Compatible neutral overlaps: Compatible neutral spatial overlaps (suggested score: 2.5).":
        chosen_category_score = "2.50" #"Compatible neutral overlaps"
    elif chosen_category == "Class 4: Conditionally compatible synergy neighbours level 1: Conditionally compatible uses with neighbourhood synergies and no neighbourhood conflicts (suggested score: 2).":
        chosen_category_score = "2.00" #"Conditionally compatible synergy neighbours"
    elif chosen_category == "Class 5: Conditionally compatible synergy neighbours level 2: Conditionally compatible uses with more neighbourhood synergies than neighbourhood conflicts (suggested score: 1.75).":
        chosen_category_score = "1.75" #"Conditionally compatible synergy neighbours"
    elif chosen_category == "Class 6: Non-compatible synergy neighbours level 1: Non-compatible uses with neighbourhood synergies and no neighbourhood conflicts (suggested score: 1.5).":
        chosen_category_score = "1.50" #"Non-compatible synergy neighbours"
    elif chosen_category == "Class 7: Non-compatible synergy neighbours level 2: Non-compatible uses with more neighbourhood synergies than neighbourhood conflicts (suggested score: 1.25).":
        chosen_category_score = "1.25" #"Non-compatible synergy neighbours"
    elif chosen_category == "Class 8: Conditionally compatible neutral neighbours: Conditionally compatible uses with neutral neighbourhood relations (suggested score: 1).":
        chosen_category_score = "1.00" #"Conditionally compatible neutral neighbours"
    elif chosen_category == "Class 9: Non-compatible neutral neighbours: Non-compatible uses with neutral neighbourhood relations (suggested score: -1).":
        chosen_category_score = "-1.00" #"Non-compatible neutral neighbours"
    elif chosen_category == "Class 10: Conditionally compatible conflicting neighbours: Conditionally compatible uses with conflicting neighbourhood relations (only a few conflicts) (suggested score: -2).":
        chosen_category_score = "-2.00" #"Conditionally compatible conflicting neighbours"
    elif chosen_category == "Class 11: Non-compatible conflicting neighbours: Non-compatible uses with conflicting neighbourhood relation (suggested score: -3).":
        chosen_category_score = "-3.00" #"Non-compatible conflicting neighbours"
    else: 
        chosen_category_score = ""
except: 
    chosen_category = ""
    chosen_category_score = ""

#parameter15 = the marine use to focus on 
try:
    marineUseInFocus = arcpy.GetParameterAsText(15)
    if marineUseInFocus == "": 
        marineUseInFocus = "false"
except: 
    marineUseInFocus = "false"

#parameter16 = excelsheet with temporal and spatial attributes for each marine use
try:
    attribute_excelsheet = arcpy.GetParameterAsText(16)
    if attribute_excelsheet == "": 
        attribute_excelsheet = "false"
except: 
    attribute_excelsheet = "false"

#parameter17 = include synergy-and-conflict area (checked or unchecked)
try: 
    includeSynergyAndConflictAtOnceAreaIsTrue = arcpy.GetParameterAsText(17)
    if includeSynergyAndConflictAtOnceAreaIsTrue == "": 
        includeSynergyAndConflictAtOnceAreaIsTrue = "false"
except: 
    includeSynergyAndConflictAtOnceAreaIsTrue = "false"

#extra script parameters: 
pairwise_output_folder = "pairwise_outputs"
final_folder = "final_results"
if (scoretypeToCalculateCountFor == "all") and ((countChoice == "count all") or (countChoice == "count all combinations with a specific marine use")):
    prename_table = scoretypeToCalculateCountFor + "_" + scoretypeToCalculateCountFor
else: 
    prename_table = scoretypeToCalculateCountFor
countMarineUseMatrixTable = "table1_"+prename_table+"_"+"total_count_per_marineuse_matrix.xlsx" 
countMarineUseMapTable = "table2_"+prename_table+"_"+"total_count_per_marineuse_map.xlsx"
countPairwiseMapTable = "table3_"+prename_table+"_"+"total_count_per_pairwise_combination_map.xlsx"
conflict_and_synergy_shapefile = "conflict_and_synergy_at_once.shp"
conflict_and_synergy_lyrfile = "NotExisting"
calculationtype = "count_"


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
(output_tif_incl_folder, listpairwisecountpolygon, listpairwisecountpolygonname, synergies_and_or_conflicts_array) = calculatePairwiseAndTotalCountRasters(dictMarineUses, inputexcelsheet, scoretypeToCalculateCountFor, inputfolder, pairwise_output_folder, final_folder, countMarineUseMatrixTableIsTrue, countMarineUseMatrixTable, countMarineUseMapTableIsTrue, countMarineUseMapTable, countPairwiseMapTableIsTrue, countPairwiseMapTable, somePolygonsIsTrue, numbOfSome, countChoice, chosen_category, chosen_category_score, marineUseInFocus, attribute_excelsheet, includeSynergyAndConflictAtOnceAreaIsTrue, lower_left_corner, dsc, spatial_ref, countraster_finaloutputname_only_ocean, oceanrastername_with_path, calculationtype)
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Pairwise count rasters and total count raster have been calculated, {}\n".format(printline))

if includeSynergyAndConflictAtOnceAreaIsTrue == "true":
    starttimetobeupdated = resetTime(starttimetobeupdated)
    (output_shp_incl_folder, output_shp_excl_folder) = synergyAndConflictAtOnceRasterToPolygon(synergies_and_or_conflicts_array, lower_left_corner, dsc, spatial_ref, final_folder, conflict_and_synergy_shapefile)
    (printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
    arcpy.AddMessage("Synergy-and-conflict-at-once-raster has been calculated, {}\n".format(printline))
else: 
    output_shp_incl_folder = "false"
    output_shp_excl_folder = "false"

starttimetobeupdated = resetTime(starttimetobeupdated)
populateCurrentMapDocument(output_tif_incl_folder, countraster_finaloutputname_only_ocean, listpairwisecountpolygon, listpairwisecountpolygonname, output_shp_incl_folder, output_shp_excl_folder, count_lyrfile, pairwise_marine_use_lyrfile, conflict_and_synergy_lyrfile, final_folder, pairwise_output_folder, includeSynergyAndConflictAtOnceAreaIsTrue)
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("If data exist, it has been added to current MXD document, {}\n".format(printline))






