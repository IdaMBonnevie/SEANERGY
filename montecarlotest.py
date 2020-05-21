# Purpose of script: 
#Script input to the tool called 'Monte Carlo Iteration'. 
#It adjusts score inputs randomly with maximal one synergy-conflict class up or down. It does this for each pairwise combination. 
#It does this iteratively for X iterations of the tool 'Calculate Score Map' where X is a tool input [recommended iteration input: 100 iterations]. 
#The values of positive Monte Carlo output raster cells show the number of times those cells have returned overall positive more than overall negative. 
#The values of negative Monte Carlo output raster cells show the number of times those cells have returned overall negative more than overall positive.
#With 100 iterations, -97 in a cell will indicate that the cell has returned negative in -98 cases, positive in 1 case, and neutral in 1 case.  

# The output is cut after an inputted ocean raster dataset. 


# DATE OF CREATION: 28-10-2019
# AUTHOR: Ida Maria Bonnevie

#All the Python modules in the import statement needs to be installed. 
#An ESRI ArcMap license with Spatial Analyst extension activated is required for the tool to run as a script tool in ArcMap. 


# Toolvalidator script inputted in tool: 
#import arcpy
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
#        if self.params[7].altered and self.params[7].value == True:		
#            self.params[8].enabled = True
#        else: 
#            self.params[8].enabled = False
#        
#        return
#
#    def updateMessages(self):
#        """Modify the messages created by internal validation for each tool
#        parameter.  This method is called after internal validation."""
#        return


# import standard modules: 
import arcpy
import random
import os
import pandas as pd 
import numpy as np
from collections import OrderedDict
import time
from datetime import datetime


# functions: 
def addLayerToMxd(mxd, df, inputname_inkl_folder, inputname_excl_folder, lyrfile, place, inputfolder):
    result = arcpy.MakeRasterLayer_management(inputname_inkl_folder, inputname_excl_folder[:-4]) 
    rlayer1 = result.getOutput(0)
    if lyrfile == "NotExisting": 
        lyrfile = "NotExisting"
    else: 
        arcpy.ApplySymbologyFromLayer_management(rlayer1, lyrfile)
    arcpy.mapping.AddLayer(df, rlayer1, place)
    del mxd, df

def calculateMonteCarloIterationRaster(dictactivities, matrixexcelfile, inputfolder, iteration_folder, lower_left_corner, dsc, spatial_ref, iteration_outputname, oceanrastername_with_path, iterations, starttime, starttimetobeupdated, countScoreRasterIsTrue, changeScoreInputs, changeRankingMethod):
    outputrasterlist = []
    outputrasternamelist = []
    outputextrarasterlist = []
    outputextrarasternamelist = []
    dfdesc = pd.read_excel(matrixexcelfile)    
    listOfLongActivityNames = dictactivities.keys()
    firstmontecarloraster = True
    for iteration in range(iterations): 
        starttimetobeupdated = resetTime(starttimetobeupdated)
        if changeRankingMethod == "true":
            # factor for 2.75:
            factor_2_75 = getRandomValueBetween0And1()
            # factor for 2.50:
            factor_2_50 = getRandomValueBetween0And1()
            # factor for 2.00:
            factor_2_00 = getRandomValueBetween0And1()
            # factor for 1.75:
            factor_1_75 = getRandomValueBetween0And1()
            # factor for 1.50:
            factor_1_50 = getRandomValueBetween0And1()
            # factor for 1.25:
            factor_1_25 = getRandomValueBetween0And1()
            # factor for 1.00:
            factor_1_00 = getRandomValueBetween0And1()
        firstpairwiserasterinround = True
        iterator1 = 0
        iterator2 = 1
        for column in listOfLongActivityNames: 
            inputrastername1 = dictactivities.get(column) 
            while iterator2 in range((iterator1+1),len(listOfLongActivityNames)):
                alldesc_nparray = dfdesc.loc[dfdesc['Idcolumn'] == listOfLongActivityNames[iterator2], column].values
                if len(alldesc_nparray) > 0:
                    alldesc = alldesc_nparray.item(0)
                    if len(str(alldesc)) >= 4: 
                        if alldesc[:1] == "-": 
                            spec_score = float(alldesc[:5].replace(",",".")) 
                        else: 
                            spec_score = float(alldesc[:4].replace(",","."))             
                        inputrastername2 = dictactivities.get(listOfLongActivityNames[iterator2]) #get raster2
                        if (firstmontecarloraster == True) and (firstpairwiserasterinround == True):
                            score_baseline = scoresToRasters(inputfolder, inputrastername1, inputrastername2, spec_score)                         
                            cells_with_score_array = np.copy(score_baseline)
                            cells_with_score_array[cells_with_score_array>0.] = 1 #1 is code for score
                            cells_with_score_array[cells_with_score_array<0.] = 1 #1 is code for score
                            cells_with_score_array = cells_with_score_array.astype(int)
                        elif (firstmontecarloraster == True): 
                            score_baseline += scoresToRasters(inputfolder, inputrastername1, inputrastername2, spec_score)                                                     
                            cells_with_score_array = updateScoreCellCount(score_baseline, cells_with_score_array)
                        # test score input variability: 
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
                        # test relative difference of scores: 
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
                        if firstpairwiserasterinround == True:   
                            score_outras_array = scoresToRasters(inputfolder, inputrastername1, inputrastername2, spec_score)
                            firstpairwiserasterinround = False
                        else: 
                            score_outras_array += scoresToRasters(inputfolder, inputrastername1, inputrastername2, spec_score)
                iterator2 += 1 #iterate through all rasters that are after raster1 (to iteratively be raster2)
            iterator1 += 1 #new raster1
            iterator2 = iterator1+1 #start again by iterating through rasters to be raster2 (now the number of following rasters has decreased by 1)
        if firstmontecarloraster == True:
            montecarlo_array = np.zeros_like(score_outras_array)
            montecarlo_array = montecarlo_array.astype(float)
            firstmontecarloraster = False
        score_outras_array[score_outras_array > 0.] = 1
        score_outras_array[score_outras_array < 0.] = -1
        montecarlo_array = montecarlo_array + score_outras_array
        (printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
        arcpy.AddMessage("iteration {} out of {} iterations, {}\n".format(iteration+1, iterations, printline))    
    # help raster: make boolean raster with land area as NoData:
    ocean_array = arcpy.RasterToNumPyArray(oceanrastername_with_path) # read ocean raster
    ocean_array = ocean_array.astype(float) # convert ocean raster to float
    # help checks 
    if_land_in_ocean_array = ocean_array == 0 # get all zero values corresponding to land in the ocean raster
    if_no_score_exist_array = cells_with_score_array == 0 # get all raster cells that have no pairwise scores
    if_positive_baseline = score_baseline > 0.
    if_negative_baseline = score_baseline < 0.
    if_neutral_baseline = score_baseline == 0.
    if_mostly_positive_iterations = montecarlo_array > 0.
    if_average_neutral_iterations = montecarlo_array == 0.
    if_mostly_negative_iterations = montecarlo_array < 0.
    ## output raster 1: make binary positive and negative raster:
    np.place(montecarlo_array, if_land_in_ocean_array & if_no_score_exist_array, np.nan) # replace all zero values that are both land and zero in the total binary output of all iterations with NoData
    scoreRasterOption1A = arcpy.NumPyArrayToRaster(montecarlo_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    (outputrasterlist, outputrasternamelist) = createRaster(iteration_folder, iteration_outputname, "_montecarlo_all", scoreRasterOption1A, spatial_ref, outputrasterlist, outputrasternamelist)
    ## output raster 2 (optional): make basis score raster
    if (countScoreRasterIsTrue == "true"):
        np.place(score_baseline, if_land_in_ocean_array & if_no_score_exist_array, np.nan)
        basisScoreRaster = arcpy.NumPyArrayToRaster(score_baseline, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
        createNewPath(iteration_folder)
        (outputextrarasterlist, outputextrarasternamelist) = createRaster(iteration_folder, iteration_outputname, "_basis_score", basisScoreRaster, spatial_ref, outputextrarasterlist, outputextrarasternamelist)   
    ## output raster 3: make mostly correct binary positive and negative raster:
    option1B_array = np.copy(montecarlo_array)
    np.place(option1B_array, ((
            if_mostly_positive_iterations & if_negative_baseline) | (
            if_mostly_negative_iterations & if_positive_baseline) | (
            if_average_neutral_iterations & if_positive_baseline) | (
            if_average_neutral_iterations & if_negative_baseline)    | (
            if_mostly_positive_iterations & if_neutral_baseline) | (
            if_mostly_negative_iterations & if_neutral_baseline)), np.nan) # set wrong values to NoData
    scoreRasterOption1B = arcpy.NumPyArrayToRaster(option1B_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    (outputrasterlist, outputrasternamelist) = createRaster(iteration_folder, iteration_outputname, "_montecarlo_correct", scoreRasterOption1B, spatial_ref, outputrasterlist, outputrasternamelist)
    ## output raster 4: make mostly correct score raster:
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
        (outputextrarasterlist, outputextrarasternamelist) = createRaster(iteration_folder, iteration_outputname, "_score_correct", scoreRasterOption1Bscore, spatial_ref, outputextrarasterlist, outputextrarasternamelist)
    ## output raster 5: make mostly wrong binary positive and negative raster:
    option1C_array = np.copy(montecarlo_array)
    np.place(option1C_array, ((
            if_mostly_positive_iterations & if_positive_baseline) | (
            if_mostly_negative_iterations & if_negative_baseline)  | (
            if_average_neutral_iterations & if_neutral_baseline)), np.nan) # set correct values to NoData
    scoreRasterOption1C = arcpy.NumPyArrayToRaster(option1C_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
    (outputrasterlist, outputrasternamelist) = createRaster(iteration_folder, iteration_outputname, "_montecarlo_wrong", scoreRasterOption1C, spatial_ref, outputrasterlist, outputrasternamelist)
    ## output raster 6: make mostly wrong score raster:
    if (countScoreRasterIsTrue == "true"):
        option1Cscore_array = np.copy(score_baseline)
        np.place(option1Cscore_array, ((
                if_mostly_positive_iterations & if_positive_baseline) | (
                if_mostly_negative_iterations & if_negative_baseline)  | (
                if_average_neutral_iterations & if_neutral_baseline)), np.nan) # set correct values to NoData
        scoreRasterOption1Cscore = arcpy.NumPyArrayToRaster(option1Cscore_array, lower_left_corner, dsc.meanCellWidth, dsc.meanCellHeight)
        (outputextrarasterlist, outputextrarasternamelist) = createRaster(iteration_folder, iteration_outputname, "_score_wrong", scoreRasterOption1Cscore, spatial_ref, outputextrarasterlist, outputextrarasternamelist)
    return (outputrasterlist, outputrasternamelist, outputextrarasterlist, outputextrarasternamelist)

def createNewPath(outputpath):
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

def createRaster(iteration_folder, iteration_outputname, extra_part_of_outputname, raster, spatial_ref, list_to_append_raster_to, list_to_append_rastername_to):
    createNewPath(iteration_folder)
    raster_tif_incl_folder = iteration_folder+"\\"+iteration_outputname[:-4]+extra_part_of_outputname+".tif"
    raster.save(raster_tif_incl_folder)
    arcpy.DefineProjection_management(raster_tif_incl_folder, spatial_ref)
    list_to_append_raster_to.append(raster_tif_incl_folder)
    list_to_append_rastername_to.append(iteration_outputname[:-4]+extra_part_of_outputname+".tif")
    return (list_to_append_raster_to, list_to_append_rastername_to)

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

def getRandomValueBetween0And1(): 
    new_factor = random.random()
    while (new_factor==0) or (new_factor==1):
        new_factor = random.random()
    return new_factor

def populateCurrentMapDocument(output_tif_incl_folder_list, outputnamelist, lyrfile, iteration_folder):
    try: 
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        for raster, outputname in zip(output_tif_incl_folder_list, outputnamelist):
            addLayerToMxd(mxd, df, raster, outputname, lyrfile, 'BOTTOM', iteration_folder)
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

def scoresToRasters(inputfoldername, inputrastername1, inputrastername2, score):
    # create pairwise activity score raster
    inputname1 = inputfoldername+"\\"+inputrastername1
    array_input1 = arcpy.RasterToNumPyArray(inputname1)
    array_input1 = array_input1.astype(float)
    inputname2 = inputfoldername+"\\"+inputrastername2
    array_input2 = arcpy.RasterToNumPyArray(inputname2)
    array_input2 = array_input2.astype(float)
    array_input1[array_input1+array_input2!=2.] = 0.    
    array_input1[array_input1+array_input2==2.] = score
    return (array_input1)

def updateScoreCellCount(score_outras_array, basic_array):
    positive_to_update = score_outras_array > 0    
    np.place(basic_array, positive_to_update, 1) #1 is code for score
    negative_to_update = score_outras_array < 0    
    np.place(basic_array, negative_to_update, 1) #1 is code for score
    return basic_array


# start timing: 
starttime = time.time()
starttimetobeupdated = starttime


# environment:
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput=True
os.chdir(os.path.dirname(__file__))


# parameters: 
#paramter0 = folder_with_rasterinputs
inputfolder = arcpy.GetParameterAsText(0)

#parameter1 = activities_linked_to_rasternames excelsheet
activities_linked_to_rasternames_excel = arcpy.GetParameterAsText(1)
dictactivities = getDictionaryFromExcelTwoColumns(activities_linked_to_rasternames_excel, 'full_marine_use_category_name')

#parameter2 = matrix excelsheet
inputexcelsheet = arcpy.GetParameterAsText(2)

#parameter3 = iteration output statistics raster name
iteration_outputname = arcpy.GetParameterAsText(3)

#parameter4 = oceanrastername_with_path
oceanrastername_with_path = arcpy.GetParameterAsText(4)

#parameter5 = iteration #recommendation = 100
iterations = int(arcpy.GetParameterAsText(5))

#parameter6 = monte carlo lyrfile
try: 
    binary_sensitivity_lyrfile = arcpy.GetParameterAsText(6)
    if binary_sensitivity_lyrfile == "": 
        binary_sensitivity_lyrfile = "NotExisting"
except: 
    binary_sensitivity_lyrfile = "NotExisting"

#parameter7 = add also basis total score map ##boolean  
countScoreRasterIsTrue = arcpy.GetParameterAsText(7)

#parameter8 = basis score lyrfile
try: 
    basis_score_lyrfile = arcpy.GetParameterAsText(8)
    if basis_score_lyrfile == "": 
        basis_score_lyrfile = "NotExisting"
except: 
    basis_score_lyrfile = "NotExisting"

#parameter9 = change score inputs by -1 to 1
try:
    changeScoreInputs = arcpy.GetParameterAsText(9)
    if changeScoreInputs == "": 
        changeScoreInputs = "false"
except: 
    changeScoreInputs = "false"    

#parameter10 = change ranking method
try:
    changeRankingMethod = arcpy.GetParameterAsText(10)
    if changeRankingMethod == "": 
        changeRankingMethod = "false"
except: 
    changeRankingMethod = "false"    
 
#extra script parameters: 
iteration_folder = "monte_carlo"

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
(montecarlo_tif_incl_folder_list, montecarlo_outputnamelist, basisscore_tif_incl_folder_list, basisscore_outputnamelist) = calculateMonteCarloIterationRaster(dictactivities, inputexcelsheet, inputfolder, iteration_folder, lower_left_corner, dsc, spatial_ref, iteration_outputname, oceanrastername_with_path, iterations, starttime, starttimetobeupdated, countScoreRasterIsTrue, changeScoreInputs, changeRankingMethod)
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Montecarlo for {} iterations have been calculated, {}\n".format(iterations, printline))

starttimetobeupdated = resetTime(starttimetobeupdated)
populateCurrentMapDocument(montecarlo_tif_incl_folder_list, montecarlo_outputnamelist, binary_sensitivity_lyrfile, iteration_folder)
if countScoreRasterIsTrue == "true": 
    populateCurrentMapDocument(basisscore_tif_incl_folder_list, basisscore_outputnamelist, basis_score_lyrfile, iteration_folder)
(printline, starttimetobeupdated) = printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("If data exist, it has been added to current MXD document, {}\n".format(printline))
