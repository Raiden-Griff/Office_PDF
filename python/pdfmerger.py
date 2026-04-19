from pypdf import PdfReader, PdfWriter

global pdfs
global mergedPdfs
pdfs = [PdfReader("default.pdf")]
mergedPdfs = PdfWriter()

# Requirement: list of strings to filepaths
# Code must have access to such a path, and the files must be there
# Resets pdfs and mergedPdfs
def PopulatePdfs(pdfFilePaths : list[str]) :
    mergedPdfs = PdfWriter()
    pdfs.clear
    for filePath in pdfFilePaths:
        pdfs.append(PdfReader(filePath))

# Requirement: index of the pdf desired
# The order they were inserted should be known by you
def GetPageCount(indexOf : int) :
    return pdfs[indexOf].get_num_pages

# For convenience, creates a "merged.pdf" written with the contents of the mergedPdf
def WriteToFile() :
    with open("merged.pdf", "wb") as f:
        mergedPdfs.write(f)

# Requirements: same number of values in pdfIndexes and pagenumbers
# The pdf at index n should correlate with the page number at index n
# Always creates a file, even in error conditions
# PDF will just be empty (i think)
def MergePdfs(pdfIndexes : list[int], pageNumbers : list[int]) :
    if(len(pdfIndexes) != len(pageNumbers)) :
        WriteToFile()
        return
    
    if(len(pdfIndexes) == 0) :
        WriteToFile()
        return

    for iterator in range(len(pdfIndexes)) :
        mergedPdfs.add_page(pdfs[iterator].get_page(pageNumbers[iterator]))

    WriteToFile()
