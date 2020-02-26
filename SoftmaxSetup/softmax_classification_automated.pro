;This script was written by Warren Kunkler in support of the Clark County 2016 Image Classification Project
;The point of this script calls the EPO file and applies that to the custom 8 band stack and outputs a thematic classified with 3 classes
; Tree, vegetation in shadows, and turf


PRO Softmax_classification_test
compile_opt idl2
e=envi(/headless)



;pulls all the 8 band stacks
input = 'H:\Imagery_from_79\missing_imagery\output_stacks'
File_stacked_images = FILE_Search(input, '*.dat')

;pulls the epo file
classifier_uri = 'E:\Imagery_ENVI_SupervisedTests\mosaick_stacked_imagery\Mosaic_output\TrainedSoftmaxClassifierTasks4.epo'

;restores the data in the EPO and places it in an object
trainedClassifier = ENVIRestoreObject(classifier_uri)


;The arrays for the gain and offset values that were calculated by Softmax build script
Gain = [0.0060975610, 0.0061728395, 0.0060240964, 0.0056818182, 0.0065789474, 1.0000000, 0.0047846890, 0.0054359641]
Offset = [-0.52901123, -0.57575200, -0.46548277, -0.95872629, -1.2456980, -0.33215991, -0.032127138, -0.50781298]

;loops through each 8 band stack file
foreach file, File_stacked_images do begin
  ;opens the 8 band stack
  raster = e.openraster(file)
  
  ;apply the gain and offset to the raster image
  normalized_raster = ENVIGainOffsetRaster(raster, Gain, Offset)
  
  
  base_out = File_Basename(file, '.dat')
  outputPath = 'E:\2016_ClarkCounty_imageryclassification\classifiedImagery\corrected_input3\' + base_out + '.dat'
  
  ;classify each raster with the trained classifier object and output it with the correct classes and class names in the metadata
  classRaster = ENVIClassifyRaster(normalized_raster, trainedClassifier, OUTPUT_FILENAME = outputPath)


  numClasses = classRaster.Metadata['Classes']
  classNames = classRaster.Metadata['Class Names']
endforeach




END