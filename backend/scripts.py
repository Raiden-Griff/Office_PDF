'''

Scripts for PDF Editing

'''

from pypdf import PdfReader
from PyPDF2 import PdfMerger
import pdfplumber


def extract_text_from_pdf(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        return "\n\n".join(page.extract_text() for page in pdf.pages)

# def extract_text_from_pdf(file_path: str) -> str:
#     reader = PdfReader(file_path)

#     text = ""

#     for page in reader.pages:
#         page_text = page.extract_text()
#         if page_text:
#             text += page_text + "\n"

#     return text

def merge_pdfs(file_paths: list) -> str:
    """
    Takes a list of PDF file paths and merges them.
    Returns the output file path.
    """

    merger = PdfMerger()

    for path in file_paths:
        merger.append(path)

    output_path = "merged_output.pdf"
    merger.write(output_path)
    merger.close()

    return output_path