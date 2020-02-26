#This simple script was written by Warren Kunkler in support of the 2016 Clark County Vegetation Classification project
#This script intersects the random points layer with the cleaned up feature classes that were generated by the vectorization of
#the thematic classification results

import arcpy
from arcpy import env

env.overwriteOutput = True

#designates output and environments
output = r"E:\2016_ClarkCounty_imageryclassification\LAS_POINTS_Process\LiDAR_products\output_point_fcs.gdb"

env.workspace = r"E:\2016_ClarkCounty_imageryclassification\LAS_POINTS_Process\LiDAR_products\output_cleaned_images.gdb"

ws = env.workspace

#grabs feature classes and 20K random point class
FCS = arcpy.ListFeatureClasses()
RandomPoints = r"E:\2016_ClarkCounty_imageryclassification\LAS_POINTS_Process\LiDAR_products\output_cleaned_images.gdb\RandomPoints_20k"
for fc in FCS:
    print fc
    if fc != "RandomPoints_20k":
    #intersects the random points with the feature class
        intersect_features = [fc, RandomPoints]
        arcpy.Intersect_analysis(intersect_features, output + '\\' + fc, "", "", "point")
    
