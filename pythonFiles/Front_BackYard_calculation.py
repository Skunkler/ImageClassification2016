import arcpy, string, os, sys, time, datetime
from arcpy import env

ws = r'H:\missing_sets\workSpace.gdb'
env.workspace = ws


arcpy.env.overwriteOutput = True

fcs = arcpy.ListFeatureClasses()
roads_layer = r"E:\2016_ClarkCounty_imageryclassification\las\Road_Work.gdb\GISDBA_roadparc_no_major_buf15"
GISDBA_Parcels = r"E:\2016_ClarkCounty_imageryclassification\las\FinalAccuracy_Assessment.gdb\GISDBA_AOParcels_AOX"

output = ws


logpath = r"E:\2016_ClarkCounty_imageryclassification\las\logfiles"
scriptName = sys.argv[0]
logName = "Front_BackYard_calculation"

logfile = logpath + '\\' + logName + '.log'
outfile = open(logfile, 'a')

outfile.write("\n" + "WORKSPACE: " + ws + "\n" + scriptName + "-----------------------------------------" + "\n")
outfile.close()

codeblock = """def YardDef(val):
    val = 'FrontYard'
    return val"""

codeblock2 = """def YardDef2(val):
    val = 'BackYard'
    return val"""


codeblock3 = """def ParcelFieldType(val1, val2):
    val1 = val2
    return val1"""

for fc in fcs:
    if fc[-9:] == "intersect":
        try:
            print "calculating turf for " + fc
            expression = "ParcelFieldType(!" + fc[:-10] + "turf_dis.ParcelField!, !GISDBA_parcels.LABEL_CLASS!)"
            arcpy.MakeFeatureLayer_management(fc, fc + "lyr")
            arcpy.MakeFeatureLayer_management(GISDBA_Parcels, "Parcels_Lyr")
            arcpy.AddJoin_management(fc + "lyr", "APN", "Parcels_Lyr", "APN", "KEEP_ALL")

            arcpy.Select_analysis(fc + "lyr", fc + "_Turf_Select" , fc + ".gridcode = 3 AND GISDBA_AOParcels_AOX.LANDUSE = '110'")
        
            arcpy.Select_analysis(fc + "lyr", fc + "_NonSFR_Turf", fc + ".gridcode = 3 AND GISDBA_AOParcels_AOX.LANDUSE NOT IN ('110')")
        
            arcpy.RepairGeometry_management(fc + "_Turf_Select")
            arcpy.Dissolve_management(fc + "_Turf_Select", ws + '\\' + fc[:-12] + "_turf_dis", [fc + "_APN"])


            arcpy.MakeFeatureLayer_management(ws + '\\' + fc[:-12] + "_turf_dis", "Turf_dis_lyr")
            arcpy.AddField_management("Turf_dis_lyr", "ParcelField", "LONG")
        
        
            arcpy.AddField_management("Turf_dis_lyr", "YardType", "TEXT", "", "", "50")
      
            arcpy.MultipartToSinglepart_management("Turf_dis_lyr", fc[:-12] + "_Turf_Select_single")
            arcpy.MakeFeatureLayer_management(roads_layer, "roads_lyr")
            arcpy.MakeFeatureLayer_management(fc[:-12] + "_Turf_Select_single", "Turf_Select_single_lyr")
            arcpy.SelectLayerByLocation_management("Turf_Select_single_lyr", "INTERSECT", "roads_lyr","", "NEW_SELECTION", "NOT_INVERT")
            arcpy.CalculateField_management("Turf_Select_single_lyr", "YardType", "YardDef(!YardType!)", "PYTHON_9.3", codeblock)


        
            arcpy.SelectLayerByAttribute_management("Turf_Select_single_lyr", "NEW_SELECTION", "YardType IS NULL")
            arcpy.CalculateField_management("Turf_Select_single_lyr", "YardType", "YardDef2(!YardType!)", "PYTHON_9.3", codeblock2)
            arcpy.SelectLayerByAttribute_management("Turf_Select_single_lyr", "CLEAR_SELECTION")
            arcpy.CopyFeatures_management("Turf_Select_single_lyr", output + '\\' + fc[:-12] + "turf_calculated")

            arcpy.MakeFeatureLayer_management(output + '\\' + fc[:-12] + "turf_calculated", "Turf_calc_lyr")
            arcpy.MakeFeatureLayer_management(fc + "_NonSFR_Turf", "NonSFR_Lyr")
            

            arcpy.Append_management(["NonSFR_lyr"], "Turf_calc_lyr", "NO_TEST")
            arcpy.RemoveJoin_management(fc + "lyr")
            print "success for calculating turf for " + fc
        except:
            print "Process failed for: " + fc
            outFail = open(logpath + "\\fail_" + logName + ".log", "a")
            outFail.write( "failed " + fc + "\n")
            outFail.close()
            print arcpy.GetMessages(2)
            ouch = arcpy.GetMessages(2)
            outfile.write(ouch + "\n")
            outfile.write("Process: Failed for: " + fc + " " + str(timeYearMonDay) + " " + str(timeHour) + ":" + str(timeMin) + "\n")

        outfile.close()

timeYearMonDay = datetime.date.today()
timeHour = time.localtime()[3]
timeMin = time.localtime()[4]


print "Process done! " + str(timeYearMonDay) +  " " + str(timeHour)+ ":"   + str(timeMin)
outfile= open(logfile,'a')
outfile.write("Process Complete "  + str(timeYearMonDay) +  " " + str(timeHour)+ ":"   + str(timeMin) +  '\n' )
outfile.close()
