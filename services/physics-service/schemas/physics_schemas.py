from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SimulationRequest(BaseModel):
    cad_model_id: str
    simulation_type: str = Field(description="'stress' or 'thermal'")
    boundary_conditions: Dict[str, Any]
    material_id: str

class SimulationResultSchema(BaseModel):
    id: str
    simulation_id: str
    max_stress: Optional[float] = None
    max_temperature: Optional[float] = None
    safety_factor: Optional[float] = None
    metrics: Dict[str, Any]
    
    class Config:
        orm_mode = True
