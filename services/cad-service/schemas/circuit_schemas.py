from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Pin(BaseModel):
    id: str = Field(description="Unique identifier for the pin within the component, typically a number or alphanumeric string.")
    name: Optional[str] = Field(None, description="Name of the pin (e.g., VCC, GND, IN, OUT).")
    x: float = Field(0.0, description="X coordinate relative to the component center.")
    y: float = Field(0.0, description="Y coordinate relative to the component center.")

class Component(BaseModel):
    id: str = Field(description="Unique reference designator for the component (e.g., R1, U1).")
    value: str = Field(description="Value or part number of the component (e.g., 10k, NE555).")
    footprint: str = Field(description="KiCad footprint name (e.g., Resistor_SMD:R_0805_2012Metric).")
    x: float = Field(0.0, description="Absolute X position of the component on the PCB.")
    y: float = Field(0.0, description="Absolute Y position of the component on the PCB.")
    sch_x: float = Field(0.0, description="X coordinate of the component on the logical schematic (frontend UI).")
    sch_y: float = Field(0.0, description="Y coordinate of the component on the logical schematic (frontend UI).")
    rotation: float = Field(0.0, description="Rotation in degrees.")
    pins: List[Pin] = Field(default_factory=list, description="List of pins belonging to this component.")

class NetNode(BaseModel):
    component_id: str = Field(description="Reference designator of the component.")
    pin_id: str = Field(description="Pin ID on the component.")

class Net(BaseModel):
    id: int = Field(description="Unique integer ID for the net.")
    name: str = Field(description="Name of the net (e.g., +5V, GND, Net-(R1-Pad1)).")
    nodes: List[NetNode] = Field(default_factory=list, description="List of component pins connected to this net.")

class CircuitGraph(BaseModel):
    components: List[Component] = Field(default_factory=list, description="All components in the circuit.")
    nets: List[Net] = Field(default_factory=list, description="All electrical connections (nets) in the circuit.")
