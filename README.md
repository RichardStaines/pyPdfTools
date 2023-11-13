# pyPdfTools
Tools for Processing pdf files

This tool processes a folder of pdf files.

python pdfExtractBlock -t targetFolder -s "Risks and challenges" -e "FAQ" folderORfilename

e.g.
python pdfExtractBlock -t output -s "Risks and challenges" -e "FAQ" data

Parameters:
-t targetFolder - where the output files will be written (defaults to same as source)
-s startMarker - start the extraction when it finds this in the text of the pdf (inclusive)
-e endMarker - end the extraction when it finds this in the text of the pdf (exclusive)
folderORfilename - the pdf filename to process or a folder containing pdf files. It will process all .pdf files it finds in the folder.

Output: 
A .txt file will be created with the same filename root as the input file. It will be created in the taret-folder if specified otherwise in the same folder as the original pdf file.


