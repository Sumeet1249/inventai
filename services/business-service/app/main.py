from fastapi import FastAPI
from services.business_service.app.api.routers import router
import os

app = FastAPI(
    title="InventAI Business Service",
    description="Business & Venture Agent for Financial BOM and Market Sizing",
    version="1.0.0"
)

# Create exports directory
os.makedirs("/tmp/business_exports", exist_ok=True)

app.include_router(router)
