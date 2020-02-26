import arcpy
from arcpy import env

env.workspace = r"E:\2016_ClarkCounty_imageryclassification\LAS_POINTS_Process\LiDAR_products\Trees_processed.gdb"

env.overwriteOutput = True

GISDBA_Parcels = r"E:\2016_ClarkCounty_imageryclassification\LAS_POINTS_Process\LiDAR_products\reprocessed_images_vectorized_1.gdb\GISDBA_parcels"

FCS = arcpy.ListFeatureClasses()

codeblock = """def CalcArea(value1, value2):
    return value1/value2"""


for fc in FCS:
#    try:
    print fc
    arcpy.MakeFeatureLayer_management(fc, "lyr")
    arcpy.MakeFeatureLayer_management(GISDBA_Parcels, "parcels")

    arcpy.AddField_management("lyr", "Parcel_Area", "DOUBLE")
    arcpy.AddJoin_management("lyr", "APN", "parcels", "APN")
    arcpy.CalculateField_management("lyr", "Parcel_Area", "CalcArea(!" + fc + ".Shape_Area!, !GISDBA_parcels.Shape_Area!)", "PYTHON_9.3", codeblock)
    arcpy.RemoveJoin_management("lyr")
    print "process complete for " + fc
    #except:
     #   print "process failed for " + fc
