import arcpy
from arcpy import env




        


env.workspace = r"H:\missing_sets\workSpace.gdb"
ws = env.workspace

output = r"H:\missing_sets\workSpace.gdb"

env.overwriteOutput = True

fcs = arcpy.ListFeatureClasses()

codeblock = """def CalcYard(Type):
    if Type != 'BackYard' or Type != 'FrontYard':
        return 'N\A'"""

codeblock2 = """def CalcBackYard(lyr):
    return lyr"""



for fc in fcs:
    if fc[-11:] == "_calculated":

        print fc
       #selects Backyard data
        arcpy.Select_analysis(fc, ws + '\\' + fc[:-11] + '_backYards', " YardType = 'BackYard' ")
        arcpy.MakeFeatureLayer_management(fc[:-11] + '_backYards', "BackYard_lyr")
        arcpy.Dissolve_management("BackYard_lyr", ws + '\\' + fc[:-11] + '_BackDis', [fc[:-16] + '_intersect_APN'])

        #selects frontyard data
        arcpy.Select_analysis(fc, ws + '\\' + fc[:-11] + '_frontYard', " YardType = 'FrontYard' ")
        arcpy.MakeFeatureLayer_management(fc[:-11] + '_frontYard', 'FrontYard_lyr')
        arcpy.Dissolve_management('FrontYard_lyr', ws + '\\' + fc[:-11] + '_FrontDis', [fc[:-16] + '_intersect_APN'])


        #selects non-FB data
        arcpy.Select_analysis(fc, ws + '\\' + fc[:-11] + '_NonFB', " YardType IS NULL ")


        arcpy.MakeFeatureLayer_management(fc[:-11] + '_NonFB', 'NonFB_lyr')
        arcpy.CalculateField_management('NonFB_lyr', 'YardType', 'CalcYard(!YardType!)', 'PYTHON_9.3', codeblock)
        arcpy.Dissolve_management('NonFB_lyr', ws + '\\' + fc[:-11] + '_NonFB_dis', [fc[:-16] + '_intersect_APN'])

        #select nonSFR and dissolve
       
        arcpy.MakeFeatureLayer_management(fc, 'Select_lyr')
        arcpy.Dissolve_management('Select_lyr', ws + '\\' + fc + '_dissolve', [fc[:-16] + '_intersect_APN']) 
        arcpy.AddField_management(fc + '_dissolve', "FrontYard_Area", "DOUBLE")
        arcpy.AddField_management(fc + '_dissolve', "BackYard_Area", "DOUBLE")
        arcpy.AddField_management(fc + '_dissolve', "N\A_Area", "DOUBLE")

        arcpy.MakeFeatureLayer_management(fc[:-11] + "_BackDis", "BackYard_Dis_lyr")
        arcpy.MakeFeatureLayer_management(fc[:-11] + "_FrontDis", "FrontYard_Dis_lyr")
        arcpy.MakeFeatureLayer_management(fc[:-11] + "_NonFB_dis", "NonFB_dis_lyr")

        arcpy.MakeFeatureLayer_management(fc + "_dissolve", "SelectDis_lyr")
       


        arcpy.AddJoin_management("SelectDis_lyr", fc[:-16] + "_intersect_APN", "BackYard_Dis_lyr", fc[:-16] + "_intersect_APN")
        arcpy.SelectLayerByAttribute_management("SelectDis_lyr", "NEW_SELECTION", fc[:-11] + "_BackDis.Shape_Area IS NOT NULL")
        arcpy.CalculateField_management("SelectDis_lyr", fc + "_dissolve.BackYard_Area", "CalcBackYard(!" + fc[:-11] + "_BackDis.Shape_Area!)", "PYTHON_9.3", codeblock2)

        arcpy.SelectLayerByAttribute_management("SelectDis_lyr", "CLEAR_SELECTION")

        arcpy.RemoveJoin_management("SelectDis_lyr")
        arcpy.AddJoin_management("SelectDis_lyr", fc[:-16] + "_intersect_APN", "FrontYard_DIS_lyr", fc[:-16] + "_intersect_APN")
        arcpy.SelectLayerByAttribute_management("SelectDis_lyr", "NEW_SELECTION", fc[:-11] + "_FrontDis.Shape_Area IS NOT NULL")
        arcpy.CalculateField_management("SelectDis_lyr", fc + "_dissolve.FrontYard_Area", "CalcBackYard(!" + fc[:-11] + "_FrontDis.Shape_Area!)", "PYTHON_9.3", codeblock2)

        arcpy.SelectLayerByAttribute_management("SelectDis_lyr", "CLEAR_SELECTION")

        arcpy.RemoveJoin_management("SelectDis_lyr")
        arcpy.AddJoin_management("SelectDis_lyr", fc[:-16] + "_intersect_APN", "NonFB_Dis_lyr", fc[:-16] + "_intersect_APN")
        arcpy.SelectLayerByAttribute_management("SelectDis_lyr", "NEW_SELECTION", fc[:-11] + "_NonFB_dis.Shape_Area IS NOT NULL")
        arcpy.CalculateField_management("SelectDis_lyr", fc + "_dissolve.N_A_Area", "CalcBackYard(!" + fc[:-11] + "_NonFB_dis.Shape_Area!)", "PYTHON_9.3", codeblock2)

        arcpy.SelectLayerByAttribute_management("SelectDis_lyr", "CLEAR_SELECTION")
        arcpy.RemoveJoin_management("SelectDis_lyr")
        arcpy.CopyFeatures_management("SelectDis_lyr", output + '\\' + fc)
       
