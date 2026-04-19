from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tempfile

from scripts import extract_text_from_pdf
from extract_agent import extract_paper_meaning
from search import search_arxiv
from grouping_agent import group_papers
from editing_agent import run_editor, validate_editor_output
from build_pdf import build_pdf



app = FastAPI()

Path("static").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process")
async def process(file: UploadFile = File(...)):
    """Step 1: extract meaning, search arxiv, group papers."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        print("[1/3] Extracting text...")
        text = extract_text_from_pdf(tmp_path)

        print("[2/3] Extracting meaning...")
        meaning = extract_paper_meaning(text)

        print("[3/3] Searching + grouping...")
        papers = search_arxiv(meaning, max_results=10)
        groups = group_papers(papers)

        return {
            "meaning": meaning,
            "papers":  papers,
            "groups":  groups,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/build")
async def build(data: dict):
    """Step 2: run editor + build PDF. Takes output from /process as body."""
    try:
        papers = data["papers"]
        groups = data["groups"]

        print("[1/2] Running editor...")
        sections = run_editor(papers, groups)
        sections = validate_editor_output(sections, groups["reading_order"])

        print("[2/2] Building PDF...")
        output_path = "static/output.pdf"
        build_pdf(sections["sections"], papers, output_path=output_path)

        return {"pdf_url": "/static/output.pdf"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}