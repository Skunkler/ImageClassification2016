import os


imageList = []

input_one = r'E:/2016_ClarkCounty_imageryclassification/classifiedImagery/corrected_input/Tiff_Output'
input_two = r'H:/Imagery_from_79/test/NDVI_Outputs'
input_three = r'R:/Image_ClarkCounty/2016'



inputList1 = []
inputList2 = []
inputList3 = []

outFile = open(r'E:\2016_ClarkCounty_imageryclassification\NDVI_Filtering.bls', 'w')
outFile.write('PortInput1\tPortInput2\tPortInput3\n')


for root, dirs, files in os.walk(input_one):
    for filename in files:
        if filename[-4:] == ".tif":
            imageList.append(filename[:-12])
            Input_Line = '"{InputWorkSpace}/{InputFile}"'.format(InputWorkSpace = input_one, InputFile = filename)
            inputList1.append(Input_Line)


for root, dirs, files in os.walk(input_two):
    for filename in files:
        if filename[-4:] == ".tif":
            Input_Line = '"{InputWorkSpace}/{InputFile}"'.format(InputWorkSpace = input_two, InputFile = filename)
            inputList2.append(Input_Line)


for root, dirs, files in os.walk(input_three):
    for filename in files:
        if filename[-4:] == ".tif" and filename[:-4] in imageList:
            realRoot = input_three + '/' + root[-3:]
            Input_Line = '"{realRoot}/{InputFile}"'.format(realRoot = realRoot, InputFile = filename)
            inputList3.append(Input_Line)
inputList3.sort()

ListCount = len(inputList1)
for i in range(0, ListCount):
    
    
    Input1 = inputList1[i]
    Input2 = inputList2[i]
    Input3 = inputList3[i]
    line = Input1 + '\t' + Input2 + '\t' + Input3 + '\n'

    outFile.write(line)
outFile.close()
