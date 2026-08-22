from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class CADProject(Base):
    __tablename__ = "cad_projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    models = relationship("CADModel", back_populates="project", cascade="all, delete-orphan")

class CADModel(Base):
    __tablename__ = "cad_models"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("cad_projects.id"))
    name = Column(String, nullable=False)
    parameters = Column(JSON, nullable=False) # Extracted parameters from AI
    status = Column(String, default="Draft")
    
    volume = Column(Float)
    surface_area = Column(Float)
    
    project = relationship("CADProject", back_populates="models")
    exports = relationship("CADExport", back_populates="model", cascade="all, delete-orphan")

class CADExport(Base):
    __tablename__ = "cad_exports"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    model_id = Column(String, ForeignKey("cad_models.id"))
    format = Column(String, nullable=False) # STEP, STL, GLTF
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("CADModel", back_populates="exports")
