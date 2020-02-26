import os

file_1 = r"E:\2016_ClarkCounty_imageryclassification\FinalDataSets\TreeFcS.csv"
file_2 = r"E:\2016_ClarkCounty_imageryclassification\FinalDataSets\TreeFcS_original.csv"

ReadFile1 = open(file_1, "r")
ReadFile2 = open(file_2, "r")


Processed_Files_List = []
Missing_Files_List = []

for line in ReadFile1.readlines():
    Processed_fcs = line.split(",")[1][5:10]
    Processed_Files_List.append(Processed_fcs)

for line2 in ReadFile2.readlines():
    PreProcessed_fcs = line2.split(",")[1][5:10]
    if PreProcessed_fcs not in Processed_Files_List:
        Missing_Files_List.append(line2.split(",")[1])

outfile = open(r"E:\2016_ClarkCounty_imageryclassification\FinalDataSets\MissingFiles.csv","w")

for file in Missing_Files_List:
    outfile.write(file)
outfile.close
