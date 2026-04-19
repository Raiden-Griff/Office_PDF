from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import agent
import scripts

app = FastAPI()

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
    Summarizes the pdf given the path
    '''
    return agent.describe_text(pdf_path)

@app.get("/api/merge")
def merge(pdf_paths : list) -> str:
    '''
    Merges pdfs in order
    '''
    return scripts.merge_pdfs(pdf_paths)


