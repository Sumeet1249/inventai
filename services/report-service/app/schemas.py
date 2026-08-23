"""
Pydantic schemas for Report Generation Service
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PatentOutput(BaseModel):
    """Patent agent output"""
    novelty_score: float = Field(default=85.0, description="Novelty score 0-100")
    fto_status: str = Field(default="CLEARED", description="FTO status: CLEARED, NEEDS_REVIEW, BLOCKED")
    white_space_summary: str = Field(default="", description="White space analysis summary")
    claims_draft: List[str] = Field(default_factory=list, description="Patent claims")
    prior_art_graph_url: Optional[str] = None


class PhysicsOutput(BaseModel):
    """Physics simulation agent output"""
    validation_status: str = Field(default="PASS", description="PASS or FAIL")
    safety_factor: float = Field(default=2.5, description="Safety factor")
    max_stress_mpa: float = Field(default=250.0, description="Maximum stress in MPa")
    yield_strength_mpa: float = Field(default=600.0, description="Yield strength in MPa")
    heatmap_image_url: Optional[str] = None
    simulation_summary: str = Field(default="", description="Physics analysis summary")


class CADOutput(BaseModel):
    """CAD design agent output"""
    format: str = Field(default="STEP", description="File format")
    dimensions: str = Field(default="", description="Dimensions description")
    render_image_url: Optional[str] = None
    step_file_url: Optional[str] = None
    assembly_summary: str = Field(default="", description="Assembly description")


class PCBOutput(BaseModel):
    """PCB design agent output"""
    board_specs: str = Field(default="", description="Board specifications")
    spice_status: str = Field(default="PASS", description="SPICE simulation status")
    layout_image_url: Optional[str] = None
    gerber_zip_url: Optional[str] = None
    schematic_summary: str = Field(default="", description="Schematic description")


class BOMItem(BaseModel):
    """Bill of Materials item"""
    item: str
    qty: int = 1
    cost: float
    supplier: Optional[str] = None
    lead_time_days: Optional[int] = None


class BusinessOutput(BaseModel):
    """Business analysis agent output"""
    total_cogs_usd: float = Field(default=5200.0, description="Total COGS in USD")
    target_msrp_usd: float = Field(default=12000.0, description="Target MSRP in USD")
    gross_margin_percent: float = Field(default=56.7, description="Gross margin %")
    bom_table: List[BOMItem] = Field(default_factory=list, description="Bill of Materials")
    financial_summary: str = Field(default="", description="Financial analysis summary")


class AgentOutputs(BaseModel):
    """Unified outputs from all agents"""
    patent: Optional[PatentOutput] = None
    physics: Optional[PhysicsOutput] = None
    cad: Optional[CADOutput] = None
    pcb: Optional[PCBOutput] = None
    business: Optional[BusinessOutput] = None


class ReportRequest(BaseModel):
    """Request to generate engineering report"""
    project_id: str = Field(..., description="Unique project identifier")
    project_title: str = Field(..., description="Project title")
    author: str = Field(default="InventAI Autonomous Engineering Platform")
    timestamp: Optional[datetime] = None
    agent_outputs: AgentOutputs = Field(..., description="Outputs from all agents")
    company_name: str = Field(default="InventAI", description="Company name for branding")
    logo_url: Optional[str] = None
    confidentiality_level: str = Field(default="CONFIDENTIAL", description="CONFIDENTIAL, INTERNAL, PUBLIC")


class ReportResponse(BaseModel):
    """Response with generated report URLs"""
    status: str = Field(default="success", description="success or error")
    project_id: str
    report_urls: Dict[str, str] = Field(default_factory=dict)
    generation_time_seconds: float = 0.0
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "ok"
    service: str = "report-service"
    version: str = "1.0.0"
