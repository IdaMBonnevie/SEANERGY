# F1 FUNCTIONS FOR SEANERGY for the tool 'Calculate Score Map' and the tool 'Calculate Count Map'. 
    
# import modules: 
import arcpy
from collections import OrderedDict
import numpy as np 
import os
import pandas as pd
import functions_general as gf 


# functions for formula F1 (score or count): 
def addScoreToDictPerMarineUseInMatrix(columnnumb, column, dicttable1, specific_score_or_count, listOfLongMarineUseNames, iterator2):
    dicttable1[column][columnnumb] = dicttable1[column][columnnumb]+specific_score_or_count                    
    dicttable1[listOfLongMarineUseNames[iterator2]][columnnumb] = dicttable1[listOfLongMarineUseNames[iterator2]][columnnumb]+specific_score_or_count

# calculate pairwise and total score rasters - main F1 function 1 of 2
def calculatePairwiseAndTotalRasters(dictMarineUses, matrixexcelfile, scoretypeToFocusOn, inputfoldernamewithpath, pairwise_output_folder, finalfoldername, tableOption1IsChecked, table1name, tableOption2IsChecked, table2name, tableOption3IsChecked, table3name, somePolygonsIsTrue, numbOfSome, onlyOneMarineUseInFocusIsTrue, marineUseInFocus, includeSynergyAndConflictAtOnceAreaIsTrue, lower_left_corner, dsc, spatial_ref, finaloutputname_only_covering_ocean, oceanrastername_with_path, calculationtype, countChoice, chosen_category, chosen_category_score, attribute_excelsheet, tooloption):
    # import ocean array: 
    ocean_array = arcpy.RasterToNumPyArray(oceanrastername_with_path)
    ocean_array = ocean_array.astype(float)
    # table 2 inputs:
    if (tooloption == "producecountmap") and (tableOption2IsChecked == "true"): 
        ocean_cell_number = np.count_nonzero(ocean_array)
    # preset parameters: 
    dfdesc = pd.read_excel(matrixexcelfile)    
    listOfLongMarineUseNames = dictMarineUses.keys()
    listpairwiserastername = []
    listpairwisepolygon = []
    listpairwisepolygonname = []
    dictpairwiserastername = {}
    dicttable1 = {}
    dicttable2 = {}
    dftable3 = "false" # false as default but might change
    if (tooloption == "producecountmap"):
        synergies_and_or_conflicts_array = "false" # false as default but might change
    for longname_marine_use in listOfLongMarineUseNames: 
        # table 1 inputs:
        if tableOption1IsChecked == "true":
            if (scoretypeToFocusOn == "all"):
                if (tooloption == "producescoremap"):
                    dicttable1[longname_marine_use] = [0]*4 
                elif (tooloption == "producecountmap"): 
                    dicttable1[longname_marine_use] = [0]*3     
            elif scoretypeToFocusOn == "positive":
                if (tooloption == "producescoremap"):
                    dicttable1[longname_marine_use] = [0]*2 
                elif (tooloption == "producecountmap"): 
                    dicttable1[longname_marine_use] = [0]                 
            elif scoretypeToFocusOn == "negative":
                if (tooloption == "producescoremap"):
                    dicttable1[longname_marine_use] = [0]*2 
                elif (tooloption == "producecountmap"): 
                    dicttable1[longname_marine_use] = [0]              
        # table 2 inputs:
        if tableOption2IsChecked == "true":         
            dicttable2[longname_marine_use]=[0]*7
            if (tooloption == "producescoremap"):
                dicttable2[longname_marine_use][3]=np.zeros_like(ocean_array, dtype=bool)
            elif (tooloption == "producecountmap"):
                dicttable2[longname_marine_use][1] = ocean_cell_number
                dicttable2[longname_marine_use][5]=np.zeros_like(ocean_array, dtype=bool)
    # table 3 inputs:
    if tableOption3IsChecked == "true":
        dftable3 = pd.DataFrame(columns=listOfLongMarineUseNames,index=listOfLongMarineUseNames)
        dftable3.index.name = 'Idcolumn'
        dftable3 = dftable3.reset_index()        
    # preset parameters:
    firstraster = True
    firstsynergyandconflictarray = True 
    firstbasicarray = True 
    iterator1 = 0
    iterator2 = 1
    # main code: create total scores or total counts:  
    for column in listOfLongMarineUseNames: 
        inputrastername1 = dictMarineUses.get(column) 
        while iterator2 in range((iterator1+1),len(listOfLongMarineUseNames)):       
            inputrastername2 = dictMarineUses.get(listOfLongMarineUseNames[iterator2]) #get raster for marine use 2
            # make pairwise rasters: set score=0 if score is never needed and get matrixinput:
            if (tooloption == "producecountmap") and (scoretypeToFocusOn == "all") and ((countChoice == "count all") or (countChoice == "count all combinations with a specific marine use")) and (tableOption1IsChecked == "false") and (includeSynergyAndConflictAtOnceAreaIsTrue == "false"):
                specific_score = 0 
                # set matrixinput = '' if no pairwise polygons should be created and added: 
                if ((somePolygonsIsTrue == "true") and (numbOfSome == 0)): 
                    matrixinput = ''
                else: 
                    # get matrixinput if pairwise polygons should be created and added:
                    try: 
                        matrixinput_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongMarineUseNames[iterator2], column].values
                        matrixinput = str(matrixinput_nparray.item(0))
                    # set matrixinput = '' if no description can be found in matrix: 
                    except: 
                        matrixinput = 'nan'
            # make pairwise rasters: get score if score is needed and get matrixinput:
            else: 
                # get matrixinput:
                matrixinput_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongMarineUseNames[iterator2], column].values
                if len(matrixinput_nparray) > 0:
                    matrixinput = matrixinput_nparray.item(0)
                    # get score if it exists:
                    if (len(str(matrixinput)) >= 4):                                                 
                        if str(matrixinput)[:1] == "-": 
                            specific_score = float(matrixinput[:5].replace(",",".")) #get the score
                        else: 
                            specific_score = float(matrixinput[:4].replace(",",".")) #get the score 
                    # if score do not exist, score is set to 0:
                    else: 
                        specific_score = 0
                else: 
                    specific_score = 0
           # make pairwise rasters: get spatial and temporal attributes if that is needed for the count type:
            if (tooloption == "producecountmap"):                 
                if ((countChoice == "count vertically different overlaps") or (countChoice == "count vertically same overlaps") or (countChoice == "count pairwise overlaps where both marine uses are mobile")):
                    if attribute_excelsheet == "false": 
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
            # make marine use pairwise rasters: 
            if ((tooloption == "producescoremap") and (len(str(matrixinput)) >= 4)) or (tooloption == "producecountmap"):
                inputmarineuselongname1 = column
                inputmarineuselongname2 = listOfLongMarineUseNames[iterator2]
                # make pairwise score rasters for all, synergies (positive), or conflicts (negative) --->:
                if (scoretypeToFocusOn == "all") or ((scoretypeToFocusOn == "positive") and (specific_score > 0)) or ((scoretypeToFocusOn == "negative") and (specific_score < 0)):
                    # ---> for specified conditions: 
                    if ((onlyOneMarineUseInFocusIsTrue == "false") and (tooloption == "producescoremap")) or (
                        (onlyOneMarineUseInFocusIsTrue == "true") and (marineUseInFocus == "false") and (tooloption == "producescoremap")) or (
                        (onlyOneMarineUseInFocusIsTrue == "true") and ((column == marineUseInFocus) or (listOfLongMarineUseNames[iterator2] == marineUseInFocus)) and (tooloption == "producescoremap")) or (
                        (countChoice == "count all") and (tooloption == "producecountmap")) or (
                        (countChoice == "count all combinations with a specific marine use") and ((marineUseInFocus == listOfLongMarineUseNames[iterator2]) or (marineUseInFocus == column)) and (tooloption == "producecountmap")) or (
                        (countChoice == "count combinations with a specific marine use where synergy-conflict inputs exist") and ((specific_score > 0) or (specific_score < 0)) and ((marineUseInFocus == listOfLongMarineUseNames[iterator2]) or (marineUseInFocus == column)) and (tooloption == "producecountmap")) or (
                        (countChoice == "count combinations where synergy-conflict inputs exist") and ((specific_score > 0) or (specific_score < 0)) and (tooloption == "producecountmap")) or (
                        (countChoice == "count combinations for a specific conflict-synergy category") and ((specific_score > 0) or (specific_score < 0)) and (specific_score == float(chosen_category_score)) and (tooloption == "producecountmap")) or (
                        (countChoice == "count multiuse-options mentioned in the MUSES project") and ('MUSES' in str(matrixinput)) and ((specific_score > 0) or (specific_score < 0)) and (tooloption == "producecountmap")) or (
                        (countChoice == "count vertically different overlaps") and (notActualOverlapping == "true") and ((specific_score > 0) or (specific_score < 0)) and (tooloption == "producecountmap")) or (
                        (countChoice == "count vertically same overlaps") and (notActualOverlapping == "false") and ((specific_score > 0) or (specific_score < 0)) and (tooloption == "producecountmap")) or (
                        (countChoice == "count pairwise overlaps where both marine uses are mobile") and (bothTemporal == "true") and ((specific_score > 0) or (specific_score < 0)) and (tooloption == "producecountmap")):                
                        (outras_array, array_pairwise_score, dicttable2, dftable3, dictpairwiserastername, listpairwiserastername) = scoresToRasters1(inputfoldernamewithpath, inputrastername1, inputrastername2, specific_score, lower_left_corner, dsc, matrixinput, pairwise_output_folder, dictpairwiserastername, calculationtype, tableOption2IsChecked, dicttable2, inputmarineuselongname1, inputmarineuselongname2, tableOption3IsChecked, dftable3, "true", listpairwiserastername, somePolygonsIsTrue, numbOfSome, spatial_ref, includeSynergyAndConflictAtOnceAreaIsTrue, tooloption)
                        if firstraster == True:         
                            cummulated_score_outras_array = outras_array # set total score raster = first pairwise score raster to start accumulating scores
                            firstraster = False
                            # make synergy-and-conflict-at-once area polygon - part 1:
                            if (includeSynergyAndConflictAtOnceAreaIsTrue == "true") and (firstsynergyandconflictarray == True):
                                if (tooloption == "producescoremap"):                               
                                    synergies_and_or_conflicts_array = np.copy(outras_array)
                                elif (tooloption == "producecountmap"):
                                    synergies_and_or_conflicts_array = np.copy(array_pairwise_score)
                                synergies_and_or_conflicts_array[synergies_and_or_conflicts_array>0.] = 2 #2 is code for synergies
                                synergies_and_or_conflicts_array[synergies_and_or_conflicts_array<0.] = 1 #1 is code for conflicts
                                synergies_and_or_conflicts_array = synergies_and_or_conflicts_array.astype(int)
                                firstsynergyandconflictarray = False
                            # make basic raster with values=1 for conflict-synergy extent - part 1: 
                            elif (firstbasicarray == True):
                                if (tooloption == "producescoremap"):
                                    cells_with_score_array = np.copy(outras_array)
                                    cells_with_score_array[cells_with_score_array>0.] = 1 #1 is to count cells with scores
                                    cells_with_score_array[cells_with_score_array<0.] = 1 #1 is to count cells with scores
                                elif (tooloption == "producecountmap"):
                                    cells_with_score_array = np.copy(outras_array)
                                cells_with_score_array = cells_with_score_array.astype(int)    
                                firstbasicarray = False
                        else: 
                            cummulated_score_outras_array += outras_array # update total score raster iteratively as the pairwise score rasters are created
                            # make synergy-and-conflict-at-once area polygon - part 2:
                            if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
                                if (tooloption == "producescoremap"):
                                    synergies_and_or_conflicts_array = gf.updateSynergyAndConflictInCellKnowledge(outras_array, synergies_and_or_conflicts_array, specific_score)                                    
                                elif (tooloption == "producecountmap"):
                                    synergies_and_or_conflicts_array = gf.updateSynergyAndConflictInCellKnowledge(array_pairwise_score, synergies_and_or_conflicts_array, specific_score)                                    
                            # make basic raster with values=1 for conflict-synergy extent - part 2: 
                            else: 
                                cells_with_score_array = gf.updateScoreCellCount(outras_array, cells_with_score_array, tooloption)
                    # table 1 inputs:
                    if (tableOption1IsChecked == "true"):
                        if ((scoretypeToFocusOn == "all") and (specific_score > 0) and (tooloption == "producescoremap")) or (
                            (scoretypeToFocusOn == "positive") and (specific_score > 0) and (tooloption == "producescoremap"))  or (
                            (scoretypeToFocusOn == "negative") and (specific_score < 0) and (tooloption == "producescoremap")):
                            addScoreToDictPerMarineUseInMatrix(0, column, dicttable1, specific_score, listOfLongMarineUseNames, iterator2)
                            addScoreToDictPerMarineUseInMatrix(1, column, dicttable1, 1, listOfLongMarineUseNames, iterator2)                            
                        elif ((scoretypeToFocusOn == "all") and (specific_score < 0) and (tooloption == "producescoremap")):
                            addScoreToDictPerMarineUseInMatrix(2, column, dicttable1, specific_score, listOfLongMarineUseNames, iterator2)
                            addScoreToDictPerMarineUseInMatrix(3, column, dicttable1, 1, listOfLongMarineUseNames, iterator2)
                        elif (tooloption == "producecountmap"):
                            addScoreToDictPerMarineUseInMatrix(0, column, dicttable1, 1, listOfLongMarineUseNames, iterator2)
                            if (scoretypeToFocusOn == "all") and (specific_score > 0):
                                addScoreToDictPerMarineUseInMatrix(1, column, dicttable1, 1, listOfLongMarineUseNames, iterator2)
                            elif (scoretypeToFocusOn == "all") and (specific_score < 0):
                                addScoreToDictPerMarineUseInMatrix(2, column, dicttable1, 1, listOfLongMarineUseNames, iterator2)
                if ((specific_score > 0) and (scoretypeToFocusOn == "negative")) or ((specific_score < 0) and (scoretypeToFocusOn == "positive")):
                    (outras_array, array_pairwise_score, dicttable2, dftable3, dictpairwiserastername, listpairwiserastername) = scoresToRasters1(inputfoldernamewithpath, inputrastername1, inputrastername2, specific_score, lower_left_corner, dsc, matrixinput, pairwise_output_folder, dictpairwiserastername, calculationtype, tableOption2IsChecked, dicttable2, inputmarineuselongname1, inputmarineuselongname2, tableOption3IsChecked, dftable3, "false", listpairwiserastername, somePolygonsIsTrue, numbOfSome, spatial_ref, includeSynergyAndConflictAtOnceAreaIsTrue, tooloption)
                    # make synergy-and-conflict-at-once area polygon - part 3:
                    if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
                        if (firstsynergyandconflictarray == True):
                            if (tooloption == "producescoremap"):
                                synergies_and_or_conflicts_array = np.copy(outras_array)
                            elif (tooloption == "producecountmap"):
                                synergies_and_or_conflicts_array = np.copy(array_pairwise_score)
                            if ((specific_score > 0) and (scoretypeToFocusOn == "negative")): 
                                synergies_and_or_conflicts_array[synergies_and_or_conflicts_array>0.] = 2 #2 is code for synergies
                            elif ((specific_score < 0) and (scoretypeToFocusOn == "positive")):
                                synergies_and_or_conflicts_array[synergies_and_or_conflicts_array<0.] = 1 #1 is code for conflicts                           
                            synergies_and_or_conflicts_array = synergies_and_or_conflicts_array.astype(int)
                            firstsynergyandconflictarray = False
                        else: 
                            if (tooloption == "producescoremap"):
                                synergies_and_or_conflicts_array = gf.updateSynergyAndConflictInCellKnowledge(outras_array, synergies_and_or_conflicts_array, specific_score)
                            elif (tooloption == "producecountmap"):
                                synergies_and_or_conflicts_array = gf.updateSynergyAndConflictInCellKnowledge(array_pairwise_score, synergies_and_or_conflicts_array, specific_score)
            iterator2 += 1 #iterate through all rasters that are after raster1 (to iteratively be raster2)
        iterator1 += 1 #new raster1
        iterator2 = iterator1+1 #start again by iterating through rasters to be raster2 (now the number of following rasters has decreased by 1)
    # make synergy-and-conflict-at-once area polygon - part 4:
    if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):
        cells_with_no_output = synergies_and_or_conflicts_array == 0
    # make basic raster with values=1 for conflict-synergy extent - part 4:
    else: 
        cells_with_no_output = cells_with_score_array == 0
    # convert total score numpy array to total score raster with terrestrial/land area as NoData:
    ocean_array_land = ocean_array == 0    
    np.place(cummulated_score_outras_array, ocean_array_land & cells_with_no_output, np.nan)
    scoreRaster = arcpy.NumPyArrayToRaster(cummulated_score_outras_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    gf.createNewPath(finalfoldername)
    output_tif_incl_folder = finalfoldername+"\\"+finaloutputname_only_covering_ocean
    scoreRaster.save(output_tif_incl_folder)
    arcpy.DefineProjection_management(output_tif_incl_folder, spatial_ref)
    # table 1 inputs:
    if tableOption1IsChecked == "true":
        forTable1getTotalMatrixSumCountPerMarineUse(dicttable1, scoretypeToFocusOn, finalfoldername, table1name, tooloption)
    # table 2 inputs:
    if tableOption2IsChecked == "true":
        forTable2getTotalMapSumCountAndAveragePerMarineUse(listOfLongMarineUseNames, dicttable2, finalfoldername, scoretypeToFocusOn, table2name, countChoice, tooloption)
    # table 3 inputs:
    if tableOption3IsChecked == "true":
        forTable3getTotalMapSumPerPairwiseCombination(finalfoldername, dftable3, table3name)
    # if is chosen to only add pairwise polygons to map with highest and lowest scores:
    if (tableOption3IsChecked == "true") and (somePolygonsIsTrue == "true") and (numbOfSome != "all") and (numbOfSome != 0) and (tooloption == "producescoremap"): 
        # add numbOfSome lowest negative pairwise score polygons - conflicst first:
        if (scoretypeToFocusOn == "all") or (scoretypeToFocusOn == "negative"):  
            dictpairwiserastername_new = OrderedDict(sorted(dictpairwiserastername.items()))
        # add numbOfSome highest positive pairwise score polygons - synergies first:
        if (scoretypeToFocusOn == "all") or (scoretypeToFocusOn == "positive"):
            dictpairwiserastername_new = OrderedDict(sorted(dictpairwiserastername.items(), reverse=True))
        (listpairwisepolygon, listpairwisepolygonname) = gf.getNumbOfSomePolygonElementsFromOrderedDict(dictpairwiserastername_new, numbOfSome, listpairwisepolygon, listpairwisepolygonname, pairwise_output_folder, 3, tooloption)        
    if (tableOption3IsChecked == "true") and (somePolygonsIsTrue == "true") and (numbOfSome != "all") and (tooloption == "producecountmap"):
        dictpairwiserastername_new = OrderedDict(sorted(dictpairwiserastername.items(), reverse=True))
        (listpairwisepolygon, listpairwisepolygonname) = gf.getNumbOfSomePolygonElementsFromOrderedDict(dictpairwiserastername_new, numbOfSome, listpairwisepolygon, listpairwisepolygonname, pairwise_output_folder, 2, tooloption)
    # add all pairwise score polygons to map (default setting unless numbOfSome is set) 
    elif (numbOfSome != 0) and (tooloption == "producescoremap"): 
        (listpairwisepolygon, listpairwisepolygonname) = gf.getNumbOfAllPolygonElementsFromOrderedList(listpairwiserastername, listpairwisepolygon, listpairwisepolygonname, pairwise_output_folder, 3, tooloption)
    elif (numbOfSome != 0) and (tooloption == "producecountmap"): 
        (listpairwisepolygon, listpairwisepolygonname) = gf.getNumbOfAllPolygonElementsFromOrderedList(listpairwiserastername, listpairwisepolygon, listpairwisepolygonname, pairwise_output_folder, 2, tooloption)
    # output total score raster, pairwise polygons to be added to the map and their names, and synergies-and-conflicts-at-once-array if requested:
    if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"): 
        return (output_tif_incl_folder, listpairwisepolygon, listpairwisepolygonname, synergies_and_or_conflicts_array)
    else:
        return (output_tif_incl_folder, listpairwisepolygon, listpairwisepolygonname, "redundant") 

# table1 main function: 
def forTable1getTotalMatrixSumCountPerMarineUse(dicttable1, scoretypeToFocusOn, finalfoldername, table1name, tooloption):
    dftable1 = pd.DataFrame.from_dict(dicttable1, orient='index')        
    if (scoretypeToFocusOn == "all") and (tooloption == "producescoremap"):
        columnA = "Sum of inputted synergy scores"
        columnB = "Count of inputted synergy scores"
        columnC = "Sum of inputted conflict scores"
        columnD = "Count of inputted conflict scores"
        dftable1.columns = [columnA, columnB, columnC, columnD] 
    elif (scoretypeToFocusOn == "all") and (tooloption == "producecountmap"):        
        columnA = "Count of all combinations including empty outputs"
        columnB = "Count of inputted synergy scores"
        columnC = "Count of inputted conflict scores"
        dftable1.columns = [columnA, columnB, columnC]        
    elif (scoretypeToFocusOn == "positive") and (tooloption == "producescoremap"):
        columnA = "Sum of inputted synergy scores"
        columnB = "Count of inputted synergy scores"
        dftable1.columns = [columnA, columnB] 
    elif (scoretypeToFocusOn == "positive") and (tooloption == "producecountmap"):
        columnA = "Count of inputted synergy scores"
        dftable1.columns = [columnA] 
    elif (scoretypeToFocusOn == "negative") and (tooloption == "producescoremap"):
        columnA = "Sum of inputted conflict scores"
        columnB = "Count of inputted conflict scores"
        dftable1.columns = [columnA, columnB] 
    elif (scoretypeToFocusOn == "negative") and (tooloption == "producecountmap"):
        columnA = "Count of inputted conflict scores"
        dftable1.columns = [columnA] 
    if (scoretypeToFocusOn == "all") or (scoretypeToFocusOn == "positive") or ((scoretypeToFocusOn == "negative") and (tooloption == "producecountmap")):
        dftable1 = dftable1.sort_values(by=[columnA], ascending=False)
    elif (scoretypeToFocusOn == "negative") and (tooloption == "producescoremap"):
        dftable1 = dftable1.sort_values(by=[columnA], ascending=True)
    gf.createNewPath(os.path.join(os.path.dirname(__file__),finalfoldername))
    dftable1.to_excel(os.path.join(os.path.dirname(__file__),finalfoldername,table1name))

#table2 main function: 
def forTable2getTotalMapSumCountAndAveragePerMarineUse(listOfLongMarineUseNames, dicttable2, finalfoldername, scoretypeToFocusOn, table2name, countChoice, tooloption):
    for longname in listOfLongMarineUseNames:
        if (tooloption == "producescoremap"): 
            # calculate average score per pairwise overlap in map  
            if dicttable2[longname][1] != 0.:
                dicttable2[longname][2] = float(dicttable2[longname][0])/float(dicttable2[longname][1])
            else: 
                dicttable2[longname][2] = 0
            # get sum of boolean array to get contributing cells  
            dicttable2[longname][3] = np.sum(dicttable2[longname][3])
            # calculate average score per contributing raster cell 
            if dicttable2[longname][3] == 0.:
                dicttable2[longname][4] = 0
            else: 
                dicttable2[longname][4] = float(dicttable2[longname][0])/float(dicttable2[longname][3])
            # calculate percent score contribution area
            if dicttable2[longname][5] == 0.:
                dicttable2[longname][6] = 0
            else: 
                dicttable2[longname][6] = float(dicttable2[longname][3])/float(dicttable2[longname][5])*100
        elif (tooloption == "producecountmap"):    
            # get count of contributing marine use raster cells:
            dicttable2[longname][5] = np.sum(dicttable2[longname][5])
    df = pd.DataFrame.from_dict(dicttable2, orient='index')
    if (tooloption == "producescoremap"):
        columnF = "Count of individual marine use raster cells for each marine use"
    elif (tooloption == "producecountmap"):   
        columnA = "Count of individual marine use raster cells for each marine use"    
        columnB = "Count of ocean raster cells"  
        columnC = "Ocean coverage percentage of data"
        columnF = "Count of each marine use raster cells that contain at least one overlap (overlap as defined by the count setting)"            
        if (countChoice == "count all combinations with a specific marine use") or (countChoice == "count all"):       
            columnD = "Total count of spatial pairwise combinations in map for each marine use (including the combinations that do not have a synergy-conflict score)"
            columnE = "Average count of spatial pairwise combinations per raster cell in map for each marine use (including the combinations that do not have a synergy-conflict score)"
            columnG = "Average count of spatial pairwise combinations per raster cell with overlaps in map for each marine use (including the combinations that do not have a synergy-conflict score)"              
    if (scoretypeToFocusOn == "all") and (tooloption == "producescoremap"): 
        columnA = "Total score in map for each marine use"
        columnB = "Total count of spatial pairwise conflict-synergy combinations in map for each marine use"
        columnC = "Average score per pairwise conflict-synergy combination in map for each marine use"
        columnD = "Total count of raster cells that each marine use contribute conflict-synergy scores to in map"
        columnE = "Average score per raster cell that each marine use contribute conflict-synergy scores to in map"
        columnG = "Percent area with conflict-synergy scores out of the area for each marine use"      
    elif (scoretypeToFocusOn == "all") and (tooloption == "producecountmap"):
        columnD = "Total count of spatial pairwise combinations in map for each marine use (only the combinations that have a synergy-conflict score)"
        columnE = "Average count of spatial pairwise combinations per raster cell in map for each marine use (only the combinations that have a synergy-conflict score)"
        columnG = "Average count of spatial pairwise combinations per raster cell with conflict-synergy overlaps in map for each marine use (only the combinations that have a synergy-conflict score)"
    elif (scoretypeToFocusOn == "positive") and (tooloption == "producescoremap"): 
        columnA = "Total positive score in map for each marine use"
        columnB = "Total count of spatial positive pairwise conflict-synergy combinations in map for each marine use"
        columnC = "Average score per positive pairwise conflict-synergy combination in map for each marine use"
        columnD = "Total count of raster cells that each marine use contribute synergy scores to in map"
        columnE = "Average score per raster cell that each marine use contribute synergy scores to in map"
        columnG = "Percent area with synergy scores out of the area for each marine use"      
    elif (scoretypeToFocusOn == "positive") and (tooloption == "producecountmap"):
        columnD = "Total count of spatial positive pairwise combinations in map for each marine use"
        columnE = "Average count of spatial positive pairwise combinations per raster cell in map for each marine use"
        columnG = "Average count of spatial positive pairwise combinations per raster cell with synergy overlaps in map for each marine use"
    elif (scoretypeToFocusOn == "negative") and (tooloption == "producescoremap"): 
        columnA = "Total negative score in map for each marine use"
        columnB = "Total count of spatial negative pairwise conflict-synergy combinations in map for each marine use"
        columnC = "Average score per negative pairwise conflict-synergy combination in map for each marine use"
        columnD = "Total count of raster cells that each marine use contribute conflict scores to in map"
        columnE = "Average score per raster cell that each marine use contribute conflict scores to in map"
        columnG = "Percent area with conflict scores out of the area for each marine use"      
    elif (scoretypeToFocusOn == "negative") and (tooloption == "producecountmap"):
        columnD = "Total count of spatial negative pairwise combinations in map for each marine use"
        columnE = "Average count of spatial negative pairwise combinations per raster cell in map for each marine use"
        columnG = "Average count of spatial negative pairwise combinations per raster cell with conflict overlaps in map for each marine use"
    df.columns = [columnA, columnB, columnC, columnD, columnE, columnF, columnG]  
    if (scoretypeToFocusOn == "all") or (scoretypeToFocusOn == "positive"):
        if (tooloption == "producescoremap"):    
            df = df.sort_values(by=[columnA], ascending=False)
        elif (tooloption == "producecountmap"):
            df = df.sort_values(by=[columnD], ascending=False)
    elif (scoretypeToFocusOn == "negative"):
        if (tooloption == "producescoremap"):    
            df = df.sort_values(by=[columnA], ascending=True)
        elif (tooloption == "producecountmap"):
            df = df.sort_values(by=[columnD], ascending=True)
    if (tooloption == "producecountmap"):
        # count coverage percentage:
        df[columnC] = df[columnA]/df[columnB]*100
        # count average count per marine use raster cell:
        df[columnE] = df[columnD]/df[columnA]
        # count average count per contributing marine use raster cell:
        df[columnG] = df[columnD]/df[columnF]   
    gf.createNewPath(os.path.join(os.path.dirname(__file__),finalfoldername))
    df.to_excel(os.path.join(os.path.dirname(__file__),finalfoldername,table2name))  

#table3 main function: 
def forTable3getTotalMapSumPerPairwiseCombination(finalfoldername, dftable3, table3name):
    gf.createNewPath(os.path.join(os.path.dirname(__file__),finalfoldername))
    dftable3.to_excel(os.path.join(os.path.dirname(__file__),finalfoldername,table3name), index=False)  

# convert pairwise score rasters into polygons where the matrix description is added as attribute: 
def pairwiseRasterToPolygon(rastername, specific_score, matrixinput, pairwise_output_folder, listpairwisepolygon, listpairwisepolygonname, tooloption):
    gf.createNewPath(pairwise_output_folder)
    marineuseoutput_shp_excl_folder = rastername[:-4]+".shp"
    marineuseoutput_shp_incl_folder = pairwise_output_folder+"\\"+marineuseoutput_shp_excl_folder
    arcpy.RasterToPolygon_conversion(arcpy.sa.Raster(pairwise_output_folder+"\\"+rastername), marineuseoutput_shp_incl_folder, "NO_SIMPLIFY","VALUE","MULTIPLE_OUTER_PART")             
    gf.addField(marineuseoutput_shp_incl_folder, "TEXT", fieldname = "finalvalue", precision = "", decimals = "", field_length = 20)
    if (tooloption == "producescoremap"): 
        gf.calculateField1(marineuseoutput_shp_incl_folder, "finalvalue", str(specific_score), expression_type="PYTHON")
    elif (tooloption == "producecountmap"):
        gf.calculateField1(marineuseoutput_shp_incl_folder, "finalvalue", str(1), expression_type="PYTHON")
    if (type(matrixinput) == float) and (tooloption == "producescoremap"): 
        matrixinput=''
    elif (type(matrixinput) == float) and (tooloption == "producecountmap"): 
        matrixinput = str(matrixinput)
    if (len(matrixinput)%254 == 0) and (tooloption == "producescoremap"): 
        numberroundsneeded = ((len(matrixinput)/254)+1)
    elif (len(matrixinput)%254 == 0) and (tooloption == "producecountmap"): 
        numberroundsneeded = int((len(matrixinput)/254)+1) 
    if (tooloption == "producescoremap"): 
        numberroundsneeded = ((len(matrixinput)/254)+2)
    elif (tooloption == "producecountmap"): 
        numberroundsneeded = int((len(matrixinput)/254)+2) 
    matrixstart=0
    matrixend=254
    if len(matrixinput) > 0: #if matrixinput is not an empty string
        for fieldcount in range(1,numberroundsneeded):
            gf.addField(marineuseoutput_shp_incl_folder, "TEXT", "full_desc"+str(fieldcount), precision = "", decimals = "", field_length = 254)
            gf.calculateField1(marineuseoutput_shp_incl_folder, "full_desc"+str(fieldcount), "'"+matrixinput[matrixstart:matrixend]+"'", expression_type="PYTHON")
            matrixstart=matrixstart+254
            matrixend=matrixend+254
            if matrixend > len(matrixinput):
                matrixend = len(matrixinput)
    arcpy.DeleteField_management(marineuseoutput_shp_incl_folder, "Id")
    listpairwisepolygon.append(marineuseoutput_shp_incl_folder)
    listpairwisepolygonname.append(marineuseoutput_shp_excl_folder)
    return (listpairwisepolygon, listpairwisepolygonname)

# save pairwise score numpyarrays as rasters: 
def pairwiseRasterToSave(array_input, lower_left_corner, dsc, spatial_ref, pairwise_output_folder, inputrastername1, inputrastername2, calculationtype, score, matrixinput, dictpairwiserastername, sum_of_all_cells, listpairwiserastername, tableOption3IsChecked, somePolygonsIsTrue, numbOfSome, tooloption):
    if (numbOfSome != 0): 
        pairwise_marine_use_array = np.copy(array_input)
        pairwise_marine_use_array = pairwise_marine_use_array.astype(int)
        pairwise_marine_use_array[pairwise_marine_use_array!=0.] = 1.
        pairwiseRaster = arcpy.NumPyArrayToRaster(pairwise_marine_use_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight, 0)
        gf.createNewPath(pairwise_output_folder)
        raster_outputname = gf.returnRasterFilename1(inputrastername1, inputrastername2, calculationtype)
        pairwiseRaster.save(pairwise_output_folder+"\\"+raster_outputname)
        arcpy.DefineProjection_management(pairwise_output_folder+"\\"+raster_outputname, spatial_ref)
        # if it is chosen to only add polygons to map with highest and lowest scores:
        if ((tableOption3IsChecked == "true") and (somePolygonsIsTrue == "true") and (numbOfSome != "all")):
            if sum_of_all_cells in dictpairwiserastername: 
                dictpairwiserastername[sum_of_all_cells].append(raster_outputname)
                if (tooloption == "producescoremap"):
                    dictpairwiserastername[sum_of_all_cells].append(score)
                dictpairwiserastername[sum_of_all_cells].append(matrixinput)

            else: 
                if (tooloption == "producescoremap"):
                    dictpairwiserastername[sum_of_all_cells] = [raster_outputname, score, matrixinput]
                elif (tooloption == "producecountmap"):
                    dictpairwiserastername[sum_of_all_cells] = [raster_outputname, matrixinput]
        # if it is chosen to add all polygons to map:
        else:
            listpairwiserastername.append(raster_outputname)
            if (tooloption == "producescoremap"):
                listpairwiserastername.append(score)
            listpairwiserastername.append(matrixinput)
    return (dictpairwiserastername, listpairwiserastername)    

# create pairwise score rasters based on marine use rasters and inputted score - main F1 function 2 of 2:
def scoresToRasters1(inputfoldernamewithpath, inputrastername1, inputrastername2, specific_score, lower_left_corner, dsc, matrixinput, pairwise_output_folder, dictpairwiserastername, calculationtype, tableOption2IsChecked, dicttable2, inputmarineuselongname1, inputmarineuselongname2, tableOption3IsChecked, dftable3, getStatisticsAndPolygons, listpairwiserastername, somePolygonsIsTrue, numbOfSome, spatial_ref, includeSynergyAndConflictAtOnceAreaIsTrue, tooloption):
    if (tooloption == "producecountmap"):
        array_pairwise_score = "redundantAsDefault"
    # create pairwise marine use score raster
    inputname1 = inputfoldernamewithpath+"\\"+inputrastername1
    array_input1 = arcpy.RasterToNumPyArray(inputname1) # array_input1 is marine use 1
    array_input1 = array_input1.astype(float)    
    inputname2 = inputfoldernamewithpath+"\\"+inputrastername2
    array_input2 = arcpy.RasterToNumPyArray(inputname2) # array_input2 is marine use 2 
    array_input2 = array_input2.astype(float)
    ifOverlaps = array_input1+array_input2==2. 
    ifNotOverlaps = array_input1+array_input2!=2.
    # table 2 inputs:
    if ((tableOption2IsChecked == "true") and (getStatisticsAndPolygons == "true")):
        if (tooloption == "producescoremap"): 
            dicttable2[inputmarineuselongname1][5]=np.count_nonzero(array_input1)
            dicttable2[inputmarineuselongname2][5]=np.count_nonzero(array_input2)
            dicttable2[inputmarineuselongname1][3] += ifOverlaps
            dicttable2[inputmarineuselongname2][3] += ifOverlaps
        elif (tooloption == "producecountmap"): 
            dicttable2[inputmarineuselongname1][0]=np.count_nonzero(array_input1)
            dicttable2[inputmarineuselongname2][0]=np.count_nonzero(array_input2)
            dicttable2[inputmarineuselongname1][5] += ifOverlaps
            dicttable2[inputmarineuselongname2][5] += ifOverlaps
    # update marine use array 1 to be a pairwise overlap array 
    array_input1[ifNotOverlaps] = 0.
    # create score raster for score tool:
    if (tooloption == "producescoremap"):
        array_input1[ifOverlaps] = specific_score # pairwise score array is created 
        array_pairwise_score = "redundant"
    elif (tooloption == "producecountmap"):
        # if polygon with synergies-and-conflicts-at-once should be included, get score array for count tool to count synergies and conflicts:
        if (includeSynergyAndConflictAtOnceAreaIsTrue == "true"):      
            array_pairwise_score = np.copy(array_input1)    
            array_pairwise_score[ifOverlaps] = specific_score # pairwise score array is created
		# create score raster for count tool: 
        array_input1[ifOverlaps] = 1. # pairwise count array is created (where score=1)
    # table 2 inputs:
    if ((tableOption2IsChecked == "true") and (getStatisticsAndPolygons == "true")):
		# table 2 inputs - sum of score cells: 
        if (tooloption == "producescoremap"):
            dicttable2[inputmarineuselongname1][0]+= np.sum(array_input1)
            dicttable2[inputmarineuselongname2][0]+= np.sum(array_input1)
		# table 2 inputs - count of score cells:
            dicttable2[inputmarineuselongname1][1]+= np.count_nonzero(array_input1)
            dicttable2[inputmarineuselongname2][1]+= np.count_nonzero(array_input1)
        elif (tooloption == "producecountmap"):
            dicttable2[inputmarineuselongname1][3]+= np.count_nonzero(array_input1)
            dicttable2[inputmarineuselongname2][3]+= np.count_nonzero(array_input1)
    # table 3 inputs:
    if ((tableOption3IsChecked == "true") and (getStatisticsAndPolygons == "true")):
        if (tooloption == "producescoremap"):
            (dftable3.loc[dftable3['Idcolumn'] == inputmarineuselongname2, inputmarineuselongname1]) = np.sum(array_input1)   
        elif (tooloption == "producecountmap"):
            (dftable3.loc[dftable3['Idcolumn'] == inputmarineuselongname2, inputmarineuselongname1]) = np.count_nonzero(array_input1)   
    # create a pairwise marine use overlap count raster to be converted later to polygon and outputtet later as extra map data:
    if (((len(np.unique(array_input1)) > 1) and (tooloption == "producescoremap")) or ((np.count_nonzero(array_input1) > 1) and (tooloption == "producecountmap"))) and (getStatisticsAndPolygons == "true") and (numbOfSome != 0):
        if (tooloption == "producescoremap"): 
            sum_of_all_cells = np.sum(array_input1)
        elif (tooloption == "producecountmap"): 
            sum_of_all_cells = np.count_nonzero(array_input1)
        (dictpairwiserastername, listpairwiserastername) = pairwiseRasterToSave(array_input1, lower_left_corner, dsc, spatial_ref, pairwise_output_folder, inputrastername1, inputrastername2, calculationtype, specific_score, matrixinput, dictpairwiserastername, sum_of_all_cells, listpairwiserastername, tableOption3IsChecked, somePolygonsIsTrue, numbOfSome, tooloption)
    return (array_input1, array_pairwise_score, dicttable2, dftable3, dictpairwiserastername, listpairwiserastername)
