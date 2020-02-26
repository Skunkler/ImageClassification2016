;This Script was written by Warren Kunkler in support of the Clark County Image Classification project
;This script was designed to create an 8 band custom stack that would be used to supplement the Softmax Regression Classifier
;This same script created the 8 band stacked imager that were later mosaicked together and used as a training site for the gradient descent trainer



PRO CustomBand_Stack
;uses the standard IDL2 compile option that standardizes various datatypes
compile_opt IDL2


E = envi(/headless)
input='H:\2017_3_inch_samples'

File_raw_images = FILE_Search(input, '*.tif')
output_dir = input + '\output_stacks\'
File_MKDIR, output_dir


;loops through all 4 band images
foreach file, File_raw_images do begin
  base_out = output_dir
  
  
  ;opens the 4 band image and stores it in an object variable as well as grabs the feature ID
  raster = e.openraster(file)
  FID =  ENVIRASTERTOFID(raster[0])
  
  ;tests to see if feature ID is valid, if not close the image file and loop to the next image
  if(fid eq -1) then begin
    e.close
    return
    endif
    
    
    ;stores the coordinate ESPG code for Nevada State Plane as we'll need this later
    Coord = ENVICoordSys(COORD_SYS_CODE = 3421)
    
    ;grabs the image bands from the raster object
    ImageBands = raster[0]
    NIR_Band = ImageBands.GetData(bands=[3])
    Blue_Band = ImageBands.GetData(bands=[2])
    Green_Band = ImageBands.GetData(bands=[1])
    Red_Band = ImageBands.GetData(bands=[0]) 
    
    ;calculates the NDVI value that is stored as an array
    NDVI_Result = (float(NIR_Band)-float(Red_Band))/(float(NIR_Band)+float(Red_Band))
    
    ;saves the calculated NDVI array to an ENVI .dat raster file
    NDVI_Float_Raster = ENVIRASTER(NDVI_Result, URI = output_dir + 'NDVIFloat.dat')
    NDVI_Float_Raster.save
    NDVI_Float_Raster.close 
    
    ;opens the NDVI array and associated header file
    file_to_open = output_dir + 'NDVIFloat.dat'
    file_to_open_hdr = output_dir + 'NDVIFloat.hdr'
    
    
    ;creates an array of 0 values that are the same dimensions as the NDVI image
    Eight_bit = n_elements(NDVI_Result)
    
    ;converts the 0 values to 0.0 float values and copies the values from the NDVI array into the eight bit array
    imageArray = fltarr(Eight_bit)
    imageArray[*] = NDVI_Result
    
    ;calculates a min-max stretch
    min_value = min(imageArray, max=max_value)
    
    
    ;performs a linear range stretch on the raster image and then saves the stretched now unsigned 8 bit array to a temp file in a tif format
    raster_NDVI_Stretch = e.openraster(file_to_open, SPATIALREF_OVERRIDE = raster.spatialref)
    stretchNDVI = ENVILinearRangeStretchRaster(raster_NDVI_Stretch, MIN=min_value, MAX=max_value)
    
    TempFileOut_Name = FILE_Basename(file, '.tif')
    stretchNDVI.export, base_out + TempFileOut_Name + '_NDVI_temp.tif', 'TIFF'
    stretchNDVI.close
    raster_NDVI_Stretch.close
    
    Repro_file = base_out + TempFileOut_Name + '_NDVI_temp.tif'
    
    Repro_raster = e.openraster(Repro_file)
    
    ;reprojects the tiff raster image with the correct coordinate system that is in state plane
    Task = ENVITask('ReprojectRaster')
    Task.COORD_SYS = Coord
    Task.INPUT_RASTER = Repro_raster
    Task.OUTPUT_RASTER_URI = base_out + TempFileOut_Name + '_NDVI.dat'
    Task.Execute
    Repro_raster.close
    
    
    ;This section of the code calculates the occurance matrix for the mean statistic value on the green band and the homogeneous statistic on the blue band
    envi_open_file, file, r_fid=r_fid
    fid = ENVIRasterToFID(raster)
    ENVI_File_Query, fid, ns=ns, nl=nl, nb=nb
    dims = [-1l, 0, ns-1, 0, nl-1]
    outname = base_out + TempFileOut_Name + '_greenMean_statsTemp.dat'
    out_bname=['Mean']
    pos = [1]
    Method_CoOccur = [0,0,1,0,0,0,0,0]
    
    
    ENVI_DOIT, 'texture_stats_doit', fid=fid, pos=pos, dims=dims, $
      kx=5, ky=5, method=[0,1,0,0,0], $
      OUT_NAME=outname, R_FID=R_FID, out_bname=out_bname
    
    ENVI_DOIT, 'texture_cooccur_doit', fid=fid, $
      pos=pos, dims=dims, method=Method_CoOccur, kx=5, ky=5, $
      direction=[1,1], out_name=base_out + TempFileOut_Name + '_homog_statsTemp.dat', r_fid=r_fid
    
    
    ;calculates a Roberts filter on the blue band stores the data from this roberts filter array into a new image
    Sobimage = Roberts(Blue_Band)

    Image_export = ENVIRaster(Sobimage, URI = base_out + TempFileOut_Name + '_roberts.dat', SPATIALRef = raster.spatialref)
    image_export.save
    image_export.close
    
    
    
    NDVI_Band = base_out + TempFileOut_Name + '_NDVI.dat'
   
    FILE_DELETE, file_to_open
    FILE_DELETE, file_to_open_hdr  
    FILE_DELETE, Repro_file 
  
  
  ;open all the raster products
  NDVI_FILE = base_out + TempFileOut_Name + '_NDVI.dat'
  
  NDVI_Raster = e.openraster(NDVI_File)
  
  Spatial_Ref = raster.spatialref
  
  FiltFile =  base_out + TempFileOut_Name + '_filtered.dat'
  
  Filt_Image = e.openraster(base_out + TempFileOut_Name + '_roberts.dat', SPATIALREF_OVERRIDE = raster.spatialref)
  
  Homog_raster = e.openraster(base_out + TempFileOut_Name + '_homog_statsTemp.dat', SPATIALREF_OVERRIDE = raster.spatialref)
  
  Mean_Green_raster = e.openraster(base_out + TempFileOut_Name + '_greenMean_statsTemp.dat', SPATIALREF_OVERRIDE = raster.spatialref)
  
  ;stack the 4 band product with the 4 supplemental products in order to create a custom 8 band stack
  BandStack = ENVIMetaspectralRaster([NDVI_Raster, Homog_raster, Filt_Image, Mean_Green_raster], SPATIALREF = Spatial_Ref)
  BandStack.export, base_out + TempFileOut_Name + '_stacked_needsproj.dat', 'ENVI'
  Filt_Image.close
  NDVI_Raster.close
  
  ;reopen the .dat 8 band stack and reproject and output it to a tiff output
  Bandstack_file = base_out+TempFileOut_Name + '_stacked_needsproj.dat'
  orig_bandstack = e.openraster(Bandstack_file)
  Task.COORD_SYS = Coord
  Task.INPUT_RASTER = orig_bandstack
  Task.OUTPUT_RASTER_URI = base_out + TempFileOut_Name + '_stacked.tif'
  Task.Execute
  orig_bandstack.close
  
  ;delete the .dat 8 band stack files
  File_DELETE, Bandstack_file
  File_Delete, base_out + TempFileOut_Name + '_stacked_needsproj.hdr'
  
  
  
endforeach



e.close



END