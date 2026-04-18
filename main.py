from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
    
@app.post("/example")
def example():
    return {"message": "This is an example POST endpoint."}
