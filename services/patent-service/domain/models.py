from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Patent(Base):
    __tablename__ = "patents"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    abstract = Column(Text, nullable=False)
    claims = Column(JSON, nullable=False)
    filing_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Pending")
    
    # Relationships
    inventors = relationship("Inventor", back_populates="patent", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="patent", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="patent", cascade="all, delete-orphan")

class Inventor(Base):
    __tablename__ = "inventors"

    id = Column(String, primary_key=True, default=generate_uuid)
    patent_id = Column(String, ForeignKey("patents.id"))
    name = Column(String, nullable=False)
    company = Column(String)

    patent = relationship("Patent", back_populates="inventors")

class Citation(Base):
    __tablename__ = "citations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    patent_id = Column(String, ForeignKey("patents.id"))
    cited_patent_number = Column(String, nullable=False)
    relevance_score = Column(String)

    patent = relationship("Patent", back_populates="citations")

class AnalysisResult(Base):
    """Stores AI-generated analysis like Novelty and Prior-Art"""
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    patent_id = Column(String, ForeignKey("patents.id"))
    analysis_type = Column(String, nullable=False) # e.g., "novelty", "prior_art"
    findings = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    patent = relationship("Patent", back_populates="analysis_results")
