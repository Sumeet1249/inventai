from fastapi import FastAPI
from app.database import engine, Base
from app.api.v1.auth_routes import router as auth_router

# Create database tables on startup (In production, use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="InventAI Enterprise Auth Service")

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "Auth Service Online"}
