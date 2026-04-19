import urllib.request
import os
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY
from pypdf import PdfWriter, PdfReader
import io

DOWNLOAD_DIR = Path("downloaded_papers")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def download_pdf(paper: dict) -> Path:
    """Download a paper PDF from ArXiv if not already cached."""
    arxiv_id = paper["arxiv_id"].split("/abs/")[-1]
    dest = DOWNLOAD_DIR / f"{arxiv_id.replace('/', '_')}.pdf"

    if dest.exists():
        print(f"  [cached] {paper['title'][:60]}")
        return dest

    url = f"https://arxiv.org/pdf/{arxiv_id}"
    print(f"  [downloading] {paper['title'][:60]}")
    urllib.request.urlretrieve(url, dest)
    return dest


def blurb_to_pdf(text: str) -> bytes:
    """Render a blurb string as a full A4 page PDF, returned as bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=3*cm, rightMargin=3*cm,
        topMargin=4*cm, bottomMargin=4*cm
    )

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=12,
        leading=20,
        alignment=TA_JUSTIFY,
        fontName="Times-Roman"
    )

    story = [Spacer(1, 2*cm)]
    for para in text.strip().split("\n\n"):
        story.append(Paragraph(para.strip(), body_style))
        story.append(Spacer(1, 0.5*cm))

    doc.build(story)
    return buf.getvalue()


def build_pdf(sections: list[dict], papers: list[dict], output_path: str = "static\\output.pdf"):
    """
    Merges blurbs and paper PDFs into a single document.
    sections: output from run_editor()["sections"]
    papers: indexed paper list from search_arxiv()
    """
    paper_lookup = {p["index"]: p for p in papers}
    writer = PdfWriter()

    for section in sections:
        if section["type"] == "blurb":
            print(f"  [blurb] {section['text'][:60]}...")
            pdf_bytes = blurb_to_pdf(section["text"])
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)

        elif section["type"] == "paper":
            paper = paper_lookup[section["paper_index"]]
            print(f"  [paper] {paper['title'][:60]}")
            pdf_path = download_pdf(paper)
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"\nDone! Saved to {output_path}")


if __name__ == "__main__":
    # sample — replace with real outputs from editor.py and search.py
    sample_sections = [
        {"type": "blurb",  "text": "This collection explores the evolution of attention mechanisms in transformers.\n\nWe begin with the foundational work before moving to efficiency improvements."},
        {"type": "paper",  "paper_index": 0},
        {"type": "blurb",  "text": "Having established the core transformer architecture, we now turn to sparse variants.\n\nThe following paper addresses the quadratic complexity bottleneck directly."},
        {"type": "paper",  "paper_index": 1},
        {"type": "blurb",  "text": "Taken together, these works chart a clear trajectory toward efficient, scalable attention.\n\nFuture work will likely combine hierarchical and sparse approaches."},
    ]

    sample_papers = [
        {"index": 0, "title": "Attention Is All You Need", "arxiv_id": "https://arxiv.org/abs/1706.03762"},
        {"index": 1, "title": "Sparse Transformers",       "arxiv_id": "https://arxiv.org/abs/1904.10509"},
    ]

    build_pdf(sample_sections, sample_papers)