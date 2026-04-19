"""
Paper search pipeline
"""
import pdfplumber
from extract_agent import extract_paper_meaning
from search import search_arxiv
from grouping_agent import group_papers
from editing_agent import run_editor, validate_editor_output
from build_pdf import build_pdf


def extract_text_from_pdf(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        return "\n\n".join(page.extract_text() for page in pdf.pages)


def paper_search_pipeline(text: str, output_path: str = "static/output.pdf") -> dict:
    """
    Full pipeline from extracted PDF text to merged output PDF.
    
    Args:
        text: raw text extracted from the input paper
        output_path: where to save the final merged PDF
    
    Returns:
        dict with all intermediate outputs and the pdf path
    """

    print("[1/5] Extracting meaning...")
    meaning = extract_paper_meaning(text)

    print("[2/5] Searching ArXiv...")
    papers = search_arxiv(meaning, max_results=10)

    print("[3/5] Grouping papers...")
    groups = group_papers(papers)

    print("[4/5] Running editor...")
    sections = run_editor(papers, groups)
    sections = validate_editor_output(sections, groups["reading_order"])

    print("[5/5] Building PDF...")
    build_pdf(sections["sections"], papers, output_path=output_path)

    print(f"Done! PDF saved to {output_path}")

    return {
        "pdf_path":  output_path,
        "meaning":   meaning,
        "papers":    papers,
        "groups":    groups,
        "sections":  sections,
    }


if __name__ == "__main__":
    sample_text = """
    We propose a novel attention mechanism that reduces transformer complexity from O(n²) 
    to O(n log n) while maintaining performance on NLP benchmarks. Our method, Sparse Hierarchical 
    Attention (SHA), segments input sequences into hierarchical blocks and computes attention 
    within and across blocks selectively. Experiments on GLUE, SQuAD, and long-document tasks 
    show SHA matches full attention within 0.3% while cutting memory use by 60% on sequences 
    over 4096 tokens.
    """

    result = paper_search_pipeline(sample_text)