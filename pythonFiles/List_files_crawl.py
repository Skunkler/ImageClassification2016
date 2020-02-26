import os

input_one = r'H:/Imagery_from_79/canopy_height/canopy_height'

input_two = r'E:/2016_ClarkCounty_imageryclassification/NDVI_filtered2'

OutFile = open(r'H:\Imagery_from_79\canopy_height\input_file2.bls', 'w')

OutFile.write("PortInput1\tPortInput2\n")

#List_filenames = []
List_portInput = []
List_portInput2 = []
Match_List = []


for root, dirs, files in os.walk(input_one):
    for filename in files:
        if filename[-4:] == '.img':
            Match_List.append(filename[:-10])
            Line_input = '"{InputWorkSpace}/{Input1_file}"'.format(InputWorkSpace = input_one, Input1_file = filename)
            List_portInput.append(Line_input)
            

for root, dirs, files in os.walk(input_two):
    for filename in files:
        if filename[-4:]== '.img' and filename[1:6] in Match_List:
            Line_input1 = '"{InputWorkSpace}/{Input2_file}"'.format(InputWorkSpace = input_two, Input2_file = filename)
            
            List_portInput2.append(Line_input1)
            #OutFile.write(Line_input1 + '\n')
            

ListCount = len(List_portInput)
for i in range(0, ListCount):
    Input1 = List_portInput[i]
    Input2 = List_portInput2[i]
    line = Input2 + '\t'+ Input1 + '\n'
    OutFile.write(line)

OutFile.close()
