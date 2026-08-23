"""
BOM Service - Bill of Materials Generation & Component Sourcing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Responsibilities:
1. Extract BOM from circuit/CAD designs
2. Normalize component requirements
3. Search for real products
4. Match products to requirements
5. Generate shopping lists
6. Calculate costs and optimize
7. Handle component substitutions
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BOM & Component Sourcing Service")


# ────────────── DATA MODELS ──────────────
class ComponentSpec(BaseModel):
    """Normalized component specification"""
    category: str  # MCU, Sensor, Display, Resistor, etc.
    name: str
    variant: Optional[str] = None
    voltage: Optional[str] = None
    interface: Optional[List[str]] = None  # I2C, SPI, UART, etc.
    package: Optional[str] = None  # DIP, SMD, BGA, etc.
    quantity: int = 1
    is_required: bool = True
    description: Optional[str] = None
    specs: Dict[str, Any] = {}


class BOMItem(BaseModel):
    """Bill of Materials item"""
    id: str
    component: ComponentSpec
    design_ref: Optional[str] = None  # Reference in circuit/PCB
    pin_mapping: Optional[Dict[str, str]] = None
    position: Optional[Dict[str, float]] = None  # X, Y, Z on PCB
    notes: Optional[str] = None


class BOM(BaseModel):
    """Complete Bill of Materials"""
    project_id: str
    design_id: str
    timestamp: str
    items: List[BOMItem]
    total_components: int
    required_count: int
    optional_count: int
    estimated_cost: Optional[float] = None
    cost_currency: str = "INR"


class BOMRequest(BaseModel):
    """Request model for BOM generation"""
    project_id: str
    design_id: str
    circuit_data: Optional[Dict[str, Any]] = None
    cad_data: Optional[Dict[str, Any]] = None


# ────────────── BOM EXTRACTION ──────────────
class BOMExtractor:
    """Extract BOM from circuit and CAD designs"""

    def __init__(self):
        self.component_categories = {
            "MCU": ["ESP32", "Arduino", "STM32", "ARM", "Microcontroller"],
            "Sensor": ["BME280", "DHT22", "MPU6050", "Accelerometer", "Temperature"],
            "Display": ["OLED", "LCD", "SSD1306", "LED", "Screen"],
            "Power": ["Regulator", "Buck", "Boost", "LDO", "Supply"],
            "Resistor": ["Ω", "Ohm", "R"],
            "Capacitor": ["μF", "nF", "pF", "uF", "Cap"],
            "Inductor": ["H", "mH", "uH"],
            "Diode": ["Diode", "LED", "Zener"],
            "Transistor": ["BJT", "MOSFET", "FET", "Transistor"],
            "Connector": ["USB", "JST", "Header", "Socket", "Pin"],
            "Motor": ["Motor", "Stepper", "Servo"],
            "Actuator": ["Relay", "Solenoid"],
            "PCB": ["PCB", "Board"],
            "Mechanical": ["Screw", "Nut", "Standoff", "Enclosure"]
        }

    def extract_from_circuit(self, circuit_data: Dict[str, Any]) -> List[ComponentSpec]:
        """Extract components from circuit schematic"""
        components = []
        
        # Parse circuit components
        if "components" in circuit_data:
            logger.info(f"Circuit data received: {circuit_data}")
            for comp in circuit_data["components"]:
                logger.info(f"Processing component: {comp} (type: {type(comp)})")
                spec = self._normalize_component(comp)
                if spec:
                    components.append(spec)
        
        logger.info(f"Extracted {len(components)} components from circuit")
        return components

    def extract_from_cad(self, cad_data: Dict[str, Any]) -> List[ComponentSpec]:
        """Extract components from CAD model (mechanical parts)"""
        components = []
        
        if "bom" in cad_data:
            for item in cad_data["bom"]:
                spec = self._normalize_component(item)
                if spec:
                    components.append(spec)
        
        logger.info(f"Extracted {len(components)} components from CAD")
        return components

    def _normalize_component(self, comp_data: Dict[str, Any]) -> Optional[ComponentSpec]:
        """Normalize component into standard specification"""
        try:
            name = comp_data.get("name", "")
            value = comp_data.get("value", "")
            quantity = int(comp_data.get("quantity", 1))
            
            category = self._categorize(name, value)
            
            return ComponentSpec(
                category=category,
                name=name,
                variant=comp_data.get("variant"),
                voltage=comp_data.get("voltage"),
                interface=comp_data.get("interface", []),
                package=comp_data.get("package"),
                quantity=quantity,
                is_required=comp_data.get("required", True),
                description=comp_data.get("description"),
                specs=comp_data.get("specs", {})
            )
        except Exception as e:
            logger.warning(f"Failed to normalize component: {e}")
            return None

    def _categorize(self, name: str, value: str = "") -> str:
        """Categorize component by name and value"""
        text = f"{name} {value}".upper()
        
        for category, keywords in self.component_categories.items():
            if any(kw.upper() in text for kw in keywords):
                return category
        
        return "Other"


# ────────────── BOM GENERATION ──────────────
class BOMGenerator:
    """Generate BOM from design data"""

    def __init__(self):
        self.extractor = BOMExtractor()

    async def generate_bom(self, 
                          project_id: str,
                          design_id: str,
                          circuit_data: Optional[Dict] = None,
                          cad_data: Optional[Dict] = None) -> BOM:
        """Generate complete BOM from circuit and CAD"""
        
        components = []
        
        # Extract from circuit
        if circuit_data:
            circuit_comps = self.extractor.extract_from_circuit(circuit_data)
            components.extend(circuit_comps)
        
        # Extract from CAD
        if cad_data:
            cad_comps = self.extractor.extract_from_cad(cad_data)
            components.extend(cad_comps)
        
        # Merge duplicate components
        merged = self._merge_components(components)
        
        # Create BOM items
        bom_items = []
        for i, comp in enumerate(merged):
            item = BOMItem(
                id=f"bom_item_{i}",
                component=comp,
                design_ref=None,
                pin_mapping=None,
                position=None
            )
            bom_items.append(item)
        
        # Calculate statistics
        required = sum(1 for item in bom_items if item.component.is_required)
        optional = len(bom_items) - required
        
        bom = BOM(
            project_id=project_id,
            design_id=design_id,
            timestamp=datetime.now().isoformat(),
            items=bom_items,
            total_components=len(bom_items),
            required_count=required,
            optional_count=optional
        )
        
        logger.info(f"Generated BOM with {len(bom_items)} items")
        return bom

    def _merge_components(self, components: List[ComponentSpec]) -> List[ComponentSpec]:
        """Merge duplicate components and sum quantities"""
        merged_dict = {}
        
        for comp in components:
            key = (comp.category, comp.name, comp.variant or "")
            
            if key in merged_dict:
                merged_dict[key].quantity += comp.quantity
            else:
                merged_dict[key] = comp
        
        return list(merged_dict.values())


# ────────────── API ENDPOINTS ──────────────
@app.post("/api/bom/generate")
async def generate_bom(request: BOMRequest) -> BOM:
    """Generate BOM from circuit and CAD designs"""
    try:
        generator = BOMGenerator()
        bom = await generator.generate_bom(
            project_id=request.project_id,
            design_id=request.design_id,
            circuit_data=request.circuit_data,
            cad_data=request.cad_data
        )
        return bom
    except Exception as e:
        logger.error(f"BOM generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bom/{project_id}")
async def get_bom(project_id: str) -> Dict[str, Any]:
    """Retrieve previously generated BOM"""
    return {
        "project_id": project_id,
        "message": "BOM retrieval from cache - database integration needed"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
