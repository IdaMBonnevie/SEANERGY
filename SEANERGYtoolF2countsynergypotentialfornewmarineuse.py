# Purpose of script: 
#Script input to the tool called 'Find Synergy Potential Counts For New Marine Use'. 
#It finds locations of all existing marine uses that pairwisely have a positive conflict-synergy score with the specified input marine use. 
#It counts the number of such existing marine uses per cell. 

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
import time
import functions_F2potentialuse as f2 
import functions_general as gf 


# start timing: 
starttime = time.time()
starttimetobeupdated = starttime

# parameters
#paramter0 = folder_with_rasterinputs
inputfolder = arcpy.GetParameterAsText(0)
rasterinputlist = gf.getTifFilesInFolder(inputfolder)

#parameter1 = marine_uses_linked_to_rasternames excelsheet
marine_uses_linked_to_rasternames_excel = arcpy.GetParameterAsText(1)
dictMarineUses = gf.getDictionaryFromExcelTwoColumns(marine_uses_linked_to_rasternames_excel, 'full_marine_use_category_name')

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
starttimetobeupdated = gf.resetTime(starttimetobeupdated)
(output_tif_incl_folder, marineusepolygonnamelist_inkl_folder, marineusepolygonnamelist_exls_folder, pairwisescorepolygonnamelist_inkl_folder, pairwisescorepolygonnamelist_exls_folder) = f2.calculatePotentialSynergiesWithExistingUsesRaster(marineUseInFocus, dictMarineUses, inputexcelsheet, inputfolder, final_folder, pairwise_output_folder, process_folder, addConflictingExistingMarineUseInteractionsIsTrue, synergy_with_existing_uses_raster_only_ocean_name, oceanrastername_with_path, lower_left_corner, dsc, spatial_ref, starttimetobeupdated, "countsynergypotentialfornewmarineuse")
(printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Potential synergy destinations with counts have been calculated, {}\n".format(printline))

starttimetobeupdated = gf.resetTime(starttimetobeupdated)
gf.populateCurrentMapDocument2(output_tif_incl_folder, synergy_with_existing_uses_raster_only_ocean_name, marineusepolygonnamelist_inkl_folder, marineusepolygonnamelist_exls_folder, pairwisescorepolygonnamelist_inkl_folder, pairwisescorepolygonnamelist_exls_folder, new_marine_use_potentials_lyrfile, pairwise_lyrfile, final_folder, pairwise_output_folder)
(printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("If data exist, it has been added to current MXD document, {}\n".format(printline))
