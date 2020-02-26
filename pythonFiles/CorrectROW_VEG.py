import arcpy, sys, os, string, time, datetime
from arcpy import env






env.workspace = r"E:\2016_ClarkCounty_imageryclassification\LAS_POINTS_Process\LiDAR_products\Missing_book_160\Missing_book_160_Trees.gdb"
ws = env.workspace

#env.workspace=ws

arcpy.env.overwriteOutput = True

fCS = arcpy.ListFeatureClasses()

GISDBA_Parcels = r'E:\2016_ClarkCounty_imageryclassification\LAS_POINTS_Process\LiDAR_products\book_139_test\vectorized_polys.gdb\GISDBA_parcels'
FinalOutput = ws


"""logpath = r"E:\2016_ClarkCounty_imageryclassification\las\logfiles"
scriptName = sys.argv[0]
logName = sys.argv[0].split('\\')[len(sys.argv[0].split("\\"))-1][0:-3]

logfile = logpath + '\\' + logName + '.log'
outfile = open(logfile, 'a')

outfile.write("\n" + "WORKSPACE: " + ws + "\n" + scriptName + "-----------------------------------------" + "\n")
outfile.close()"""





codeblock = """def FieldName(val, val2):
    val = val2
    return val"""

for fc in arcpy.ListFeatureClasses():
    if fc[-9:] == "intersect":
        try:
            print "select trees from classified veg layer..."
            arcpy.Select_analysis(fc, "Trees_select", "gridcode = 1")
            

            print "repairing and dissolving tree selection layer"
            arcpy.RepairGeometry_management('Trees_select')
            arcpy.Dissolve_management("Trees_select", ws + '\\' + fc[:-9] + '_dis', ["APN"])


            print "adding field to dissolve layer, calculating parcel field..."
            arcpy.MakeFeatureLayer_management(ws + '\\' + fc[:-9] + '_dis', 'Dissolve_Lyr')


            arcpy.AddField_management("Dissolve_Lyr", 'ParcelField', 'LONG')
            arcpy.AddJoin_management("Dissolve_Lyr", "APN", GISDBA_Parcels, "APN")
            arcpy.CalculateField_management("Dissolve_Lyr", "ParcelField", "FieldName(!" + fc[:-9] + "_dis.ParcelField!, !GISDBA_Parcels.LABEL_CLASS!)", "PYTHON_9.3", codeblock)
            arcpy.RemoveJoin_management("Dissolve_Lyr")


            print "select roads from GISDBA parcels, convert trees ROW polys to singlpart polys, and select trees NON ROW polys"
            arcpy.Select_analysis("Dissolve_Lyr", "Trees_ROW", "ParcelField = 717 OR ParcelField = 725")
            arcpy.MultipartToSinglepart_management("Trees_ROW", "Trees_ROW_Single")
            arcpy.Select_analysis("Dissolve_Lyr", "Trees_NONROW", "ParcelField < 717 or ParcelField = 719 OR ParcelField = 721 OR ParcelField > 725")



            print "select non_row_aoi layer"
            arcpy.MakeFeatureLayer_management("Trees_NONROW", "Trees_NONROW_lyr")
            arcpy.MakeFeatureLayer_management("Trees_ROW_Single", "Trees_ROW_Single_lyr")
    
            arcpy.SelectLayerByLocation_management("Trees_NONROW_lyr", "BOUNDARY_TOUCHES", "Trees_ROW_Single_lyr", "", "NEW_SELECTION", "NOT_INVERT")




            print "create non_row_aoi layer"
            arcpy.Select_analysis("Trees_NONROW_lyr", "TREES_NONROW_AOI")

            print "select non_row_non_aoi layer and create"
            arcpy.SelectLayerByLocation_management("Trees_NONROW_lyr", "BOUNDARY_TOUCHES", "Trees_ROW_Single_lyr", "", "NEW_SELECTION", "INVERT")
            arcpy.Select_analysis("Trees_NONROW_lyr", "TREES_NONROW_NONAOI")

            print "creating the last compiled_clean trees feature class"
            arcpy.Append_management("Trees_ROW_Single_lyr", "TREES_NONROW_AOI", "NO_TEST")
            arcpy.MakeFeatureLayer_management("TREES_NONROW_AOI", "TREES_NONROW_AOI_lyr")
            arcpy.SelectLayerByAttribute_management("TREES_NONROW_AOI_lyr", "NEW_SELECTION", "ParcelField = 717 OR ParcelField = 725")
            arcpy.Eliminate_management("TREES_NONROW_AOI_lyr", ws + '\\' + fc[:-9] + '_intermediateData')
            arcpy.MakeFeatureLayer_management(ws + '\\' + fc[:-9] + '_intermediateData', "intermediateData_lyr")
            arcpy.Append_management("intermediateData_lyr", "TREES_NONROW_NONAOI", "NO_TEST")

            arcpy.CopyFeatures_management("TREES_NONROW_NONAOI", FinalOutput + '\\' + fc[:-9] + '_TREES_correctROW')

        except:
            arcpy.Select_analysis(fc, "Trees_select", "gridcode = 1")
            arcpy.RepairGeometry_management("Trees_select")
            arcpy.Dissolve_management("Trees_select", FinalOutput + '\\' + fc[:-9] + "_TREES_correctROW", ["APN"])


            
            print "Process failed for: " + fc
            
            #outFail = open(logpath + "\\fail_" + logName + ".log", "a")
            #outFail.write( "failed " + fc + "\n")
            #outFail.close()
            print arcpy.GetMessages(2)
            ouch = arcpy.GetMessages(2)
            #outfile.write(ouch + "\n")
            #outfile.write("Process: Failed for: " + fc + " " + str(timeYearMonDay) + " " + str(timeHour) + ":" + str(timeMin) + "\n")

        #outfile.close()

"""timeYearMonDay = datetime.date.today()
timeHour = time.localtime()[3]
timeMin = time.localtime()[4]


print "Process done! " + str(timeYearMonDay) +  " " + str(timeHour)+ ":"   + str(timeMin)
outfile = open(logfile,'a')
outfile.write("Process Complete " + str(timeYearMonDay) + " " + str(timeHour) + ":" + str(timeMin) + '\n' )
outfile.close()"""
            
