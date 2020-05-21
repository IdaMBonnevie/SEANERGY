# Purpose of script: 
#Script input to the tool called 'Find Synergy Potential Scores For New Marine Use'. 
#It finds locations and scores of all marine uses that pairwisely have a positive conflict-synergy score with the specified input marine use. 
#It calculates the total scores of those potential positive combinations per cell. 

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
#        if self.params[2].altered:
#            excelfile_with_path = (self.params[2].value.value).replace("\a","\\a").replace("\b","\\b")
#            df = pd.read_excel(excelfile_with_path)
#            rawlist_options = list(df.columns)
#            list_options = rawlist_options[1:]
#            self.params[3].filter.list = list_options
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

def addLayerToMxd(mxd, df, inputname_inkl_folder, lyrfile, place, mode, inputfolder, inputname_excl_folder):
    if mode == "marine_use_individual" or mode == "marine_use_pairwise":
        rlayer1 = arcpy.mapping.Layer(os.path.join(os.path.dirname(__file__),inputname_inkl_folder))        
    elif mode == "mainmap":
        result = arcpy.MakeRasterLayer_management(arcpy.mapping.Layer(os.path.join(os.path.dirname(__file__),inputname_inkl_folder)), inputname_excl_folder[:-4]) 
        rlayer1 = result.getOutput(0)
    if lyrfile == "NotExisting": 
        lyrfile = "NotExisting"
    else: 
        arcpy.ApplySymbologyFromLayer_management(rlayer1, lyrfile)
        if mode == "marine_use_individual" or mode == "marine_use_pairwise": 
            if rlayer1.symbologyType == "UNIQUE_VALUES":
                rlayer1.symbology.addAllValues()
    arcpy.mapping.AddLayer(df, rlayer1, place)
    del mxd, df

def calculateField1(outputpath, valuefield, valueToInput, expression_type="VB"): 
    arcpy.CalculateField_management(outputpath, valuefield, valueToInput, expression_type, "")

def calculatePotentialSynergiesWithExistingUsesRaster(marineUseInFocus, dictMarineUses, matrixexcelfile, inputfolder, final_folder, pairwise_output_folder, process_folder, addConflictingExistingMarineUseInteractionsIsTrue, synergy_with_existing_uses_raster_only_ocean_name, oceanrastername_with_path, lower_left_corner, dsc, spatial_ref, starttimetobeupdated):
    dfdesc = pd.read_excel(matrixexcelfile) #, index=False   
    listOfLongMarineUseNames = dictMarineUses.keys()
    if marineUseInFocus in listOfLongMarineUseNames:
        calculationtype = "pot_score_"+dictMarineUses.get(marineUseInFocus)[:-4]+"_"
        inMarineUseRasterDict = True
    else: 
        calculationtypepart = marineUseInFocus.replace(" ","")
        if len(calculationtypepart) > 7:
            calculationtype = "pot_score_"+marineUseInFocus[:7]+"_"
            marineusename = marineUseInFocus[:7]
        else: 
            calculationtype = "pot_score_"+marineUseInFocus+"_"  
            marineusename = marineUseInFocus
        inMarineUseRasterDict = False 
    listOfExistingMarineUses = []
    marineusepolygonlist = []
    marineusepolygonnamelist = []
    pairwisescorepolygonlist = []
    pairwisescorepolygonnamelist = []
    firstposraster = True
    firstnegraster = True
    iterator1 = 0
    iterator2 = 1
    #make total potential score raster of potential synergy overlaps between existing marine uses and the chosen new marine use, as well as make individual marine use score polygons of marine uses with potential synergies with the chosen new marine use: 
    for column in listOfLongMarineUseNames: 
        # if marine use is in marine use raster dictionary
        if (inMarineUseRasterDict == True):
            inputrastername1 = dictMarineUses.get(column) #get raster1
            while iterator2 in range((iterator1+1),len(listOfLongMarineUseNames)):
                if ((marineUseInFocus == column) or (marineUseInFocus == listOfLongMarineUseNames[iterator2])):
                    alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongMarineUseNames[iterator2], column].values
                    if len(alldesc_nparray) > 0:
                        alldesc = alldesc_nparray.item(0)
                        if len(str(alldesc)) >= 4: 
                            if alldesc[:1] == "-": 
                                spec_score = float(alldesc[:5].replace(",",".")) #get the score
                            else: 
                                spec_score = float(alldesc[:4].replace(",",".")) #get the score            
                            inputrastername2 = dictMarineUses.get(listOfLongMarineUseNames[iterator2]) #get raster2
                            if (marineUseInFocus == column):
                                (score_outras_array, overnull, marineusepolygonlist, marineusepolygonnamelist) = scoreToOneRaster(inputfolder, inputrastername2, spec_score, lower_left_corner, dsc, spatial_ref, alldesc, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype)
                            elif (marineUseInFocus == listOfLongMarineUseNames[iterator2]):
                                (score_outras_array, overnull, marineusepolygonlist, marineusepolygonnamelist) = scoreToOneRaster(inputfolder, inputrastername1, spec_score, lower_left_corner, dsc, spatial_ref, alldesc, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype)
                            if spec_score < 0: 
                                if firstnegraster == True:         
                                    remove_area_array = score_outras_array < 0
                                    firstnegraster = False
                                else: 
                                    specific_score_array = np.copy(score_outras_array)
                                    remove_area_specific_array = specific_score_array < 0
                                    remove_area_array = (remove_area_array | remove_area_specific_array)
                            if spec_score > 0: 
                                if (marineUseInFocus == column):
                                    if overnull == True: 
                                        listOfExistingMarineUses.append(inputrastername2)
                                elif (marineUseInFocus == listOfLongMarineUseNames[iterator2]):
                                    if overnull == True: 
                                        listOfExistingMarineUses.append(inputrastername1)                                    
                                if firstposraster == True:         
                                    cummulated_score_outras_array = score_outras_array
                                    firstposraster = False
                                else: 
                                    cummulated_score_outras_array += score_outras_array
                iterator2 += 1 #iterate through all rasters that are after raster1 (to iteratively be raster2)
        # if marine use is not in marine use raster dictionary - 
        ## and the marine-use-raster-index of column is smaller than the marine-use-raster-index of the marine use in focus
        ### the pairwise score is found for the column and the marine-use-in-focus-as-row
        elif ((inMarineUseRasterDict == False) and (dfdesc.columns.tolist().index(column) < dfdesc.columns.tolist().index(marineUseInFocus))):
            inputrastername1 = dictMarineUses.get(column) #get raster1
            inputlongname1 = column
            inputrastername2 = marineusename
            inputlongname2 = marineUseInFocus
            alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == inputlongname2, inputlongname1].values
            if len(alldesc_nparray) > 0:
                alldesc = alldesc_nparray.item(0)
                if len(str(alldesc)) >= 4: 
                    if alldesc[:1] == "-": 
                        spec_score = float(alldesc[:5].replace(",",".")) #get the score
                    else: 
                        spec_score = float(alldesc[:4].replace(",",".")) #get the score            
                    (score_outras_array, overnull, marineusepolygonlist, marineusepolygonnamelist) = scoreToOneRaster(inputfolder, inputrastername1, spec_score, lower_left_corner, dsc, spatial_ref, alldesc, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype)
                    if spec_score < 0: 
                        if firstnegraster == True:         
                            remove_area_array = score_outras_array < 0
                            firstnegraster = False
                        else: 
                            specific_score_array = np.copy(score_outras_array)
                            remove_area_specific_array = specific_score_array < 0
                            remove_area_array = (remove_area_array | remove_area_specific_array)
                    if spec_score > 0: 
                        if overnull == True: 
                            listOfExistingMarineUses.append(inputrastername1)                                    
                        if firstposraster == True:         
                            cummulated_score_outras_array = score_outras_array
                            firstposraster = False
                        else: 
                            cummulated_score_outras_array += score_outras_array
        # if marine use is not in marine use raster dictionary -
        ## and the marine-use-raster-index of column is equal to or larger than the marine-use-raster-index of the marine use in focus
        ### the pairwise score is found iteratively for the marine-use-as-column and other-marine-uses-as-row -
        #### and then the loop breaks for the rest of the columns 
        elif (inMarineUseRasterDict == False):
            inputrastername1 = marineusename
            inputlongname1 = marineUseInFocus
            while iterator2 in range((iterator1+1),len(listOfLongMarineUseNames)):
                alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongMarineUseNames[iterator2], inputlongname1].values
                if len(alldesc_nparray) > 0:
                    alldesc = alldesc_nparray.item(0)
                    if len(str(alldesc)) >= 4: 
                        if alldesc[:1] == "-": 
                            spec_score = float(alldesc[:5].replace(",",".")) #get the score
                        else: 
                            spec_score = float(alldesc[:4].replace(",",".")) #get the score            
                        inputrastername2 = dictMarineUses.get(listOfLongMarineUseNames[iterator2]) #get raster2
                        (score_outras_array, overnull, marineusepolygonlist, marineusepolygonnamelist) = scoreToOneRaster(inputfolder, inputrastername2, spec_score, lower_left_corner, dsc, spatial_ref, alldesc, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype)
                        if spec_score < 0: 
                            if firstnegraster == True:         
                                remove_area_array = score_outras_array < 0
                                firstnegraster = False
                            else: 
                                specific_score_array = np.copy(score_outras_array)
                                remove_area_specific_array = specific_score_array < 0
                                remove_area_array = (remove_area_array | remove_area_specific_array)
                        if spec_score > 0: 
                            if overnull == True: 
                                listOfExistingMarineUses.append(inputrastername2)
                            if firstposraster == True:         
                                cummulated_score_outras_array = score_outras_array
                                firstposraster = False
                            else: 
                                cummulated_score_outras_array += score_outras_array
                iterator2 += 1 #iterate through all rasters that are after raster1 (to iteratively be raster2)
            break
        iterator1 += 1 #new raster1
        iterator2 = iterator1+1 #start again by iterating through rasters to be raster2 (now the number of following rasters has decreased by 1)
    #make total score raster with land area as NoData: 
    ocean_array = arcpy.RasterToNumPyArray(oceanrastername_with_path)
    ocean_array = ocean_array.astype(float)
    ocean_array_land = ocean_array == 0
    np.place(cummulated_score_outras_array, remove_area_array, -1) #highlight conflicts
    np.place(cummulated_score_outras_array, ocean_array_land, np.nan)   
    scoreRaster = arcpy.NumPyArrayToRaster(cummulated_score_outras_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    createNewPath(final_folder)
    output_tif_incl_folder = final_folder+"\\"+synergy_with_existing_uses_raster_only_ocean_name
    scoreRaster.save(output_tif_incl_folder)
    arcpy.DefineProjection_management(output_tif_incl_folder, spatial_ref)
    #make pairwise conflicting marine use score polygons if any negative scores between existing marine uses exist:    
    if addConflictingExistingMarineUseInteractionsIsTrue == "true":
        if len(listOfExistingMarineUses) >= 2: 
            raster1iterator = 0
            while raster1iterator < len(listOfExistingMarineUses):
                shortrastername1 = listOfExistingMarineUses[raster1iterator]
                longrastername1 = dictMarineUses.keys()[dictMarineUses.values().index(shortrastername1)]
                for raster2iterator in range(raster1iterator+1, len(listOfExistingMarineUses)):
                    shortrastername2 = listOfExistingMarineUses[raster2iterator]
                    longrastername2 = dictMarineUses.keys()[dictMarineUses.values().index(shortrastername2)]
                    alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == longrastername2, longrastername1].values
                    if len(alldesc_nparray) > 0:
                        alldesc = alldesc_nparray.item(0)                       
                        if len(str(alldesc)) >= 4: 
                            if alldesc[:1] == "-": 
                                spec_score = float(alldesc[:5].replace(",",".")) #get the score
                                (pairwisescorepolygonlist, pairwisescorepolygonnamelist) = scoresToRasters(inputfolder, shortrastername1, shortrastername2, spec_score, lower_left_corner, dsc, alldesc, pairwise_output_folder, pairwisescorepolygonlist, pairwisescorepolygonnamelist, "score_")
                raster1iterator += 1
    return (output_tif_incl_folder, marineusepolygonlist, marineusepolygonnamelist, pairwisescorepolygonlist, pairwisescorepolygonnamelist)

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

def getTifFilesInFolder(inputfolder):
    inputfileList = os.listdir(inputfolder)
    finalinputfileList = []
    for input in inputfileList: 
    	if input[-4:] == ".tif":
    		finalinputfileList.append(input)
    return finalinputfileList

def individualOrPairwiseScoreRasterToPolygon(array_input, lower_left_corner, dsc, spatial_ref, output_folder, inputrastername1, inputrastername2, calculationtype, matrixinput, score, polygonlist, polygonnamelist):
    individual_or_pairwise_marine_use_array = np.copy(array_input)
    individual_or_pairwise_marine_use_array = individual_or_pairwise_marine_use_array.astype(int)
    individual_or_pairwise_marine_use_array[individual_or_pairwise_marine_use_array!=0.] = 1
    individualOrPairwiseScoreRaster = arcpy.NumPyArrayToRaster(individual_or_pairwise_marine_use_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    createNewPath(output_folder)
    polygon_outputname = returnRasterFilename(inputrastername1, inputrastername2, calculationtype)
    marineuseoutput_shp_draft_incl_folder = output_folder+"\\"+polygon_outputname[:-4]+"_draft.shp"
    marineuseoutput_shp_draft_excl_folder = polygon_outputname[:-4]+"_draft.shp"
    marineuseoutput_shp_incl_folder = output_folder+"\\"+polygon_outputname[:-4]+".shp"
    marineuseoutput_shp_excl_folder = polygon_outputname[:-4]+".shp"
    arcpy.RasterToPolygon_conversion(individualOrPairwiseScoreRaster, marineuseoutput_shp_draft_incl_folder, "NO_SIMPLIFY","VALUE","MULTIPLE_OUTER_PART")             
    arcpy.MakeFeatureLayer_management(marineuseoutput_shp_draft_incl_folder, marineuseoutput_shp_draft_excl_folder[:-4], '"gridcode" = 1')
    arcpy.CopyFeatures_management(marineuseoutput_shp_draft_excl_folder[:-4], marineuseoutput_shp_incl_folder)
    arcpy.DefineProjection_management(marineuseoutput_shp_incl_folder, spatial_ref)
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
            calculateField1(marineuseoutput_shp_incl_folder, "full_desc"+str(fieldcount), "'"+(str(matrixinput[matrixstart:matrixend]).replace("'",""))+"'", expression_type="PYTHON")
            matrixstart=matrixstart+254
            matrixend=matrixend+254
            if matrixend > len(matrixinput):
                matrixend = len(matrixinput)
    arcpy.DeleteField_management(marineuseoutput_shp_incl_folder, "Id")
    polygonlist.append(marineuseoutput_shp_incl_folder)
    polygonnamelist.append(marineuseoutput_shp_excl_folder)
    return (polygonlist, polygonnamelist)

def populateCurrentMapDocument(rastername, output_tif_excl_folder, marineusepolygonnamelist_inkl_folder, marineusepolygonnamelist_exls_folder, pairwisescorepolygonnamelist_inkl_folder, pairwisescorepolygonnamelist_exls_folder, lyrfile1, lyrfile2, inputfolder1, inputfolder2):
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    addLayerToMxd(mxd, df, rastername, lyrfile1, 'TOP', "mainmap", inputfolder1, output_tif_excl_folder)
    for marineusepolygonname_inkl_folder, marineusepolygonname_exls_folder in zip(marineusepolygonnamelist_inkl_folder, marineusepolygonnamelist_exls_folder): 
        addLayerToMxd(mxd, df, marineusepolygonname_inkl_folder, lyrfile2, 'BOTTOM', "marine_use_individual", inputfolder2, marineusepolygonname_exls_folder) #raster parameter does not matter when not mainmap
    for pairwisepolygonname_inkl_folder, pairwisepolygonname_exls_folder in zip(pairwisescorepolygonnamelist_inkl_folder, pairwisescorepolygonnamelist_exls_folder): 
        addLayerToMxd(mxd, df, pairwisepolygonname_inkl_folder, lyrfile2, 'BOTTOM', "marine_use_pairwise", inputfolder2, pairwisepolygonname_exls_folder) #raster parameter does not matter when not mainmap

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
    if inputrastername1 == inputrastername2: 
        if len(inputrastername1[:-4]) >= 7:  
            finalrastername = calculationtype+inputrastername1[:-4][:7]+".tif"   
        else: 
            finalrastername = calculationtype+inputrastername1[:-4]+".tif"    
    else:        
        if len(inputrastername1[:-4]) >= 7 and len(inputrastername2[:-4]) >= 7:  
            finalrastername = calculationtype+inputrastername1[:-4][:7]+"_"+inputrastername2[:-4][:7]+".tif"   
        elif len(inputrastername1) >= 7: 
            finalrastername = calculationtype+inputrastername1[:-4][:7]+"_"+inputrastername2[:-4]+".tif"   
        elif len(inputrastername2) >= 7: 
            finalrastername = calculationtype+inputrastername1[:-4]+"_"+inputrastername2[:-4][:7]+".tif"   
        else: 
            finalrastername = calculationtype+inputrastername1[:-4]+"_"+inputrastername2[:-4]+".tif"    
    return finalrastername                       

def scoresToRasters(inputfoldername, inputrastername1, inputrastername2, score, lower_left_corner, dsc, matrixinput, pairwise_output_folder, pairwisemarineusepolygonlist, pairwisemarineusepolygonnamelist, calculationtype):
    #create pairwise marine use score raster
    inputname1 = inputfoldername+"\\"+inputrastername1
    array_input1 = arcpy.RasterToNumPyArray(inputname1)
    array_input1 = array_input1.astype(float)
    inputname2 = inputfoldername+"\\"+inputrastername2
    array_input2 = arcpy.RasterToNumPyArray(inputname2)
    array_input2 = array_input2.astype(float)
    array_input1[array_input1+array_input2!=2.] = 0.    
    array_input1[array_input1+array_input2==2.] = score
    #create pairwise marine use polygon:
    if np.sum(array_input1) < 0: # should be below 0 since it is conflict scores and thus negative scores 
        (pairwisemarineusepolygonlist, pairwisemarineusepolygonnamelist) = individualOrPairwiseScoreRasterToPolygon(array_input1, lower_left_corner, dsc, spatial_ref, pairwise_output_folder, inputrastername1, inputrastername2, calculationtype, matrixinput, score, pairwisemarineusepolygonlist, pairwisemarineusepolygonnamelist)
    return (pairwisemarineusepolygonlist, pairwisemarineusepolygonnamelist)

def scoreToOneRaster(inputfoldername, inputrastername, score, lower_left_corner, dsc, spatial_ref, matrixinput, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype):
    #create individual marine use score raster
    inputname = inputfoldername+"\\"+inputrastername
    array_input = arcpy.RasterToNumPyArray(inputname)
    array_input = array_input.astype(float)
    array_input[array_input+array_input!=2.] = 0.    
    array_input[array_input+array_input==2.] = score
    overnull=False
    #create individual marine use polygon:
    if np.sum(array_input) > 0: 
        overnull=True
        (marineusepolygonlist, marineusepolygonnamelist) = individualOrPairwiseScoreRasterToPolygon(array_input, lower_left_corner, dsc, spatial_ref, process_folder, inputrastername, inputrastername, calculationtype, matrixinput, score, marineusepolygonlist, marineusepolygonnamelist)
    return (array_input, overnull, marineusepolygonlist, marineusepolygonnamelist)

def valuesToOneInRaster(inputraster, outputname):
    outras = arcpy.sa.Int(arcpy.sa.Con(((inputraster > 0) | (inputraster < 0)),1,0))
    outras.save(os.path.join(os.path.dirname(__file__),outputname))
    return outras


# start timing: 
starttime = time.time()
starttimetobeupdated = starttime

# parameters
#paramter0 = folder_with_rasterinputs
inputfolder = arcpy.GetParameterAsText(0)
rasterinputlist = getTifFilesInFolder(inputfolder)

#parameter1 = marine_uses_linked_to_rasternames excelsheet
marine_uses_linked_to_rasternames_excel = arcpy.GetParameterAsText(1)
dictMarineUses = getDictionaryFromExcelTwoColumns(marine_uses_linked_to_rasternames_excel, 'full_marine_use_category_name')

#parameter2 = matrix excelsheet
inputexcelsheet = arcpy.GetParameterAsText(2)

#parameter3 = marine use in focus
marineUseInFocus = arcpy.GetParameterAsText(3)

#parameter4 = synergy_with_existing_uses_raster_only_ocean_name
synergy_with_existing_uses_raster_only_ocean_name = arcpy.GetParameterAsText(4)

#parameter5 = oceanrastername_with_path
oceanrastername_with_path = arcpy.GetParameterAsText(5)

#parameter6 = synergy_lyrfile
try: 
    new_marine_use_potentials_lyrfile = arcpy.GetParameterAsText(6)
    if new_marine_use_potentials_lyrfile == "": 
        new_marine_use_potentials_lyrfile = "NotExisting"
except: 
    new_marine_use_potentials_lyrfile = "NotExisting"

#parameter7 = pairwise_lyrfile  
try: 
    pairwise_lyrfile = arcpy.GetParameterAsText(7)
    if pairwise_lyrfile == "": 
        pairwise_lyrfile = "NotExisting"
except: 
    pairwise_lyrfile = "NotExisting"

#parameter8 = add existing marine use interactions #boolean #if yes, then get all polygons and cut them with new marine use raster 
addConflictingExistingMarineUseInteractionsIsTrue = arcpy.GetParameterAsText(8)

#extra script parameters: 
pairwise_output_folder = "pairwise_outputs"
process_folder = "partial_results"
final_folder = "final_results"


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
(output_tif_incl_folder, marineusepolygonnamelist_inkl_folder, marineusepolygonnamelist_exls_folder, pairwisescorepolygonnamelist_inkl_folder, pairwisescorepolygonnamelist_exls_folder) = calculatePotentialSynergiesWithExistingUsesRaster(marineUseInFocus, dictMarineUses, inputexcelsheet, inputfolder, final_folder, pairwise_output_folder, process_folder, addConflictingExistingMarineUseInteractionsIsTrue, synergy_with_existing_uses_raster_only_ocean_name, oceanrastername_with_path, lower_left_corner, dsc, spatial_ref, starttimetobeupdated)
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Potential synergy destinations with scores have been calculated, {}\n".format(printline))

starttimetobeupdated = resetTime(starttimetobeupdated)
populateCurrentMapDocument(output_tif_incl_folder, synergy_with_existing_uses_raster_only_ocean_name, marineusepolygonnamelist_inkl_folder, marineusepolygonnamelist_exls_folder, pairwisescorepolygonnamelist_inkl_folder, pairwisescorepolygonnamelist_exls_folder, new_marine_use_potentials_lyrfile, pairwise_lyrfile, final_folder, pairwise_output_folder)
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("If data exist, it has been added to current MXD document, {}\n".format(printline))
