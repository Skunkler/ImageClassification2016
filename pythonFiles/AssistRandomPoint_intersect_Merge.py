#This script was written by Warren Kunkler in support of the 2016 Clark County Imagery Project
#This script takes the points that were intersected for each feature class and merges them together

import arcpy
from arcpy import env


#Sets up environments and creates MergeInput_List
env.overwriteOutput = True

env.workspace = r"D:\LiDAR_factor\2016_LiDAR_study\studyAreaLiDAR.gdb"
ws = env.workspace

FCS = arcpy.ListFeatureClasses()
MergeInput_List = []

#loops through each file and merges the data to a MergeInput_List
for fc in FCS:
    if fc != "Random_points_20k":
        MergeInput_List.append(fc)

#merges all images together
arcpy.Merge_management(MergeInput_List, ws + '\\' + "Merged_OutputIntersect")

