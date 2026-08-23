"""
Substitution Service - Component Alternatives & Compatibility Checking
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Responsibilities:
1. Find compatible component substitutes
2. Calculate compatibility scores
3. Identify missing/extra features
4. Provide substitution recommendations
5. Check electrical/mechanical compatibility
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Component Substitution Service")


# ────────────── DATA MODELS ──────────────
class ComponentSubstitution(BaseModel):
    """Component substitution record"""
    original_component: str
    substitute_component: str
    compatibility_score: float  # 0-100
    compatibility_notes: str
    missing_features: List[str]
    extra_features: List[str]
    impact_level: str  # "low", "medium", "high"
    can_substitute: bool
    warnings: Optional[List[str]] = None


class SubstitutionRequest(BaseModel):
    """Request for substitution suggestions"""
    component_name: str
    component_specs: Dict[str, Any]
    reason: str  # "unavailable", "cost_reduction", "compatibility"
    max_suggestions: int = 5


class SubstitutionRecommendation(BaseModel):
    """AI-generated substitution recommendation"""
    original: str
    alternatives: List[ComponentSubstitution]
    best_option: Optional[ComponentSubstitution] = None
    explanation: str
    design_impact: str


# ────────────── COMPATIBILITY CHECKER ──────────────
class CompatibilityChecker:
    """Check component compatibility"""

    # Define component compatibility matrices
    COMPONENT_FAMILIES = {
        "MCU": {
            "ESP32": ["ESP32-WROOM-32", "ESP32-WROVER", "ESP32-S3"],
            "Arduino": ["Uno", "Nano", "Mega"],
            "STM32": ["STM32F4", "STM32L0"],
        },
        "Sensor": {
            "Temperature": ["DS18B20", "DHT22", "BMP280", "BME280"],
            "IMU": ["MPU6050", "MPU9250", "ICM20689"],
            "Pressure": ["BMP280", "BME280", "BMP085"],
        },
        "Display": {
            "OLED": ["SSD1306", "SH1106"],
            "LCD": ["16x2", "20x4"],
            "LED_MATRIX": ["MAX7219"],
        },
        "Power": {
            "Regulator": ["AMS1117", "LM7805", "LDO"],
            "Buck": ["MP1584", "LM2596"],
        },
    }

    @staticmethod
    def check_voltage_compatibility(original_voltage: str, substitute_voltage: str) -> tuple:
        """Check if voltages are compatible"""
        try:
            orig_v = float(original_voltage.replace("V", ""))
            subs_v = float(substitute_voltage.replace("V", ""))

            # Allow ±10% voltage difference
            tolerance = orig_v * 0.1
            is_compatible = abs(orig_v - subs_v) <= tolerance

            return is_compatible, f"{substitute_voltage} vs {original_voltage}"
        except:
            return False, "Could not parse voltage"

    @staticmethod
    def check_interface_compatibility(original_interfaces: List[str], substitute_interfaces: List[str]) -> tuple:
        """Check if interfaces are compatible"""
        # Common interface equivalencies
        interface_map = {
            "I2C": ["I2C", "TWI"],
            "SPI": ["SPI"],
            "UART": ["UART", "Serial"],
            "Analog": ["ADC", "Analog"],
        }

        original_group = set()
        substitute_group = set()

        for iface in original_interfaces or []:
            for group, options in interface_map.items():
                if iface in options:
                    original_group.add(group)

        for iface in substitute_interfaces or []:
            for group, options in interface_map.items():
                if iface in options:
                    substitute_group.add(group)

        # Check if substitute has at least the same interfaces
        compatible = original_group.issubset(substitute_group)
        missing = original_group - substitute_group
        extra = substitute_group - original_group

        return compatible, {
            "missing": list(missing),
            "extra": list(extra)
        }

    @staticmethod
    def check_package_compatibility(original_package: str, substitute_package: str) -> tuple:
        """Check if packages are compatible"""
        # Package equivalencies
        package_groups = {
            "DIP": ["DIP", "DIL"],
            "SMD": ["SMD", "SM0805", "SM1206"],
            "BGA": ["BGA"],
            "LQFP": ["LQFP44", "LQFP48"],
        }

        orig_group = None
        subs_group = None

        for group, options in package_groups.items():
            if original_package in options:
                orig_group = group
            if substitute_package in options:
                subs_group = group

        compatible = orig_group == subs_group or subs_group == "SMD"  # SMD is often more flexible
        return compatible, f"{substitute_package} vs {original_package}"


# ────────────── SUBSTITUTION ENGINE ──────────────
class SubstitutionEngine:
    """Generate substitution recommendations"""

    def __init__(self):
        self.checker = CompatibilityChecker()

    async def find_substitutes(self, request: SubstitutionRequest) -> SubstitutionRecommendation:
        """Find compatible substitutes for a component"""

        # Simulated substitute database (in production: query from DB)
        substitute_database = self._get_substitutes_for_component(
            request.component_name, request.reason
        )

        substitutions = []

        for substitute in substitute_database[:request.max_suggestions]:
            compat_score = await self._calculate_compatibility(
                request.component_specs, substitute
            )

            subst = ComponentSubstitution(
                original_component=request.component_name,
                substitute_component=substitute["name"],
                compatibility_score=compat_score,
                compatibility_notes=substitute.get("notes", ""),
                missing_features=substitute.get("missing_features", []),
                extra_features=substitute.get("extra_features", []),
                impact_level="low" if compat_score >= 90 else "medium" if compat_score >= 75 else "high",
                can_substitute=compat_score >= 75,
                warnings=substitute.get("warnings", [])
            )

            substitutions.append(subst)

        # Sort by compatibility score
        substitutions.sort(key=lambda x: x.compatibility_score, reverse=True)

        # Select best option
        best = substitutions[0] if substitutions else None

        # Generate explanation
        explanation = self._generate_explanation(
            request.component_name, substitutions, request.reason
        )

        design_impact = self._assess_design_impact(substitutions, request.component_specs)

        return SubstitutionRecommendation(
            original=request.component_name,
            alternatives=substitutions,
            best_option=best,
            explanation=explanation,
            design_impact=design_impact
        )

    async def _calculate_compatibility(self, original_specs: Dict, substitute_specs: Dict) -> float:
        """Calculate compatibility score"""
        score = 0.0
        max_score = 100.0

        # Voltage compatibility (40%)
        if original_specs.get("voltage") and substitute_specs.get("voltage"):
            volt_compat, _ = self.checker.check_voltage_compatibility(
                original_specs["voltage"], substitute_specs["voltage"]
            )
            score += 40 if volt_compat else 20
        else:
            score += 30

        # Interface compatibility (30%)
        if original_specs.get("interface") and substitute_specs.get("interface"):
            iface_compat, details = self.checker.check_interface_compatibility(
                original_specs["interface"], substitute_specs["interface"]
            )
            if iface_compat:
                score += 30
            else:
                score += 20 - (len(details.get("missing", [])) * 5)
        else:
            score += 25

        # Package compatibility (20%)
        if original_specs.get("package") and substitute_specs.get("package"):
            pkg_compat, _ = self.checker.check_package_compatibility(
                original_specs["package"], substitute_specs["package"]
            )
            score += 20 if pkg_compat else 10
        else:
            score += 15

        # Performance (10%)
        score += 10  # Placeholder

        return min(max_score, max(0.0, score))

    def _get_substitutes_for_component(self, component: str, reason: str) -> List[Dict]:
        """Get substitutes from database"""
        # Placeholder: in production, query from database
        substitutes_map = {
            "ESP32": [
                {
                    "name": "ESP32-S3",
                    "voltage": "3.3V",
                    "interface": ["WiFi", "BLE", "USB"],
                    "missing_features": [],
                    "extra_features": ["More GPIO", "USB OTG"],
                    "notes": "Drop-in replacement, better performance",
                    "price_factor": 1.2,
                },
                {
                    "name": "Arduino Nano",
                    "voltage": "5V",
                    "interface": ["UART"],
                    "missing_features": ["WiFi", "BLE"],
                    "extra_features": [],
                    "notes": "No wireless, need separate module",
                    "warnings": ["Voltage incompatible", "Missing wireless"],
                    "price_factor": 0.5,
                },
            ],
            "BME280": [
                {
                    "name": "BMP280",
                    "voltage": "3.3V",
                    "interface": ["I2C", "SPI"],
                    "missing_features": ["Humidity"],
                    "extra_features": [],
                    "notes": "Temperature + Pressure only",
                    "price_factor": 0.7,
                },
                {
                    "name": "DHT22",
                    "voltage": "3.3V",
                    "interface": ["Digital"],
                    "missing_features": ["Pressure", "I2C"],
                    "extra_features": [],
                    "notes": "Different interface, lower accuracy",
                    "warnings": ["Different communication protocol"],
                    "price_factor": 0.5,
                },
            ],
        }

        return substitutes_map.get(component, [])

    def _generate_explanation(self, original: str, alternatives: List, reason: str) -> str:
        """Generate human-readable explanation"""
        if not alternatives:
            return f"No compatible substitutes found for {original}."

        best = alternatives[0]

        if reason == "unavailable":
            return f"{original} is unavailable. Best alternative: {best.substitute_component} ({best.compatibility_score:.0f}% compatible). {best.compatibility_notes}"
        elif reason == "cost_reduction":
            return f"For cost savings, consider {best.substitute_component} instead of {original}. Saves cost but {len(best.missing_features)} features missing."
        else:
            return f"Alternative suggestion: {best.substitute_component} with {best.compatibility_score:.0f}% compatibility."

    def _assess_design_impact(self, alternatives: List, specs: Dict) -> str:
        """Assess impact on design"""
        if not alternatives:
            return "High impact - no compatible substitutes found"

        best = alternatives[0]

        if best.compatibility_score >= 95:
            return "Low impact - drop-in replacement"
        elif best.compatibility_score >= 80:
            return "Medium impact - minor changes needed"
        elif best.compatibility_score >= 60:
            return "High impact - significant redesign required"
        else:
            return "Very high impact - may not be suitable"


# ────────────── API ENDPOINTS ──────────────
@app.post("/api/substitutions/find")
async def find_substitutions(request: SubstitutionRequest) -> SubstitutionRecommendation:
    """Find compatible component substitutes"""
    try:
        engine = SubstitutionEngine()
        recommendation = await engine.find_substitutes(request)
        return recommendation
    except Exception as e:
        logger.error(f"Substitution search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/substitutions/{component_name}")
async def get_substitution_history(component_name: str) -> Dict[str, Any]:
    """Get historical substitutions for a component"""
    return {
        "component": component_name,
        "message": "Substitution history - database integration needed"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
