from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import backend.extract_agent as extract_agent
import scripts
import shutil, os

app = FastAPI()

# Create upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# allow Vite dev server to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI"}

@app.get("/api/summarize")
def summarize(pdf_path):
    ''' 
    Summarizes the pdf given the path, returns as mk
    '''
    return extract_agent.describe_text(pdf_path)

@app.get("/api/merge")
def merge(pdf_paths : list) -> str:
    '''
    Merges pdfs in order
    '''
    return scripts.merge_pdfs(pdf_paths)

# Recieves
@app.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    print("Upladoing")
    file_path = f"{UPLOAD_DIR}/{pdf.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(pdf.file, buffer)
    
    return {"filename": pdf.filename, "path": file_path}
