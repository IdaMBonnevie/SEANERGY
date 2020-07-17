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
import time
import functions_F1existinguses as f1 
import functions_general as gf 


# start timing: 
starttime = time.time()
starttimetobeupdated = starttime


# parameters: 
#paramter0 = folder_with_rasterinputs
inputfoldernamewithpath = arcpy.GetParameterAsText(0)

#parameter1 = marine_uses_linked_to_rasternames excelsheet
marine_uses_linked_to_rasternames_excel = arcpy.GetParameterAsText(1)
dictMarineUses = gf.getDictionaryFromExcelTwoColumns(marine_uses_linked_to_rasternames_excel, 'full_marine_use_category_name')

#parameter2 = matrix excelsheet
inputexcelsheet = arcpy.GetParameterAsText(2)

#parameter3 = pos, neg, all strings
scoretypeToFocusOn = arcpy.GetParameterAsText(3)

#parameter4 = scoreraster_finaloutputname_only_ocean
finaloutputname_only_covering_ocean = arcpy.GetParameterAsText(4)

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
tableOption1IsChecked = arcpy.GetParameterAsText(8) 

#parameter9 = score sum per marine use based on map (checked or unchecked) 
tableOption2IsChecked = arcpy.GetParameterAsText(9) 

#parameter10 = score sum per pairwise combination based on map (checked or unchecked)  
tableOption3IsChecked = arcpy.GetParameterAsText(10) 

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
pairwise_output_foldername = "pairwise_outputs"
finalfoldername = "final_results"
table1name = "table1_"+scoretypeToFocusOn+"_"+"total_score_per_marineuse_matrix.xlsx"
table2name = "table2_"+scoretypeToFocusOn+"_"+"total_score_per_marineuse_map.xlsx"
table3name = "table3_"+scoretypeToFocusOn+"_"+"total_score_per_pairwise_combination_map.xlsx"
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
starttimetobeupdated = gf.resetTime(starttimetobeupdated)
(output_tif_incl_folder, listpairwisepolygon, listpairwisepolygonname, synergies_and_or_conflicts_array) = f1.calculatePairwiseAndTotalRasters(dictMarineUses, inputexcelsheet, scoretypeToFocusOn, inputfoldernamewithpath, pairwise_output_foldername, finalfoldername, tableOption1IsChecked, table1name, tableOption2IsChecked, table2name, tableOption3IsChecked, table3name, somePolygonsIsTrue, numbOfSome, onlyOneMarineUseInFocusIsTrue, marineUseInFocus, includeSynergyAndConflictAtOnceAreaIsTrue, lower_left_corner, dsc, spatial_ref, finaloutputname_only_covering_ocean, oceanrastername_with_path, calculationtype, "noCountChoice", "no_chosen_category", "no_chosen_category_score", "no_attribute_excelsheet", "producescoremap")
(printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Pairwise score rasters and total score raster have been calculated, {}\n".format(printline))

# make synergy-and-conflict area polygon - part 5:
if includeSynergyAndConflictAtOnceAreaIsTrue == "true":
    starttimetobeupdated = gf.resetTime(starttimetobeupdated)
    (output_shp_incl_folder, output_shp_excl_folder) = gf.synergyAndConflictAtOnceRasterToPolygon(synergies_and_or_conflicts_array, lower_left_corner, dsc, spatial_ref, finalfoldername, conflict_and_synergy_shapefile)
    (printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
    arcpy.AddMessage("Synergy-and-conflict-at-once-raster has been calculated, {}\n".format(printline))
else: 
    output_shp_incl_folder = "false"
    output_shp_excl_folder = "false"

starttimetobeupdated = gf.resetTime(starttimetobeupdated)
gf.populateCurrentMapDocument1(output_tif_incl_folder, finaloutputname_only_covering_ocean, listpairwisepolygon, listpairwisepolygonname, output_shp_incl_folder, output_shp_excl_folder, score_lyrfile, pairwise_lyrfile, conflict_and_synergy_lyrfile, finalfoldername, pairwise_output_foldername, includeSynergyAndConflictAtOnceAreaIsTrue)
(printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("If data exist, it has been added to current MXD document, {}\n".format(printline))
