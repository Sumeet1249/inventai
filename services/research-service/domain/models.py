from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    abstract = Column(Text, nullable=False)
    url = Column(String)
    published_date = Column(DateTime)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Processing")
    
    # Relationships
    authors = relationship("Author", back_populates="paper", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="paper", cascade="all, delete-orphan")
    analysis_results = relationship("Analysis", back_populates="paper", cascade="all, delete-orphan")

class Author(Base):
    __tablename__ = "authors"

    id = Column(String, primary_key=True, default=generate_uuid)
    paper_id = Column(String, ForeignKey("research_papers.id"))
    name = Column(String, nullable=False)
    affiliation = Column(String)

    paper = relationship("ResearchPaper", back_populates="authors")

class Document(Base):
    """Represents the parsed content and chunks of a research paper"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    paper_id = Column(String, ForeignKey("research_papers.id"))
    content = Column(Text, nullable=False)
    chunks = Column(JSON, nullable=False) # List of extracted chunk metadata
    vector_indexed = Column(String, default="Pending")

    paper = relationship("ResearchPaper", back_populates="documents")

class Analysis(Base):
    """Stores AI-generated analysis like Summaries and Q&A"""
    __tablename__ = "analysis"

    id = Column(String, primary_key=True, default=generate_uuid)
    paper_id = Column(String, ForeignKey("research_papers.id"))
    analysis_type = Column(String, nullable=False) # e.g., "summary", "qa"
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("ResearchPaper", back_populates="analysis_results")
