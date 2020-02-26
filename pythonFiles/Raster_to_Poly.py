#This script was written by Warren Kunkler in support of the Clark County Image Classification Project for 2016
#The goal of this project is to support the Water Smart Landscape project
#The output of this script is the vectorization of the thematic classified raster images that were created by the Softmax Regression Classifier


import arcpy, sys, datetime, time, os, string
from arcpy import env


#set up workspace environment and logpath
logpath = r'D:\RetroStudy\2008\logs'

env.overwriteOutput = True
ws = r'D:\RetroStudy\2014\2014_cleaned_round1\eliminate'
env.workspace = ws



scriptName = sys.argv[0]
logName = sys.argv[0].split('\\')[len(sys.argv[0].split("\\"))-1][0:-3]

logfile = logpath + '\\' + logName + '.log'
outfile = open(logfile, 'a')

outfile.write("\n" + "WORKSPACE: " + ws + "\n" + scriptName + "-----------------------------------------" + "\n")
outfile.close()


#define rasters and output workspace
output = r'D:\RetroStudy\2014\polys_temp.gdb'
rasters = arcpy.ListRasters("*","*")

#loop through rasters and convert each one to a polygon
for raster in rasters:
    try:
        print "converting: ", raster, " to polygon"
        Polys = output + '\\' + raster[:-4]   
        arcpy.RasterToPolygon_conversion(raster, Polys, "NO_SIMPLIFY", "VALUE")
    except:

        print arcpy.GetMessages(2)
        """print "Process failed for: " + raster
        outFail = open(logpath + "\\fail_" + logName + ".log", "a")
        outFail.write( "failed " + raster + "\n")
        
        print arcpy.GetMessages(2)
        ouch = arcpy.GetMessages(2)
        outfile.write(ouch + "\n")
        outfile.write("Process: Failed for: " + raster + " " + str(timeYearMonDay) + " " + str(timeHour) + ":" + str(timeMin) + "\n")

    outfile.close()


timeYearMonDay = datetime.date.today()
timeHour = time.localtime()[3]
timeMin = time.localtime()[4]


print "Process done! " + str(timeYearMonDay) +  " " + str(timeHour)+ ":"   + str(timeMin)
outfile= open(logfile,'a')
outfile.write("Process Complete "  + str(timeYearMonDay) +  " " + str(timeHour)+ ":"   + str(timeMin) +  '\n' )
outfile.close()"""
