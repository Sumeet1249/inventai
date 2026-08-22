from fastapi import FastAPI
from pydantic import BaseModel
from app.services.cadquery_script import CADGenerator

app = FastAPI(title="InventAI CAD Service")

class BracketParams(BaseModel):
    width: float
    height: float
    thickness: float

@app.post("/generate/bracket")
def generate_bracket(params: BracketParams):
    return CADGenerator.generate_bracket(params.width, params.height, params.thickness)

@app.get("/health")
def health():
    return {"status": "healthy"}
