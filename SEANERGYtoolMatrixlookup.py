# Purpose of script: 
#Script input to the tool called 'Conflict Synergy Matrix Lookup'. 
#It print the matrix content belonging to the combination of the two inputted marined uses. 

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
#        if self.params[0].altered:
#            self.params[1].enabled = True
#            excelfile_with_path = (self.params[0].value.value).replace("\a","\\a").replace("\b","\\b")           
#            df = pd.read_excel(excelfile_with_path)
#            rawlist_use1_options = list(df.columns)
#            list_use1_options = rawlist_use1_options[1:]
#            self.params[1].filter.list = list_use1_options
#        else: 
#            self.params[1].enabled = False
#            self.params[2].enabled = False
#        if self.params[1].altered:
#            self.params[2].enabled = True
#            list_use2_options = list(df.ix[:,0])
#            self.params[2].filter.list = list_use2_options
#        else: 
#            self.params[2].enabled = False
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
import time
import functions_general as gf 


# start timing: 
starttime = time.time()
starttimetobeupdated = starttime


# environment:
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput=True
os.chdir(os.path.dirname(__file__))


# parameters: 
#parameter0 = matrix excelsheet
inputexcelsheet = arcpy.GetParameterAsText(0)

#parameter1 = long name for use1
use1 = arcpy.GetParameterAsText(1)

#parameter2 = long name for use2
use2 = arcpy.GetParameterAsText(2)


# main code:
df = pd.read_excel(inputexcelsheet)
list_use1_options = list(df.columns)[1:]
columnindex = list_use1_options.index(use1)
list_use2_options = list(df.ix[:,0])
rowindex = list_use2_options.index(use2)
if rowindex >= columnindex: 
    desc = df.ix[rowindex, columnindex+1]
else: 
    desc = df.ix[columnindex, rowindex+1]    

arcpy.AddMessage("\n")
starttimetobeupdated = gf.resetTime(starttimetobeupdated)
try:   
    if np.isnan(desc):
        (printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)
        arcpy.AddMessage("Matrix content is empty, {}\n".format(printline))    
except:
    if rowindex >= columnindex:
        arcpy.AddMessage("Matrix content is:")
        arcpy.AddMessage("For use1: {} and use2: {}:\n".format(use2, use1))
        arcpy.AddMessage("{} \n".format(desc))
        (printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)
        arcpy.AddMessage("Calculated {}".format(printline))    
    else: 
        arcpy.AddMessage("Matrix content is:")
        arcpy.AddMessage("For use1: {} and use2: {}:\n".format(use1, use2))
        arcpy.AddMessage("{} \n".format(desc))
        (printline, starttimetobeupdated) = gf.printTime(starttime, starttimetobeupdated)
        arcpy.AddMessage("Calculated {}".format(printline))    
