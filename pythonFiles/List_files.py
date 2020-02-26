import os

TextFile = open('E:\\2016_ClarkCounty_imageryclassification\\classifiedImagery\\ListFiles.txt','w')
inputPath = 'E:\\2016_ClarkCounty_imageryclassification\\classifiedImagery\\corrected_input\\Tiff_Output'


for root, dirs, files in os.walk(inputPath):
    for filename in files:
        if filename[-4:] == ".tif":
            TextFile.write('\'{x}\',\n'.format(x = filename[1:-12]))
TextFile.close()
