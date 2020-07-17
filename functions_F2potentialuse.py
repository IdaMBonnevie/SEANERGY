# F2 FUNCTIONS FOR SEANERGY for the tool 'Find Synergy Potential Scores For New Marine Use' and the tool 'Find Synergy Potential Counts For New Marine Use'. 

# import modules: 
import arcpy
import numpy as np 
import pandas as pd
import functions_general as gf 


# functions for formula F2 (score or count): 
# calculate potential synergy areas for new unlocated marine use in focus - main F2 function 1 of 3:
def calculatePotentialSynergiesWithExistingUsesRaster(marineUseInFocus, dictMarineUses, matrixexcelfile, inputfoldername, final_folder, pairwise_output_folder, process_folder, addConflictingExistingMarineUseInteractionsIsTrue, synergy_with_existing_uses_raster_only_ocean_name, oceanrastername_with_path, lower_left_corner, dsc, spatial_ref, starttimetobeupdated, tooloption):
    # preset parameters: 
    dfdesc = pd.read_excel(matrixexcelfile)    
    listOfLongMarineUseNames = dictMarineUses.keys()
    if (tooloption == "scoresynergypotentialfornewmarineuse"):
        calculationtypepart1 = "pot_score_"
    elif (tooloption == "countsynergypotentialfornewmarineuse"):
        calculationtypepart1 = "pot_count_"
    if marineUseInFocus in listOfLongMarineUseNames:
        calculationtype = calculationtypepart1+dictMarineUses.get(marineUseInFocus)[:-4]+"_"
        inMarineUseRasterDict = True
    else: 
        calculationtypepart = marineUseInFocus.replace(" ","")
        if len(calculationtypepart) > 7:
            calculationtype = calculationtypepart1+marineUseInFocus[:7]+"_"
            marineusename = marineUseInFocus[:7]
        else: 
            calculationtype = calculationtypepart1+marineUseInFocus+"_"  
            marineusename = marineUseInFocus
        inMarineUseRasterDict = False 
    listOfExistingMarineUses = []
    marineusepolygonlist = []
    marineusepolygonnamelist = []
    pairwisepolygonlist = []
    pairwisepolygonnamelist = []
    firstposraster = True
    firstnegraster = True
    iterator1 = 0
    iterator2 = 1
    # make total potential score or count raster of potential synergy overlaps between existing marine uses and the chosen new marine use, as well as make individual marine use score or count polygons of marine uses with potential synergies with the chosen new marine use: 
    for column in listOfLongMarineUseNames: 
        # get score and create potential pairwise score raster -->
        # --> if the marine use in focus is in the marine use raster dictionary (if it does not already exist as raster it will not be in the marine use raster dictionary):
        if (inMarineUseRasterDict == True):
            inputrastername1 = dictMarineUses.get(column) #get raster for marine use 1 (could be the marine use in focus)
            while iterator2 in range((iterator1+1),len(listOfLongMarineUseNames)):
                # get score and matrixinput for the pairwise combination if -->
                # ---> condition: if the marine use in focus is either marine use 1 or marine use 2
                if ((marineUseInFocus == column) or (marineUseInFocus == listOfLongMarineUseNames[iterator2])): 
                    matrixinput_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongMarineUseNames[iterator2], column].values
                    if len(matrixinput_nparray) > 0:
                        matrixinput = matrixinput_nparray.item(0)
                        if len(str(matrixinput)) >= 4: 
                            if matrixinput[:1] == "-": 
                                specific_score = float(matrixinput[:5].replace(",",".")) #get the negative score
                            else: 
                                specific_score = float(matrixinput[:4].replace(",",".")) #get the positive score            
                            inputrastername2 = dictMarineUses.get(listOfLongMarineUseNames[iterator2]) #get raster for marine use 2 (could be the marine use in focus)
                            # get and convert the other marine use raster to a score raster for all the locations where the other marine use is present - then a pairwise potential synergy raster is created: 
                            if (marineUseInFocus == column):
                                (outras_array, overnull, marineusepolygonlist, marineusepolygonnamelist) = scoreToOneRaster(inputfoldername, inputrastername2, specific_score, lower_left_corner, dsc, spatial_ref, matrixinput, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype, tooloption)
                            elif (marineUseInFocus == listOfLongMarineUseNames[iterator2]):
                                (outras_array, overnull, marineusepolygonlist, marineusepolygonnamelist) = scoreToOneRaster(inputfoldername, inputrastername1, specific_score, lower_left_corner, dsc, spatial_ref, matrixinput, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype, tooloption)
                            # locations with negative scores should be noted down to be fixed as conflicts in the potential score output: 
                            if specific_score < 0: 
                                if firstnegraster == True:         
                                    if (tooloption == "scoresynergypotentialfornewmarineuse"):
                                        remove_area_array = outras_array < 0 # remove area with negative scores
                                    elif (tooloption == "countsynergypotentialfornewmarineuse"):
                                        remove_area_array = outras_array > 0 # remove area with positive count of negative scores
                                    firstnegraster = False
                                else: 
                                    specific_score_array = np.copy(outras_array)
                                    if (tooloption == "scoresynergypotentialfornewmarineuse"):
                                        remove_area_specific_array = specific_score_array < 0 # remove area with negative scores
                                    elif (tooloption == "countsynergypotentialfornewmarineuse"):
                                        remove_area_specific_array = specific_score_array > 0 # remove area with positive count of negative scores
                                    remove_area_array = (remove_area_array | remove_area_specific_array)
                            # the pairwise potential synergy raster is kept and accumulated if the score is positive: 
                            if specific_score > 0: 
                                if (marineUseInFocus == column):
                                    if overnull == True: 
                                        listOfExistingMarineUses.append(inputrastername2)
                                elif (marineUseInFocus == listOfLongMarineUseNames[iterator2]):
                                    if overnull == True: 
                                        listOfExistingMarineUses.append(inputrastername1)                                    
                                # all pairwise potential synergy rasters are accumulated in one array: 
                                if firstposraster == True:         
                                    cummulated_score_outras_array = outras_array
                                    firstposraster = False
                                else: 
                                    cummulated_score_outras_array += outras_array
                iterator2 += 1 #iterate through all rasters that are after raster1 (to iteratively be raster2)
        # get score and create potential pairwise score raster -->
        # --> if marine use in focuus is not in marine use raster dictionary (if it does not already exist as raster it will not be in the marine use raster dictionary) - 
        ## and the marine-use-raster-index of column is smaller than the marine-use-raster-index of the marine use in focus
        ### the pairwise score is found for the column and the marine-use-in-focus-as-row
        elif ((inMarineUseRasterDict == False) and (dfdesc.columns.tolist().index(column) < dfdesc.columns.tolist().index(marineUseInFocus))):
            inputrastername1 = dictMarineUses.get(column) #get raster for marine use 1 (could NOT be the marine use in focus)
            inputlongname1 = column
            inputrastername2 = marineusename #get raster for marine use 2 (it is defined to be the marine use in focus)
            inputlongname2 = marineUseInFocus
            # get score and matrixinput for the pairwise combination: 
            matrixinput_nparray = dfdesc.loc[dfdesc['Idcolumn'] == inputlongname2, inputlongname1].values
            if len(matrixinput_nparray) > 0:
                matrixinput = matrixinput_nparray.item(0)
                if len(str(matrixinput)) >= 4: 
                    if matrixinput[:1] == "-": 
                        specific_score = float(matrixinput[:5].replace(",",".")) #get the score
                    else: 
                        specific_score = float(matrixinput[:4].replace(",",".")) #get the score            
                    # get and convert the other marine use raster to a score raster for all the locations where the other marine use is present - then a pairwise potential synergy raster is created:
                    (outras_array, overnull, marineusepolygonlist, marineusepolygonnamelist) = scoreToOneRaster(inputfoldername, inputrastername1, specific_score, lower_left_corner, dsc, spatial_ref, matrixinput, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype, tooloption)
                    # locations with negative scores should be noted down to be fixed as conflicts in the potential score output: 
                    if specific_score < 0: 
                        if firstnegraster == True:         
                            if (tooloption == "scoresynergypotentialfornewmarineuse"):
                                remove_area_array = outras_array < 0 # remove area with negative scores
                            elif (tooloption == "countsynergypotentialfornewmarineuse"):
                                remove_area_array = outras_array > 0 # remove area with positive count of negative scores
                            firstnegraster = False
                        else: 
                            specific_score_array = np.copy(outras_array)
                            if (tooloption == "scoresynergypotentialfornewmarineuse"):
                                remove_area_specific_array = specific_score_array < 0 # remove area with negative scores
                            elif (tooloption == "countsynergypotentialfornewmarineuse"):
                                remove_area_specific_array = specific_score_array > 0 # remove area with positive count of negative scores
                            remove_area_array = (remove_area_array | remove_area_specific_array)
                    # the pairwise potential synergy raster is kept and accumulated if the score is positive: 
                    if specific_score > 0: 
                        if overnull == True: 
                            listOfExistingMarineUses.append(inputrastername1)                                    
                        # all pairwise potential synergy rasters are accumulated in one array: 
                        if firstposraster == True:         
                            cummulated_score_outras_array = outras_array
                            firstposraster = False
                        else: 
                            cummulated_score_outras_array += outras_array
        # get score and create potential pairwise score raster -->
        # --> if marine use in focus is not in marine use raster dictionary (if it does not already exist as raster it will not be in the marine use raster dictionary) -
        ## and the marine-use-raster-index of column is equal to or larger than the marine-use-raster-index of the marine use in focus
        ### the pairwise score is found iteratively for the marine-use-as-column and other-marine-uses-as-row -
        #### and then the loop breaks for the rest of the columns 
        elif (inMarineUseRasterDict == False):
            inputrastername1 = marineusename #get raster for marine use 1 (it is defined to be the marine use in focus)
            inputlongname1 = marineUseInFocus
            while iterator2 in range((iterator1+1),len(listOfLongMarineUseNames)):
                # get score and matrixinput for the pairwise combination:
                alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongMarineUseNames[iterator2], inputlongname1].values
                if len(alldesc_nparray) > 0:
                    alldesc = alldesc_nparray.item(0)
                    if len(str(alldesc)) >= 4: 
                        if alldesc[:1] == "-": 
                            spec_score = float(alldesc[:5].replace(",",".")) #get the score
                        else: 
                            spec_score = float(alldesc[:4].replace(",",".")) #get the score            
                        inputrastername2 = dictMarineUses.get(listOfLongMarineUseNames[iterator2]) #get raster for marine use 2 (could NOT be the marine use in focus)
                        # get and convert the other marine use raster to a score raster for all the locations where the other marine use is present - then a pairwise potential synergy raster is created:
                        (outras_array, overnull, marineusepolygonlist, marineusepolygonnamelist) = scoreToOneRaster(inputfoldername, inputrastername2, spec_score, lower_left_corner, dsc, spatial_ref, alldesc, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype, tooloption)
                        # locations with negative scores should be noted down to be fixed as conflicts in the potential score output: 
                        if spec_score < 0: 
                            if firstnegraster == True:         
                                if (tooloption == "scoresynergypotentialfornewmarineuse"):
                                    remove_area_array = outras_array < 0 # remove area with negative scores
                                elif (tooloption == "countsynergypotentialfornewmarineuse"):
                                    remove_area_array = outras_array > 0 # remove area with positive count of negative scores
                                firstnegraster = False
                            else: 
                                specific_score_array = np.copy(outras_array)
                                if (tooloption == "scoresynergypotentialfornewmarineuse"):
                                    remove_area_specific_array = specific_score_array < 0 # remove area with negative scores
                                elif (tooloption == "countsynergypotentialfornewmarineuse"):
                                    remove_area_specific_array = specific_score_array > 0 # remove area with positive count of negative scores
                                remove_area_array = (remove_area_array | remove_area_specific_array)
                        # the pairwise potential synergy raster is kept and accumulated if the score is positive: 
                        if spec_score > 0: 
                            if overnull == True: 
                                listOfExistingMarineUses.append(inputrastername2)
                            # all pairwise potential synergy rasters are accumulated in one array: 
                            if firstposraster == True:         
                                cummulated_score_outras_array = outras_array
                                firstposraster = False
                            else: 
                                cummulated_score_outras_array += outras_array
                iterator2 += 1 #iterate through all rasters that are after raster1 (to iteratively be raster2)
            break
        iterator1 += 1 #new raster1
        iterator2 = iterator1+1 #start again by iterating through rasters to be raster2 (now the number of following rasters has decreased by 1)
    # convert total synergy potential numpy array to total score raster with terrestrial/land area as NoData and remove conflict areas:
    ocean_array = arcpy.RasterToNumPyArray(oceanrastername_with_path)
    ocean_array = ocean_array.astype(float)
    ocean_array_land = ocean_array == 0
    np.place(cummulated_score_outras_array, remove_area_array, -1) #highlight areas where conflicts might exist as -1
    np.place(cummulated_score_outras_array, ocean_array_land, np.nan)   
    scoreRaster = arcpy.NumPyArrayToRaster(cummulated_score_outras_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    gf.createNewPath(final_folder)
    output_tif_incl_folder = final_folder+"\\"+synergy_with_existing_uses_raster_only_ocean_name
    scoreRaster.save(output_tif_incl_folder)
    arcpy.DefineProjection_management(output_tif_incl_folder, spatial_ref)
    # make pairwise conflicting marine use score or count polygons if any negative scores between existing marine uses exist (optional setting):    
    if addConflictingExistingMarineUseInteractionsIsTrue == "true":        
        if len(listOfExistingMarineUses) >= 2: # if existing marine uses are at least 2 in total they might interact
            raster1iterator = 0
            # loop through existing marine use rasters: 
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
                            # if the score between the two existing marine uses in the loop is negative, their conflict polygon should be created and added:  
                            if alldesc[:1] == "-": 
                                if (tooloption == "scoresynergypotentialfornewmarineuse"):
                                    spec_score = float(alldesc[:5].replace(",",".")) #get the score
                                    smallcalculationtype = "score_"
                                elif (tooloption == "countsynergypotentialfornewmarineuse"):
                                    spec_score = "scoreIsNotRelevantSinceItIsValueOneForCounting"
                                    smallcalculationtype = "count_" 
                                # a pairwise conflict polygon between existing marine uses is created (first created as raster, then turned into a polygon):
                                (pairwisepolygonlist, pairwisepolygonnamelist) = scoresToRasters2(inputfoldername, shortrastername1, shortrastername2, specific_score, lower_left_corner, dsc, spatial_ref, matrixinput, pairwise_output_folder, pairwisepolygonlist, pairwisepolygonnamelist, smallcalculationtype, tooloption)
                raster1iterator += 1
    # output total synergy potential raster, pairwise potential synergy polygons to be added to the map and their names, and if requested; pairwise conflicting marine use polygons:
    return (output_tif_incl_folder, marineusepolygonlist, marineusepolygonnamelist, pairwisepolygonlist, pairwisepolygonnamelist)

# convert pairwise rasters or individual marine use rasters to polygons and include matrix description as attribute data: 
def pairwiseOrIndividualRasterToPolygon(array_input, lower_left_corner, dsc, spatial_ref, output_folder, inputrastername1, inputrastername2, calculationtype, matrixinput, specific_score, polygonlist, polygonnamelist, tooloption):
    individual_or_pairwise_marine_use_array = np.copy(array_input)
    individual_or_pairwise_marine_use_array = individual_or_pairwise_marine_use_array.astype(int)
    individual_or_pairwise_marine_use_array[individual_or_pairwise_marine_use_array!=0.] = 1
    individualOrPairwiseScoreRaster = arcpy.NumPyArrayToRaster(individual_or_pairwise_marine_use_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    gf.createNewPath(output_folder)
    polygon_outputname = gf.returnRasterFilename2(inputrastername1, inputrastername2, calculationtype)
    marineuseoutput_shp_draft_incl_folder = output_folder+"\\"+polygon_outputname[:-4]+"_draft.shp"
    marineuseoutput_shp_draft_excl_folder = polygon_outputname[:-4]+"_draft.shp"
    marineuseoutput_shp_incl_folder = output_folder+"\\"+polygon_outputname[:-4]+".shp"
    marineuseoutput_shp_excl_folder = polygon_outputname[:-4]+".shp"
    arcpy.RasterToPolygon_conversion(individualOrPairwiseScoreRaster, marineuseoutput_shp_draft_incl_folder, "NO_SIMPLIFY","VALUE","MULTIPLE_OUTER_PART")             
    arcpy.MakeFeatureLayer_management(marineuseoutput_shp_draft_incl_folder, marineuseoutput_shp_draft_excl_folder[:-4], '"gridcode" = 1')
    arcpy.CopyFeatures_management(marineuseoutput_shp_draft_excl_folder[:-4], marineuseoutput_shp_incl_folder)
    arcpy.DefineProjection_management(marineuseoutput_shp_incl_folder, spatial_ref)
    gf.addField(marineuseoutput_shp_incl_folder, "TEXT", fieldname = "finalvalue", precision = "", decimals = "", field_length = 20)
    if (tooloption == "scoresynergypotentialfornewmarineuse"):
        gf.calculateField1(marineuseoutput_shp_incl_folder, "finalvalue", str(specific_score), expression_type="PYTHON")
    elif (tooloption == "countsynergypotentialfornewmarineuse"):
        gf.calculateField1(marineuseoutput_shp_incl_folder, "finalvalue", str(1), expression_type="PYTHON")
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
            gf.addField(marineuseoutput_shp_incl_folder, "TEXT", "full_desc"+str(fieldcount), precision = "", decimals = "", field_length = 254)
            gf.calculateField1(marineuseoutput_shp_incl_folder, "full_desc"+str(fieldcount), "'"+(str(matrixinput[matrixstart:matrixend]).replace("'",""))+"'", expression_type="PYTHON")
            matrixstart=matrixstart+254
            matrixend=matrixend+254
            if matrixend > len(matrixinput):
                matrixend = len(matrixinput)
    arcpy.DeleteField_management(marineuseoutput_shp_incl_folder, "Id")
    polygonlist.append(marineuseoutput_shp_incl_folder)
    polygonnamelist.append(marineuseoutput_shp_excl_folder)
    return (polygonlist, polygonnamelist)

# use only one existing marine use to convert it into a potential synergy raster with the marine use in focus - main F2 function 2 of 3:
def scoreToOneRaster(inputfoldername, inputrastername, specific_score, lower_left_corner, dsc, spatial_ref, matrixinput, process_folder, marineusepolygonlist, marineusepolygonnamelist, calculationtype, tooloption):
    #create individual marine use score raster
    inputname = inputfoldername+"\\"+inputrastername
    array_input = arcpy.RasterToNumPyArray(inputname)
    array_input = array_input.astype(float)
    if (tooloption == "scoresynergypotentialfornewmarineuse"):
        array_input[array_input+array_input!=2.] = 0.    
        array_input[array_input+array_input==2.] = specific_score
    overnull=False
    #create individual marine use polygon:
    if np.sum(array_input) > 0: 
        overnull=True
        (marineusepolygonlist, marineusepolygonnamelist) = pairwiseOrIndividualRasterToPolygon(array_input, lower_left_corner, dsc, spatial_ref, process_folder, inputrastername, inputrastername, calculationtype, matrixinput, specific_score, marineusepolygonlist, marineusepolygonnamelist, tooloption)
    return (array_input, overnull, marineusepolygonlist, marineusepolygonnamelist)

# convert two existing marine uses into a pairwise conflict raster and then afterwards into a polygon - main F2 function 3 of 3:
def scoresToRasters2(inputfoldername, inputrastername1, inputrastername2, specific_score, lower_left_corner, dsc, spatial_ref, matrixinput, pairwise_output_folder, pairwisemarineusepolygonlist, pairwisemarineusepolygonnamelist, calculationtype, tooloption):
    #create pairwise marine use score raster
    inputname1 = inputfoldername+"\\"+inputrastername1
    array_input1 = arcpy.RasterToNumPyArray(inputname1)
    if (tooloption == "scoresynergypotentialfornewmarineuse"): 
        array_input1 = array_input1.astype(float)
    inputname2 = inputfoldername+"\\"+inputrastername2
    array_input2 = arcpy.RasterToNumPyArray(inputname2)
    if (tooloption == "scoresynergypotentialfornewmarineuse"): 
        array_input2 = array_input2.astype(float)
        array_input1[array_input1+array_input2!=2.] = 0.    
        array_input1[array_input1+array_input2==2.] = specific_score
    elif (tooloption == "countsynergypotentialfornewmarineuse"):
        array_input1[array_input1+array_input2!=2] = 0    
        array_input1[array_input1+array_input2==2] = 1
    #create pairwise marine use polygon:
    if ((np.sum(array_input1) < 0) and (tooloption == "scoresynergypotentialfornewmarineuse")) or (
        (np.sum(array_input1) > 0) and (tooloption == "countsynergypotentialfornewmarineuse")): # should be below 0 if negative conflict scores and above 0 if postive counts of negative conflict scores 
        (pairwisemarineusepolygonlist, pairwisemarineusepolygonnamelist) = pairwiseOrIndividualRasterToPolygon(array_input1, lower_left_corner, dsc, spatial_ref, pairwise_output_folder, inputrastername1, inputrastername2, calculationtype, matrixinput, specific_score, pairwisemarineusepolygonlist, pairwisemarineusepolygonnamelist, tooloption)
    return (pairwisemarineusepolygonlist, pairwisemarineusepolygonnamelist)
