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
    
#parameter4 = countraster_finaloutputname_only_ocean
finaloutputname_only_covering_ocean = arcpy.GetParameterAsText(4)

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
tableOption1IsChecked = arcpy.GetParameterAsText(8) 

#parameter9 = score sum per marine use based on map (checked or unchecked)  
tableOption2IsChecked = arcpy.GetParameterAsText(9) 

#parameter10 = score sum per pairwise combination based on map (checked or unchecked)  
tableOption3IsChecked = arcpy.GetParameterAsText(10) 

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
pairwise_output_foldername = "pairwise_outputs"
finalfoldername = "final_results"
if (scoretypeToFocusOn == "all") and ((countChoice == "count all") or (countChoice == "count all combinations with a specific marine use")):
    prename_table = scoretypeToFocusOn + "_" + scoretypeToFocusOn
else: 
    prename_table = scoretypeToFocusOn
table1name = "table1_"+prename_table+"_"+"total_count_per_marineuse_matrix.xlsx" 
table2name = "table2_"+prename_table+"_"+"total_count_per_marineuse_map.xlsx"
table3name = "table3_"+prename_table+"_"+"total_count_per_pairwise_combination_map.xlsx"
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
starttimetobeupdated = gf.resetTime(starttimetobeupdated)
(output_tif_incl_folder, listpairwisepolygon, listpairwisepolygonname, synergies_and_or_conflicts_array) = f1.calculatePairwiseAndTotalRasters(dictMarineUses, inputexcelsheet, scoretypeToFocusOn, inputfoldernamewithpath, pairwise_output_foldername, finalfoldername, tableOption1IsChecked, table1name, tableOption2IsChecked, table2name, tableOption3IsChecked, table3name, somePolygonsIsTrue, numbOfSome, "false", marineUseInFocus, includeSynergyAndConflictAtOnceAreaIsTrue, lower_left_corner, dsc, spatial_ref, finaloutputname_only_covering_ocean, oceanrastername_with_path, calculationtype, countChoice, chosen_category, chosen_category_score, attribute_excelsheet, "producecountmap")
(printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("Pairwise count rasters and total count raster have been calculated, {}\n".format(printline))

if includeSynergyAndConflictAtOnceAreaIsTrue == "true":
    starttimetobeupdated = gf.resetTime(starttimetobeupdated)
    (output_shp_incl_folder, output_shp_excl_folder) = gf.synergyAndConflictAtOnceRasterToPolygon(synergies_and_or_conflicts_array, lower_left_corner, dsc, spatial_ref, finalfoldername, conflict_and_synergy_shapefile)
    (printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
    arcpy.AddMessage("Synergy-and-conflict-at-once-raster has been calculated, {}\n".format(printline))
else: 
    output_shp_incl_folder = "false"
    output_shp_excl_folder = "false"

starttimetobeupdated = gf.resetTime(starttimetobeupdated)
gf.populateCurrentMapDocument1(output_tif_incl_folder, finaloutputname_only_covering_ocean, listpairwisepolygon, listpairwisepolygonname, output_shp_incl_folder, output_shp_excl_folder, count_lyrfile, pairwise_marine_use_lyrfile, conflict_and_synergy_lyrfile, finalfoldername, pairwise_output_foldername, includeSynergyAndConflictAtOnceAreaIsTrue)
(printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)                                                                    
arcpy.AddMessage("If data exist, it has been added to current MXD document, {}\n".format(printline))






