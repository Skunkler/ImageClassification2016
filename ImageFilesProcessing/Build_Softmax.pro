;This script was written by Warren Kunkler in support of the 2016 Clark County Image Classification Project
;For the Water Smart Landscape program 
;This script outputs a classifier constructed using the Softmax Regression and a gradient Descent trainer
;This script also outputs a loss profile and confusion matrix to allow the user to track the accuracy of the algorithm and gives the user the
;open to update variables to optimize the algorithm before executing it in batch mode accross different tiles of imagery




pro Build_Softmax
compile_opt idl2


e=envi(/headless)

;pulls the sample image mosaic and the ROI xml file
file = FILEPATH('northern_area_mosaick.img', root = 'E:\', subdirectory = ['Imagery_ENVI_SupervisedTests', 'mosaick_stacked_imagery', 'Mosaic_output'])
raster = e.openraster(file)

ROIFile = FILEPATH('rois_svm_soft.xml', root = 'E:\', subdirectory = ['Imagery_ENVI_SupervisedTests', 'mosaick_stacked_imagery', 'Mosaic_output'])
rois = e.openroi(ROIFile)


;extracts statistics from the raster roi samples
print, "extracting rois"
extractTask = ENVITask('ExtractExamplesFromRaster')
extractTask.INPUT_RASTER = raster
extractTask.INPUT_ROIS = rois
extractTask.Execute
outExamples = extractTask.OUTPUT_EXAMPLES

print, "normalizing data"


;applies a gain offset to the statistics
normalizeTask = ENVITask('ApplyGainOffsetToExamples')
normalizeTask.INPUT_EXAMPLES = outExamples
normalizeTask.Execute
gain = normalizeTask.OUTPUT_GAIN
offset = normalizeTask.OUTPUT_OFFSET
normalizedExamples = normalizeTask.OUTPUT_EXAMPLES
Print, 'Gain: ',gain
Print, 'Offset: ',offset


;shuffles the pulled ROI statistics
print, "shuffling samples"
shuffleTask = ENVITask('ShuffleExamples')
shuffleTask.INPUT_EXAMPLES = normalizedExamples
shuffleTask.Execute
shuffledExamples = shuffleTask.OUTPUT_EXAMPLES

print, "splitting rois"

;splits the ROIs with 80% being applied to training the classifier and 20% being used as a validation set
splitTask = ENVITask('SplitExamples')
splitTask.INPUT_EXAMPLES = shuffledExamples
splitTask.SPLIT_FRACTION = 0.8
splitTask.Execute
splitExamples = splitTask.OUTPUT_EXAMPLES


;creates the softmax regression classifier, creates the gradient descent trainer, trains the classifier
print, "creating softmax regression classifier"
softmaxTask = ENVITask('CreateSoftmaxRegressionClassifier')
softmaxTask.CLASS_NAMES = outExamples.CLASS_NAMES
softmaxTask.NATTRIBUTES = outExamples.NATTRIBUTES
softmaxTask.NCLASSES = outExamples.NCLASSES
softmaxTask.Execute
print, "creating gradient descent trainer"
GDTask = ENVITask('CreateGradientDescentTrainer')
GDTask.CONVERGENCE_CRITERION = 1e-7
GDTask.LEARNING_RATE = 100
GDTask.MAXIMUM_ITERATIONS = 150
GDTask.Execute
print, "training classifier"
trainTask = ENVITask('TrainClassifier')
trainTask.CLASSIFIER = softmaxTask.OUTPUT_CLASSIFIER
trainTask.EXAMPLES = splitExamples[0]
trainTask.TRAINER = GDTask.OUTPUT_TRAINER
trainTask.Execute
lossProfile = trainTask.LOSS_PROFILE
classifier = trainTask.TRAINED_CLASSIFIER

;outputs the EPO file that can be used to classify all images
classifierURI = 'E:\Imagery_ENVI_SupervisedTests\mosaick_stacked_imagery\Mosaic_output\TrainedSoftmaxClassifierTasks5.epo'
classifier.Save, URI=classifierURI



; Plot a loss profile and make adjustments as needed
p = PLOT(lossProfile, $
  TITLE='Loss Profile', $
  XTITLE='Iterations', $
  YTITLE='Loss', $
  COLOR='red', $
  THICK=2)

; Evaluate the result
evaluateTask = ENVITask('EvaluateClassifier')
evaluateTask.CLASSIFIER = classifier
evaluateTask.EXAMPLES = splitExamples[1]
evaluateTask.Execute
confusionMatrix = evaluateTask.OUTPUT_CONFUSION_MATRIX

; Print the confusion matrix
Print, confusionMatrix

; Print the column totals
columnTotals = confusionMatrix.ColumnTotals()
FOR i=0, (softmaxTask.NCLASSES)-1 DO $
  Print, 'Ground truth total for ', $
  softmaxTask.CLASS_NAMES[i],': ', $
  columnTotals[i]

; Print the row totals
rowTotals = confusionMatrix.RowTotals()
FOR i=0, (softmaxTask.NCLASSES)-1 DO $
  Print, 'Predicted total for ', $
  softmaxTask.CLASS_NAMES[i],': ', $
  rowTotals[i]

; Print the accuracy metrics
accuracy = confusionMatrix.Accuracy()
Print, 'Overall accuracy: ', accuracy
kappa = confusionMatrix.KappaCoefficient()
Print, 'Kappa coefficient: ', kappa
commissionError = confusionMatrix.CommissionError()
Print, 'Error of commission: ', commissionError
omissionError = confusionMatrix.OmissionError()
Print, 'Error of omission: ', omissionError
F1 = confusionMatrix.F1()
Print, 'F1 value: ', F1
precision = confusionMatrix.Precision()
Print, 'Precision: ', precision
producerAccuracy = confusionMatrix.ProducerAccuracy()
Print, 'Producer accuracy: ', producerAccuracy
recall = confusionMatrix.Recall()
Print, 'Recall: ', recall
userAccuracy = confusionMatrix.UserAccuracy()
Print, 'User accuracy: ', userAccuracy


END