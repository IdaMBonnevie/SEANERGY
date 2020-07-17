# MONTE CARLO FUNCTIONS FOR SEANERGY for the tool 'Monte Carlo Iteration'        

# import modules: 
import arcpy
import numpy as np 
import pandas as pd
import functions_general as gf 


# functions for Monte Carlo iteration of total conflict-synergy scores: 
def calculateMonteCarloIterationRaster(dictactivities, matrixexcelfile, inputfolder, iteration_folder, lower_left_corner, dsc, spatial_ref, iteration_outputname, oceanrastername_with_path, iterations, starttime, starttimetobeupdated, countScoreRasterIsTrue, changeScoreInputs, changeRankingMethod):
    # preset parameters: 
    outputrasterlist = []
    outputrasternamelist = []
    outputextrarasterlist = []
    outputextrarasternamelist = []
    dfdesc = pd.read_excel(matrixexcelfile)    
    listOfLongActivityNames = dictactivities.keys()
    firstmontecarloraster = True
    # iterate through the Monte Carlo rounds: 
    for iteration in range(iterations): 
        starttimetobeupdated = gf.resetTime(starttimetobeupdated)
        # create random factors for test 2 (change scoring scale): 
        if changeRankingMethod == "true":
            # factor for 2.75:
            factor_2_75 = gf.getRandomValueBetween0And1()
            # factor for 2.50:
            factor_2_50 = gf.getRandomValueBetween0And1()
            # factor for 2.00:
            factor_2_00 = gf.getRandomValueBetween0And1()
            # factor for 1.75:
            factor_1_75 = gf.getRandomValueBetween0And1()
            # factor for 1.50:
            factor_1_50 = gf.getRandomValueBetween0And1()
            # factor for 1.25:
            factor_1_25 = gf.getRandomValueBetween0And1()
            # factor for 1.00:
            factor_1_00 = gf.getRandomValueBetween0And1()
        firstpairwiserasterinround = True
        iterator1 = 0
        iterator2 = 1
        # get pairwise scores and turn them iteratively into total scores for the specific Monte Carlo round: 
        for column in listOfLongActivityNames: 
            inputrastername1 = dictactivities.get(column) # get marine use raster 1
            while iterator2 in range((iterator1+1),len(listOfLongActivityNames)):
                alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongActivityNames[iterator2], column].values
                # get scores: 
                if len(alldesc_nparray) > 0:
                    alldesc = alldesc_nparray.item(0)
                    if len(str(alldesc)) >= 4: 
                        if alldesc[:1] == "-": 
                            spec_score = float(alldesc[:5].replace(",",".")) 
                        else: 
                            spec_score = float(alldesc[:4].replace(",","."))             
                        inputrastername2 = dictactivities.get(listOfLongActivityNames[iterator2]) #get marine use raster 2
                        # create baseline total score raster where the score inputs stay unchanged and create an array that tracks the presence of conflicts/synergies: 
                        if (firstmontecarloraster == True) and (firstpairwiserasterinround == True):
                            score_baseline = scoresToRasters3(inputfolder, inputrastername1, inputrastername2, spec_score)                         
                            cells_with_score_array = np.copy(score_baseline)
                            cells_with_score_array[cells_with_score_array>0.] = 1 #1 is to count the presence of a conflict or synergy
                            cells_with_score_array[cells_with_score_array<0.] = 1 #1 is to count the presence of a conflict or synergy
                            cells_with_score_array = cells_with_score_array.astype(int)
                        elif (firstmontecarloraster == True): 
                            score_baseline += scoresToRasters3(inputfolder, inputrastername1, inputrastername2, spec_score)                                                     
                            cells_with_score_array = gf.updateScoreCellCount(score_baseline, cells_with_score_array, "montecarlo")
                        # test 1: test score category input variability: 
                        if changeScoreInputs == "true": 
                            if spec_score == -3.00:
                                spec_score = (spec_score + np.random.choice([0.00, 1.00]))
                            elif spec_score == -2.00:
                                spec_score = (spec_score + np.random.choice([-1.00, 0.00, 1.00]))
                            elif spec_score == -1.00:
                                spec_score = (spec_score + np.random.choice([-1.00, 0.00, 2.00]))
                            elif spec_score == 1.00:
                                spec_score = (spec_score + np.random.choice([-2.00, 0.00, 0.25, 0.50, 0.75, 1.00]))
                            elif spec_score == 1.25:
                                spec_score = (spec_score + np.random.choice([-2.25, -0.25, 0.00, 0.25, 0.50, 0.75]))
                            elif spec_score == 1.50:
                                spec_score = (spec_score + np.random.choice([-0.50, -0.25, 0.00, 0.25, 0.50, 1.00, 1.25, 1.50]))
                            elif spec_score == 1.75:
                                spec_score = (spec_score + np.random.choice([-0.75, -0.50, -0.25, 0.00, 0.25, 0.75, 1.00, 1.25]))
                            elif spec_score == 2.00:
                                spec_score = (spec_score + np.random.choice([-1.00, -0.75, -0.50, -0.25, 0.00, 0.50, 0.75, 1.00]))
                            elif spec_score == 2.50:
                                spec_score = (spec_score + np.random.choice([-1.50, -1.25, -1.00, -0.75, -0.50, 0.00, 0.25, 0.50]))
                            elif spec_score == 2.75:
                                spec_score = (spec_score + np.random.choice([-0.75, -0.25, 0.00, 0.25]))
                            elif spec_score == 3.00:
                                spec_score = (spec_score + np.random.choice([-1.00, -0.50, -0.25, 0.00]))
                        # test 2: test relative difference of scores (scoring scale): 
                        if changeRankingMethod == "true": 
                            if (spec_score == 2.75):
                                spec_score = 3.0*factor_2_75
                            elif (spec_score == 2.50):
                                spec_score = (3.0*factor_2_75)*factor_2_50
                            elif (spec_score == 2.00):
                                spec_score = ((3.0*factor_2_75)*factor_2_50)*factor_2_00
                            elif (spec_score == 1.75):
                                spec_score = (((3.0*factor_2_75)*factor_2_50)*factor_2_00)*factor_1_75
                            elif (spec_score == 1.50):
                                spec_score = ((((3.0*factor_2_75)*factor_2_50)*factor_2_00)*factor_1_75)*factor_1_50
                            elif (spec_score == 1.25):
                                spec_score = (((((3.0*factor_2_75)*factor_2_50)*factor_2_00)*factor_1_75)*factor_1_50)*factor_1_25
                            elif (spec_score == 1.00):
                                spec_score = ((((((3.0*factor_2_75)*factor_2_50)*factor_2_00)*factor_1_75)*factor_1_50)*factor_1_25)*factor_1_00
                            elif (spec_score == -2.00):
                                spec_score = ((-3.0*factor_2_75)*factor_2_50)*factor_2_00
                            elif (spec_score == -1.00):
                                spec_score = ((((((-3.0*factor_2_75)*factor_2_50)*factor_2_00)*factor_1_75)*factor_1_50)*factor_1_25)*factor_1_00
                        # create/update total score raster (score_outras_array) where the score inputs have changed based on the selected test/tests:  
                        if firstpairwiserasterinround == True:   
                            score_outras_array = scoresToRasters3(inputfolder, inputrastername1, inputrastername2, spec_score)
                            firstpairwiserasterinround = False
                        else: 
                            score_outras_array += scoresToRasters3(inputfolder, inputrastername1, inputrastername2, spec_score)
                iterator2 += 1 #iterate through all rasters that are after raster1 (to iteratively be raster2)
            iterator1 += 1 #new raster1
            iterator2 = iterator1+1 #start again by iterating through rasters to be raster2 (now the number of following rasters has decreased by 1)
        # a Monte Carlo array is created if not existing already: 
        if firstmontecarloraster == True:
            montecarlo_array = np.zeros_like(score_outras_array)
            montecarlo_array = montecarlo_array.astype(float)
            firstmontecarloraster = False
        # the total score raster where the inputs have changed is updated to track the presence of conflicts (value=-1) and the presence of synergies (value=1) in the specific Monte Carlo round:
        score_outras_array[score_outras_array > 0.] = 1
        score_outras_array[score_outras_array < 0.] = -1
        # The Monte Carlo array is counting the number of times in each Monte Carlo round that a raster returns with respectively synergies (value=1), conflicts (value=-1), or not any of the two (value=0):
        montecarlo_array = montecarlo_array + score_outras_array
        (printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
        arcpy.AddMessage("iteration {} out of {} iterations, {}\n".format(iteration+1, iterations, printline))    
    # Some statistics numpy arrays are produced to adjust the final Monte Carlo raster: 
    ocean_array = arcpy.RasterToNumPyArray(oceanrastername_with_path) # read ocean raster
    ocean_array = ocean_array.astype(float) # convert ocean raster to float
    if_land_in_ocean_array = ocean_array == 0 # get all zero values corresponding to land in the ocean raster
    if_no_score_exist_array = cells_with_score_array == 0 # get all raster cells that have no pairwise scores
    if_positive_baseline = score_baseline > 0.
    if_negative_baseline = score_baseline < 0.
    if_neutral_baseline = score_baseline == 0.
    if_mostly_positive_iterations = montecarlo_array > 0.
    if_average_neutral_iterations = montecarlo_array == 0.
    if_mostly_negative_iterations = montecarlo_array < 0.
    # Output raster 1: Make Monte Carlo main output raster counting the number of times each raster cell returns positive minus negative:
    np.place(montecarlo_array, if_land_in_ocean_array & if_no_score_exist_array, np.nan) # replace all zero values that are both land and zero in the total binary output of all iterations with NoData
    scoreRasterOption1A = arcpy.NumPyArrayToRaster(montecarlo_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    (outputrasterlist, outputrasternamelist) = gf.createRaster(iteration_folder, iteration_outputname, "_montecarlo_all", scoreRasterOption1A, spatial_ref, outputrasterlist, outputrasternamelist)
    # Output raster 2 (optional): Make basis score raster where inputs are unchanged 
    if (countScoreRasterIsTrue == "true"):
        np.place(score_baseline, if_land_in_ocean_array & if_no_score_exist_array, np.nan)
        basisScoreRaster = arcpy.NumPyArrayToRaster(score_baseline, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
        gf.createNewPath(iteration_folder)
        (outputextrarasterlist, outputextrarasternamelist) = gf.createRaster(iteration_folder, iteration_outputname, "_basis_score", basisScoreRaster, spatial_ref, outputextrarasterlist, outputextrarasternamelist)   
    # Output raster 3: Make Monte Carlo main output raster with robust ("correct") positive/negative/neutral trends: 
    option1B_array = np.copy(montecarlo_array)
    np.place(option1B_array, ((
            if_mostly_positive_iterations & if_negative_baseline) | (
            if_mostly_negative_iterations & if_positive_baseline) | (
            if_average_neutral_iterations & if_positive_baseline) | (
            if_average_neutral_iterations & if_negative_baseline)    | (
            if_mostly_positive_iterations & if_neutral_baseline) | (
            if_mostly_negative_iterations & if_neutral_baseline)), np.nan) # set wrong values to NoData
    scoreRasterOption1B = arcpy.NumPyArrayToRaster(option1B_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    (outputrasterlist, outputrasternamelist) = gf.createRaster(iteration_folder, iteration_outputname, "_montecarlo_correct", scoreRasterOption1B, spatial_ref, outputrasterlist, outputrasternamelist)
    # Output raster 4 (optional): Make basis score raster with robust ("correct") positive/negative/neutral trends:
    if (countScoreRasterIsTrue == "true"):
        option1Bscore_array = np.copy(score_baseline)
        np.place(option1Bscore_array, ((
                if_mostly_positive_iterations & if_negative_baseline) | (
                if_mostly_negative_iterations & if_positive_baseline) | (
                if_average_neutral_iterations & if_positive_baseline) | (
                if_average_neutral_iterations & if_negative_baseline)    | (
                if_mostly_positive_iterations & if_neutral_baseline) | (
                if_mostly_negative_iterations & if_neutral_baseline)), np.nan) # set wrong values to NoData
        scoreRasterOption1Bscore = arcpy.NumPyArrayToRaster(option1Bscore_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
        (outputextrarasterlist, outputextrarasternamelist) = gf.createRaster(iteration_folder, iteration_outputname, "_score_correct", scoreRasterOption1Bscore, spatial_ref, outputextrarasterlist, outputextrarasternamelist)
    # Output raster 5: Make Monte Carlo main output raster with sensitive ("wrong") positive/negative/neutral trends:
    option1C_array = np.copy(montecarlo_array)
    np.place(option1C_array, ((
            if_mostly_positive_iterations & if_positive_baseline) | (
            if_mostly_negative_iterations & if_negative_baseline)  | (
            if_average_neutral_iterations & if_neutral_baseline)), np.nan) # set correct values to NoData
    scoreRasterOption1C = arcpy.NumPyArrayToRaster(option1C_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    (outputrasterlist, outputrasternamelist) = gf.createRaster(iteration_folder, iteration_outputname, "_montecarlo_wrong", scoreRasterOption1C, spatial_ref, outputrasterlist, outputrasternamelist)
    # Output raster 6(optional): Make basis score raster with sensitive ("wrong") positive/negative/neutral trends:
    if (countScoreRasterIsTrue == "true"):
        option1Cscore_array = np.copy(score_baseline)
        np.place(option1Cscore_array, ((
                if_mostly_positive_iterations & if_positive_baseline) | (
                if_mostly_negative_iterations & if_negative_baseline)  | (
                if_average_neutral_iterations & if_neutral_baseline)), np.nan) # set correct values to NoData
        scoreRasterOption1Cscore = arcpy.NumPyArrayToRaster(option1Cscore_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
        (outputextrarasterlist, outputextrarasternamelist) = gf.createRaster(iteration_folder, iteration_outputname, "_score_wrong", scoreRasterOption1Cscore, spatial_ref, outputextrarasterlist, outputextrarasternamelist)
    return (outputrasterlist, outputrasternamelist, outputextrarasterlist, outputextrarasternamelist)

# convert two existing marine uses into a pairwise score numpy array: 
def scoresToRasters3(inputfoldername, inputrastername1, inputrastername2, score):
    inputname1 = inputfoldername+"\\"+inputrastername1
    array_input1 = arcpy.RasterToNumPyArray(inputname1)
    array_input1 = array_input1.astype(float)
    inputname2 = inputfoldername+"\\"+inputrastername2
    array_input2 = arcpy.RasterToNumPyArray(inputname2)
    array_input2 = array_input2.astype(float)
    array_input1[array_input1+array_input2!=2.] = 0.    
    array_input1[array_input1+array_input2==2.] = score
    return (array_input1)


