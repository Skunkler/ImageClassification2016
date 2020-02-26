;This script was written by Warren Kunkler in support of the 2016 Clark County Image Classification Project
;This script deletes all the auxiliary temp files from the 8 band custom stack creation that could not be deleted due to existing locks on the files
;while the previous script was still running

pro automate_delete_tempFiles

compile_opt idl2

;sets the root to the proper directory
root = 'H:\Imagery_from_79\missing_imagery\output_stacks'

;searches for all .dat files in that directory
image_files = File_Search(root, '*.dat')

foreach file, image_files do begin
  ;gives all users execute and write status so that the user can automatically delete all files that end in .dat from the directory
  file_chmod, file, /A_WRITE, /A_EXECUTE
  file_delete, file
endforeach


;grabs all header files for the roberts filter, NDVI, and statsTemp 
hdr_roberts_files = FILE_Search(root, '*roberts*')

hdr_NDVI_FILES = File_Search(root, '*NDVI*')

hdr_stats_Files = file_search(root, '*statsTemp*')


;deletes the header files
foreach file, hdr_roberts_files do begin
  file_delete, file
endforeach

foreach file, hdr_NDVI_FILES do begin
  file_delete, file
endforeach

foreach file, hdr_stats_Files do begin
  file_delete, file
endforeach




end