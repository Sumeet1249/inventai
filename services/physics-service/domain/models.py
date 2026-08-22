from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String, primary_key=True, default=generate_uuid)
    cad_model_id = Column(String, nullable=False)
    simulation_type = Column(String, nullable=False) # e.g., "stress", "thermal"
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    boundary_conditions = Column(JSON, nullable=False)
    material_properties = Column(JSON, nullable=False)
    
    results = relationship("SimulationResult", back_populates="simulation", cascade="all, delete-orphan")

class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    simulation_id = Column(String, ForeignKey("simulations.id"))
    max_stress = Column(Float)
    max_temperature = Column(Float)
    safety_factor = Column(Float)
    metrics = Column(JSON) # Detailed map data
    
    simulation = relationship("Simulation", back_populates="results")
