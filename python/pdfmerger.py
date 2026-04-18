from pypdf import PdfReader, PdfWriter

def PopulatePdfs(pdfFilePathA : str, pdfFilePathB : str) :
    global pdfA
    global pdfB
    pdfA = PdfReader(pdfFilePathA)
    pdfB = PdfReader(pdfFilePathB)

def GetPageCountA() :
    return pdfA.get_num_pages

def GetPageCountB() :
    return pdfB.get_num_pages

def MergePdfs() :
    global mergedPdfs
    mergedPdfs = PdfWriter()
    

    with open("merged.pdf", "wb") as f:
        mergedPdfs.write(f)