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
import os
import time
import functions_general as gf 
import functions_MonteCarlo as mont 


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
dictactivities = gf.getDictionaryFromExcelTwoColumns(activities_linked_to_rasternames_excel, 'full_marine_use_category_name')

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
starttimetobeupdated = gf.resetTime(starttimetobeupdated)
(montecarlo_tif_incl_folder_list, montecarlo_outputnamelist, basisscore_tif_incl_folder_list, basisscore_outputnamelist) = mont.calculateMonteCarloIterationRaster(dictactivities, inputexcelsheet, inputfolder, iteration_folder, lower_left_corner, dsc, spatial_ref, iteration_outputname, oceanrastername_with_path, iterations, starttime, starttimetobeupdated, countScoreRasterIsTrue, changeScoreInputs, changeRankingMethod)
(printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Montecarlo for {} iterations have been calculated, {}\n".format(iterations, printline))

starttimetobeupdated = gf.resetTime(starttimetobeupdated)
gf.populateCurrentMapDocument3(montecarlo_tif_incl_folder_list, montecarlo_outputnamelist, binary_sensitivity_lyrfile, iteration_folder)
if countScoreRasterIsTrue == "true": 
    gf.populateCurrentMapDocument3(basisscore_tif_incl_folder_list, basisscore_outputnamelist, basis_score_lyrfile, iteration_folder)
(printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("If data exist, it has been added to current MXD document, {}\n".format(printline))
