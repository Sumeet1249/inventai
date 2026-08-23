from fastapi import FastAPI
from services.research_service.app.services.llama_index_service import ResearchRAGService

app = FastAPI(title="InventAI Research Service")
rag_service = ResearchRAGService()

@app.get("/search")
def search_research(q: str):
    return rag_service.query(q)

@app.get("/health")
def health():
    return {"status": "healthy"}
