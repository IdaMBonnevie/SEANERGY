# GENERAL FUNCTIONS FOR SEANERGY     

# import modules: 
import arcpy
from collections import OrderedDict
from datetime import datetime
import functions_F1existinguses as f1 
import numpy as np 
import os
import pandas as pd
import random
import time


# general functions: 
#scoretool1 #counttool1 #scoretool2 #counttool2
def addField(outputpath, fieldtype, fieldname = "valuefield", precision = "", decimals = "", field_length = ""): 
    if fieldtype == "TEXT":
        arcpy.AddField_management(outputpath, fieldname, fieldtype, precision, decimals, field_length, "", "NULLABLE", "NON_REQUIRED", "")        
    else: 
        arcpy.AddField_management(outputpath, fieldname, fieldtype, precision, decimals, "", "", "NULLABLE", "NON_REQUIRED", "")

#scoretool1 #counttool1 #montecarlotool 
def addLayerToMxd1(mxd, df, inputname_inkl_folder, inputname_excl_folder, lyrfile, place, mode, inputfolder):
    if mode == "pairwise_polygon" or mode == "both_synergies_and_conflicts":
        rlayer1 = arcpy.mapping.Layer(os.path.join(os.path.dirname(__file__),inputfolder,inputname_excl_folder))
    elif mode == "mainmap" or mode == "montecarlo": 
        result = arcpy.MakeRasterLayer_management(inputname_inkl_folder, inputname_excl_folder[:-4]) 
        rlayer1 = result.getOutput(0)
    if mode == "both_synergies_and_conflicts": 
        rlayer1.transparency = 0 #here it is possible to set transparency of synergy-and-conflict-at-once.shp layer
    if lyrfile == "NotExisting": ##
        lyrfile = "NotExisting"
    else: 
        arcpy.ApplySymbologyFromLayer_management(rlayer1, lyrfile)
        if mode == "pairwise_polygon": 
            if rlayer1.symbologyType == "UNIQUE_VALUES":
                rlayer1.symbology.addAllValues()
    arcpy.mapping.AddLayer(df, rlayer1, place)
    del mxd, df

#scoretool2 #counttool2    
def addLayerToMxd2(mxd, df, inputname_inkl_folder, inputname_excl_folder, lyrfile, place, mode, inputfolder):
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

#scoretool1 #counttool1 #scoretool2 #counttool2
def calculateField1(outputpath, valuefield, valueToInput, expression_type="VB"): 
    arcpy.CalculateField_management(outputpath, valuefield, valueToInput, expression_type, "")
 
#scoretool1 #counttool1 #scoretool2 #counttool2 #montecarlotool
def createNewPath(outputpath):
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

#montecarlotool
def createRaster(iteration_folder, iteration_outputname, extra_part_of_outputname, raster, spatial_ref, list_to_append_raster_to, list_to_append_rastername_to):
    createNewPath(iteration_folder)
    raster_tif_incl_folder = iteration_folder+"\\"+iteration_outputname[:-4]+extra_part_of_outputname+".tif"
    raster.save(raster_tif_incl_folder)
    arcpy.DefineProjection_management(raster_tif_incl_folder, spatial_ref)
    list_to_append_raster_to.append(raster_tif_incl_folder)
    list_to_append_rastername_to.append(iteration_outputname[:-4]+extra_part_of_outputname+".tif")
    return (list_to_append_raster_to, list_to_append_rastername_to)

#scoretool1 #counttool1 #scoretool2 #counttool2 #montecarlotool
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

#scoretool1 #counttool1
def getNumbOfAllPolygonElementsFromOrderedList(listpairwiserastername, listpairwisepolygon, listpairwisepolygonname, pairwise_output_folder, intervalForRaster, tooloption):
    for i in range(len(listpairwiserastername)):
        if i % intervalForRaster == 0:
            if intervalForRaster == 3: 
                (listpairwisepolygon, listpairwisepolygonname) = f1.pairwiseRasterToPolygon(listpairwiserastername[i], listpairwiserastername[i+1], listpairwiserastername[i+2], pairwise_output_folder, listpairwisepolygon, listpairwisepolygonname, tooloption)
            elif intervalForRaster == 2:
                (listpairwisepolygon, listpairwisepolygonname) = f1.pairwiseRasterToPolygon(listpairwiserastername[i], "no_score", listpairwiserastername[i+1], pairwise_output_folder, listpairwisepolygon, listpairwisepolygonname, tooloption)
    return (listpairwisepolygon, listpairwisepolygonname)

#scoretool1 #counttool1
# convert pairwise rasters to polygons for the numbOfSome highest/lowest pairwise score polygons requested:  
def getNumbOfSomePolygonElementsFromOrderedDict(dictpairwisescorerastername, numbOfSome, listpairwisepolygon, listpairwisepolygonname, pairwise_output_folder, intervalForRaster, tooloption):
    dictiterator=0
    for sum_of_all_scores, raster_element_list in dictpairwisescorerastername.items():
        if dictiterator >= numbOfSome: 
            break
        for i in range(len(raster_element_list)/intervalForRaster):
            if i % intervalForRaster == 0: 
                if intervalForRaster == 3:             
                    (listpairwisepolygon, listpairwisepolygonname) = f1.pairwiseRasterToPolygon(raster_element_list[i], raster_element_list[i+1], raster_element_list[i+2], pairwise_output_folder, listpairwisepolygon, listpairwisepolygonname, tooloption)
                elif intervalForRaster == 2:
                    (listpairwisepolygon, listpairwisepolygonname) = f1.pairwiseRasterToPolygon(raster_element_list[i], "no_score", raster_element_list[i+1], pairwise_output_folder, listpairwisepolygon, listpairwisepolygonname, tooloption)
                dictiterator+=1      
    return (listpairwisepolygon, listpairwisepolygonname)

#montecarlotool
def getRandomValueBetween0And1(): 
    new_factor = random.random()
    while (new_factor==0) or (new_factor==1):
        new_factor = random.random()
    return new_factor

#scoretool2 #counttool2
def getTifFilesInFolder(inputfolder):
    inputfileList = os.listdir(inputfolder)
    finalinputfileList = []
    for input in inputfileList: 
    	if input[-4:] == ".tif":
    		finalinputfileList.append(input)
    return finalinputfileList

#scoretool1 #counttool1
def populateCurrentMapDocument1(outputrastername_tif_incl_folder, outputrastername_tif_excl_folder, listpairwisepolygon, listpairwisepolygonname, output_shp_incl_folder, output_shp_excl_folder, finaloutputlyrfile, pairwise_lyrfile, conflict_and_synergy_lyrfile, final_folder, pairwise_output_folder, includeSynergyAndConflictAtOnceAreaIsTrue):
    try: 
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        addLayerToMxd1(mxd, df, outputrastername_tif_incl_folder, outputrastername_tif_excl_folder, finaloutputlyrfile, 'TOP', "mainmap", final_folder)
        if includeSynergyAndConflictAtOnceAreaIsTrue == "true":        
            addLayerToMxd1(mxd, df, output_shp_incl_folder, output_shp_excl_folder, conflict_and_synergy_lyrfile, 'BOTTOM', "both_synergies_and_conflicts", final_folder)            
        for pairwisepolygon, pairwisepolygonname in zip(listpairwisepolygon, listpairwisepolygonname):
            addLayerToMxd1(mxd, df, pairwisepolygon, pairwisepolygonname, pairwise_lyrfile, 'BOTTOM', "pairwise_polygon", pairwise_output_folder) #raster parameter does not matter when not mainmap
    except: 
        arcpy.AddMessage("ERROR: You cannot have opened more than one MXD document in the same session for this tool to work")

#scoretool2 #counttool2
def populateCurrentMapDocument2(rastername, output_tif_excl_folder, marineusepolygonnamelist_inkl_folder, marineusepolygonnamelist_exls_folder, pairwisescorepolygonnamelist_inkl_folder, pairwisescorepolygonnamelist_exls_folder, lyrfile1, lyrfile2, inputfolder1, inputfolder2):
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    addLayerToMxd2(mxd, df, rastername, output_tif_excl_folder, lyrfile1, 'TOP', "mainmap", inputfolder1)
    for marineusepolygonname_inkl_folder, marineusepolygonname_exls_folder in zip(marineusepolygonnamelist_inkl_folder, marineusepolygonnamelist_exls_folder): 
        addLayerToMxd2(mxd, df, marineusepolygonname_inkl_folder, marineusepolygonname_exls_folder, lyrfile2, 'BOTTOM', "marine_use_individual", inputfolder2) #raster parameter does not matter when not mainmap
    for pairwisepolygonname_inkl_folder, pairwisepolygonname_exls_folder in zip(pairwisescorepolygonnamelist_inkl_folder, pairwisescorepolygonnamelist_exls_folder): 
        addLayerToMxd2(mxd, df, pairwisepolygonname_inkl_folder, pairwisepolygonname_exls_folder, lyrfile2, 'BOTTOM', "marine_use_pairwise", inputfolder2) #raster parameter does not matter when not mainmap

#montecarlotool
def populateCurrentMapDocument3(output_tif_incl_folder_list, outputnamelist, lyrfile, iteration_folder):
    try: 
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        for raster, outputname in zip(output_tif_incl_folder_list, outputnamelist):
            addLayerToMxd1(mxd, df, raster, outputname, lyrfile, 'BOTTOM', "montecarlo", iteration_folder)
    except: 
        arcpy.AddMessage("ERROR: You cannot have opened more than one MXD document in the same session for this tool to work")

#scoretool1 #counttool1 #scoretool2 #counttool2 #lookuptool #montecarlotool
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

#scoretool1 #counttool1 #scoretool2 #counttool2 #lookuptool #montecarlotool
def resetTime(starttimetobeupdated):
    starttimetobeupdated = time.time()
    dateTimeObj = datetime.now()
    timestamp = str(dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)
    print("starting process, timestamp:{}".format(timestamp))
    return (starttimetobeupdated) 

#scoretool1 #counttool1
def returnRasterFilename1(inputrastername1, inputrastername2, calculationtype):
    if len(inputrastername1[:-4]) >= 7 and len(inputrastername2[:-4]) >= 7:  
        finalrastername = calculationtype+inputrastername1[:-4][:7]+"_"+inputrastername2[:-4][:7]+".tif"   
    elif len(inputrastername1) >= 7: 
        finalrastername = calculationtype+inputrastername1[:-4][:7]+"_"+inputrastername2[:-4]+".tif"   
    elif len(inputrastername2) >= 7: 
        finalrastername = calculationtype+inputrastername1[:-4]+"_"+inputrastername2[:-4][:7]+".tif"   
    else: 
        finalrastername = calculationtype+inputrastername1[:-4]+"_"+inputrastername2[:-4]+".tif"    
    return finalrastername                       

#scoretool2 #counttool2
def returnRasterFilename2(inputrastername1, inputrastername2, calculationtype):
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

#scoretool1 #counttool1
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
        addField(output_shp_incl_folder, "TEXT", fieldname = "finalvalue", precision = "", decimals = "", field_length = 20)
        calculateField1(output_shp_incl_folder, "finalvalue", str(1), expression_type="PYTHON")
        arcpy.DeleteField_management(output_shp_incl_folder, "Id")
        return (output_shp_incl_folder, output_shp_excl_folder)
    else: 
        return ("no_output", "no_output")

#scoretool1 #counttool1
def updateScoreCellCount(score_outras_array, basic_array, tooloption):
    positive_to_update = score_outras_array > 0    
    np.place(basic_array, positive_to_update, 1) #1 is to count where there is a score
    if (tooloption == "producescoremap") or (tooloption == "montecarlo"):
        negative_to_update = score_outras_array < 0    
        np.place(basic_array, negative_to_update, 1) #1 is to count where there is a score
    return basic_array

#scoretool1 #counttool1
def updateSynergyAndConflictInCellKnowledge(score_outras_array, synergies_and_or_conflicts_array, specific_score):
    array_can_be_updated = synergies_and_or_conflicts_array == 0 # where array has no values 
    if specific_score > 0:
        synergies_specific_instance_array = score_outras_array > 0    
        np.place(synergies_and_or_conflicts_array, synergies_specific_instance_array & array_can_be_updated, 2) #2 is code for synergies
        conflicts_array = synergies_and_or_conflicts_array == 1 #1 is code for conflicts
        np.place(synergies_and_or_conflicts_array, synergies_specific_instance_array & conflicts_array, 3) #3 is code for both conflicts and synergies
    if specific_score < 0:
        conflicts_specific_instance_array = score_outras_array < 0
        np.place(synergies_and_or_conflicts_array, conflicts_specific_instance_array & array_can_be_updated, 1) #1 is code for conflicts    
        synergies_array = synergies_and_or_conflicts_array == 2 #2 is code for synergies
        np.place(synergies_and_or_conflicts_array, conflicts_specific_instance_array & synergies_array, 3) #3 is code for both conflicts and synergies
    return synergies_and_or_conflicts_array

#scoretool2 #counttool2
def valuesToOneInRaster(inputraster, outputname):
    outras = arcpy.sa.Int(arcpy.sa.Con(((inputraster > 0) | (inputraster < 0)),1,0))
    outras.save(os.path.join(os.path.dirname(__file__),outputname))
    return outras
