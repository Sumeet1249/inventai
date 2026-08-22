import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Expects DATABASE_URL from .env or defaults to a local test db
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://inventai:supersecret@localhost:5432/inventai"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to inject DB session into FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
