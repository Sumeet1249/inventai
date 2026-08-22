from fastapi import FastAPI
from services.patent_service.api.routers import router

app = FastAPI(title="InventAI Patent Service")

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "healthy"}
