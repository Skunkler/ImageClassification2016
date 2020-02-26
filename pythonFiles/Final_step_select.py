import arcpy, sys, datetime, time, os, string
from arcpy import env

#set variables for the logpath
logpath = r'E:\2016_ClarkCounty_imageryclassification\las\logfiles'

ws = r'E:\2016_ClarkCounty_imageryclassification\LAS_POINTS_Process\LiDAR_products\reprocessed_images_vectorized_1.gdb'
env.workspace = ws
env.overwriteOutput = True

scriptName = sys.argv[0]
logName = sys.argv[0].split('\\')[len(sys.argv[0].split("\\"))-1][0:-3]

logfile = logpath + '\\' + logName + '.log'
outfile = open(logfile, 'a')

outfile.write("\n" + "WORKSPACE: " + ws + "\n" + scriptName + "-----------------------------------------" + "\n")
outfile.close()





featureClasses = arcpy.ListFeatureClasses()

#expressions and codeblocks used to calculate fields using python in the field calculator tool
expression9 = "gridcode = 2"
expression10 = "gridcode = 4"

codeblock = """def Grid(val):
    val = 4
    return val"""

codeblock2 = """def Grid(val):
    val = 3
    return val"""

codeblock4 = """def Grid(val):
    val = 4
    return val"""

codeblock3 = """def val(val1, val2):
    if val2 == 4:
        val1 = val2
        return val1
    elif val2 == 3:
        val1 = val2
        return val1
    else:
        val1=val1
        return val1"""

#path to final output geodatabase
output = r'E:\2016_ClarkCounty_imageryclassification\las\Cleanup_veg_10_25_2017_output.gdb'
Parcels = r'E:\2016_ClarkCounty_imageryclassification\las\test_10_23_2017_1.gdb\GISDBA_Parcels'

#loop through all vectorized classification results
for fc in featureClasses:
    if fc[-4:] == "_veg":
        timeYearMonDay = datetime.date.today()
        timeHour = time.localtime()[3]
        timeMin = time.localtime()[4]

        outfile = open(logfile, 'a')
        print fc
        outfile.write(fc + " " + str(timeYearMonDay) + " " + str(timeHour) + ":" + str(timeMin) + "\n")
    
        try:

            #set our 5th expression to the original veg layer and select veg layer gridcode fields
            #print fc
            st = fc
            expression5 = "val(!" + fc[:-4] + "_intersect.gridcode!, !" + fc[:-6] + "_select23.gridcode!)"


            arcpy.Intersect_analysis([fc, Parcels], ws + '\\' + fc[:-4] + "_intersect")
            FC_intersect = ws + '\\' + fc[:-4] + "_intersect"
            #create a selection feature class of just small areas from classes 2 and 3
            print "round1: selecting small areas from classes 2 and 3..."
            arcpy.Select_analysis(FC_intersect, ws + '\\' + fc[:-6] +'_select23', "gridcode >= 2 AND Shape_Area <= 300")
            FC_select = ws + '\\' + fc[:-6] + '_select23'

            #make another selection from the original veg layer of class 3 polygons that are larger than 300 sq ft
            arcpy.MakeFeatureLayer_management(FC_intersect, "lyr")
            print "selecting attributes for class 3 larger that 300 sq ft..."
            arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", "gridcode = 4 AND Shape_Area > 300")
    
            arcpy.MakeFeatureLayer_management(FC_select, "lyr2")
            #use select by location of the select feature class to grab small class 2 and 3 near class 3
            print "select small classes near class 3..."
            arcpy.SelectLayerByLocation_management("lyr2", "intersect", "lyr", 1, "NEW_SELECTION")

            #use field calculator tool to recalculate small class 2 and 3 polys to class 3 if they are near class 3 in the original layer
            print "calculating gridcode value with codeblock 1..."
            arcpy.CalculateField_management("lyr2", "gridcode", "Grid(!gridcode!)", "PYTHON_9.3", codeblock)

            #select remaining class 2 polys from select layer and reclass them to class 1
            print "selecting remaining class 2 polys and executing codeblock 2..."
            arcpy.SelectLayerByAttribute_management("lyr2", "NEW_SELECTION", "gridcode = 2")
            arcpy.CalculateField_management("lyr2", "gridcode", "Grid(!gridcode!)", "PYTHON_9.3", codeblock2)


            #clear all selections
            arcpy.SelectLayerByAttribute_management("lyr", "CLEAR_SELECTION")
            arcpy.SelectLayerByAttribute_management("lyr2", "CLEAR_SELECTION")


            #add a join between select feature class and original feature class
            print "adding join between tables..."
            arcpy.AddJoin_management("lyr", "Id", "lyr2", "Id")

            #recalculate gridcodes of original feature class based off of gridcodes from select layer based on the join relationship
            print "calculating the gridcode based off of the join to the original vegetation table..."
            arcpy.CalculateField_management("lyr", fc[:-4] + "_intersect.gridcode", expression5, "PYTHON_9.3", codeblock3)
            arcpy.RemoveJoin_management("lyr")
            arcpy.SelectLayerByAttribute_management("lyr", "CLEAR_SELECTION")
            #remove the join and copy all features to a new feature class
            print "copying featues from vegetation layer to new cleaned dataset"
            arcpy.CopyFeatures_management("lyr", ws + '\\' + fc[:-4] + '_cleaned')
            arcpy.Delete_management(FC_select)
        



            
            FC_Cleaned = ws + '\\' + fc[:-4] + "_cleaned"
        
            expression6 = "val(!" + fc[:-4] + "_cleaned.gridcode!, !" + fc[:-4] + "_select23_500.gridcode!)"

            #grab classes 2 and 3 from select feature class that are smaller or equal to 500 sqft
            print "round 2: Selecting classes 2 and three that are less than 500 sq ft..."
            arcpy.Select_analysis(FC_Cleaned, ws + '\\' + fc[:-4] + '_select23_500', "gridcode >=2 AND Shape_Area <= 500")
            FC_select2 = ws + '\\' + fc[:-4] + '_select23_500'

            #select by location of selection class near class 3 that's larger than 500 sqft of original veg layer
            print "selecting class three that is larger than 500 sqft from original veg layer"
            arcpy.MakeFeatureLayer_management(FC_Cleaned, "lyr3")
            arcpy.SelectLayerByAttribute_management("lyr3", "NEW_SELECTION", "gridcode = 3 AND Shape_Area > 500")



            arcpy.MakeFeatureLayer_management(FC_select2, "lyr4")


            #grab polys from select feature class near class 3 that's larger than 500 sq ft in original feacture class and switch them to class 3 and inverse to class 1 if they are not near class in original veg layer            
            print "grabbing layers from selection class near turf from original veg class and calculating gridcode values on selection class..."
            arcpy.SelectLayerByLocation_management("lyr4", "intersect", "lyr3", 1, "new_selection")
            arcpy.CalculateField_management("lyr4", "gridcode", "Grid(!gridcode!)", "PYTHON_9.3", codeblock)

            print "select remaining class 2 values from selection class and calculate their gridcode values..."
            arcpy.SelectLayerByAttribute_management("lyr4", "NEW_SELECTION", "gridcode = 2")
            arcpy.CalculateField_management("lyr4", "gridcode", "Grid(!gridcode!)", "PYTHON_9.3", codeblock2)
            
            
            arcpy.SelectLayerByAttribute_management("lyr3", "CLEAR_SELECTION")
            arcpy.SelectLayerByAttribute_management("lyr4", "CLEAR_SELECTION")


            #join original feature class to select feature class and change the gridcode values, copy all features to ouput cleaned class
            print "join original layer to select veg layer and finalize recalculated gridcode results..."
            arcpy.AddJoin_management("lyr3", "Id", "lyr4", "Id")
            arcpy.CalculateField_management("lyr3", fc[:-4] + "_cleaned.gridcode", expression6, "PYTHON_9.3", codeblock3)
            arcpy.RemoveJoin_management("lyr3")
            arcpy.SelectLayerByAttribute_management("lyr3", "CLEAR_SELECTION")
        
            print "Copy final features from original veg layer to new cleaned 2 layer"
            arcpy.CopyFeatures_management("lyr3", ws + '\\' + fc[:-4] + '_cleaned2')
            arcpy.Delete_management(FC_select2)









            FC_Cleaned2 = ws + '\\' + fc[:-4] + '_cleaned2'
        
            expression11 = "val(!" + fc[:-4] + "_cleaned2.gridcode!, !" + fc[:-4] + "_select2.gridcode!)"
            arcpy.Select_analysis(FC_Cleaned2, ws + '\\' + fc[:-4] + '_select2', "gridcode = 2")
            FC_select3 = ws + '\\' + fc[:-4] + '_select2'

        
        
            #selecting class 3 from the cleaned veg layer
            print "round 3: selecting class 3 from veg layer..."
            arcpy.MakeFeatureLayer_management(FC_Cleaned2, "lyr5")
            arcpy.SelectLayerByAttribute_management("lyr5", "NEW_SELECTION", "gridcode = 3")


            #select from the selection veg layer that's near class 3 from the original veg layer and recalculate its value to class 3
            print "select remaining class 2 near class of original veg layer and calculate gridcode..."
            arcpy.MakeFeatureLayer_management(FC_select3, "lyr6")
            arcpy.SelectLayerByLocation_management("lyr6", "intersect", "lyr5", 1, "new_selection")
            arcpy.CalculateField_management("lyr6", "gridcode", "Grid(!gridcode!)", "PYTHON_9.3", codeblock)



            #select the remaining class 2 from the selection veg layer and recalculate its field to class 1
            print "select remaining class 2 layer and recalculate it to the tree class..." 
            arcpy.SelectLayerByAttribute_management("lyr6", "NEW_SELECTION", "gridcode = 2")
            arcpy.CalculateField_management("lyr6", "gridcode", "Grid(!gridcode!)", "PYTHON_9.3", codeblock2)

            arcpy.SelectLayerByAttribute_management("lyr5", "CLEAR_SELECTION")
            arcpy.SelectLayerByAttribute_management("lyr6", "CLEAR_SELECTION")

            #join the original veg layer to the selection veg layer and recalculate the original gridcode values of the original veg layers based on the join
            #with the selection veg layer
            print "calculate reclasses class 2 polygons in the original veg layer..."
            arcpy.AddJoin_management("lyr5", "ID", "lyr6", "ID")
            arcpy.CalculateField_management("lyr5", st[:-4] + "_cleaned2.gridcode", expression11, "PYTHON_9.3", codeblock3)
            arcpy.RemoveJoin_management("lyr5")
            arcpy.SelectLayerByAttribute_management("lyr5", "CLEAR_SELECTION")
        
            #copy the features from the cleaned 2 feature to the cleaned3 feature class
            arcpy.CopyFeatures_management("lyr5", ws + '\\' + fc[:-4] + '_cleaned3')
            arcpy.Delete_management(FC_select3)

            FC_Cleaned3 = ws + '\\' + fc[:-4] + '_cleaned3'

            expression12 = "val(!" + fc[:-4] + "_cleaned3.gridcode!, !" + fc[:-4] + "_select2F.gridcode!)"

            print "round 4: selecting class 3 with an area less than 200 sq"
            #select from the cleaned 3 feature class where gridcode = 3 and the area is less than or equal to 200 sq ft
            arcpy.Select_analysis(FC_Cleaned3, ws + '\\' + fc[:-4] + '_select2F', "gridcode = 3 AND Shape_Area <= 200")

            FC_select2f = ws + '\\' +  fc[:-4] + '_select2f'

            #select the attributes from the selection of class 3 based on the location to the to the original class 
            arcpy.MakeFeatureLayer_management(FC_Cleaned3, "lyr7")
            arcpy.SelectLayerByAttribute_management("lyr7", "NEW_SELECTION", "gridcode = 3 AND Shape_Area > 200")
            arcpy.MakeFeatureLayer_management(FC_select2f, "lyr8")

            arcpy.SelectLayerByLocation_management("lyr8", "intersect", "lyr7", 1, "new_selection")

            #calculate the values of the gridcode to class 4 if they are equal to class 3
            arcpy.CalculateField_management("lyr8", "gridcode", "Grid(!gridcode!)", "PYTHON_9.3", codeblock4)

            #select values from where the gridcode is equal to class 3, and reclass them to class 1
            print "selecting class 3 from orig veg near remaining class 2 from select layer and reclassing the class 2 to 3..."
            arcpy.SelectLayerByAttribute_management("lyr8", "NEW_SELECTION", "gridcode = 3")
            arcpy.CalculateField_management("lyr8", "gridcode", "Grid(!gridcode!)", "PYTHON_9.3", codeblock2)

            #select class 4 and move it to class
            print "selecting class 4 and moving them to class 3..."
            arcpy.SelectLayerByAttribute_management("lyr8", "NEW_SELECTION", "gridcode = 4")
            #calculate new gridcode field
            arcpy.CalculateField_management("lyr8", "gridcode", "Grid(!gridcode!)", "PYTHON_9.3", codeblock)
            arcpy.SelectLayerByAttribute_management("lyr7", "CLEAR_SELECTION")
            arcpy.SelectLayerByAttribute_management("lyr8", "CLEAR_SELECTION")

        


            #join the original layer to the new selection layer and execute the codeblock to recalculate the original values of cleaned3 with the selection veg layer
            arcpy.AddJoin_management("lyr7", "Id", "lyr8", "Id")
            arcpy.CalculateField_management("lyr7", st[:-4] + "_cleaned3.gridcode", expression12, "PYTHON_9.3", codeblock3)
            arcpy.RemoveJoin_management("lyr7")
            arcpy.SelectLayerByAttribute_management("lyr7", "CLEAR_SELECTION")
        
            #after removing the last join, copy all features to the new _cleanedFinal feature class
            arcpy.CopyFeatures_management("lyr7", output + '\\' + fc[:-4] + '_cleanedFinal')
            arcpy.Delete_management(FC_select2f)
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
            











