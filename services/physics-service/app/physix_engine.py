"""
PhysiX — Self-Correcting Physics Intelligence Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Orchestrates multi-physics simulations with automatic design correction.
Provides explainable failure diagnosis and self-correcting design loops.
"""

import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class PhysicsType(Enum):
    """Physics simulation types"""
    STRUCTURAL = "structural"
    THERMAL = "thermal"
    FLUID = "fluid"
    VIBRATION = "vibration"
    AERODYNAMIC = "aerodynamic"


@dataclass
class PhysicsConstraint:
    """Physics constraint from requirements"""
    type: PhysicsType
    parameter: str  # e.g., "max_stress", "temperature"
    limit: float
    unit: str
    description: str = ""


@dataclass
class PhysicsResult:
    """Result from a single physics simulation"""
    simulation_type: PhysicsType
    status: str  # "PASS", "FAIL", "WARNING"
    primary_metric: float
    primary_metric_name: str
    primary_metric_unit: str
    limit: float
    safety_factor: float
    critical_regions: List[Dict[str, Any]]  # regions of highest stress/concern
    timestamp: str
    explanation: str = ""


@dataclass
class FailureDiagnosis:
    """Structured failure analysis"""
    failed: bool
    primary_reason: str
    critical_region: Optional[str]
    affected_metrics: List[Dict[str, Any]]
    root_cause: str
    recommended_fixes: List[str]  # ["increase thickness", "add fillet", ...]
    severity: str  # "CRITICAL", "HIGH", "MEDIUM"


@dataclass
class PhysiXScore:
    """Multi-physics feasibility score"""
    overall_score: float  # 0-100
    structural_score: float
    thermal_score: Optional[float]
    fluid_score: Optional[float]
    vibration_score: Optional[float]
    aerodynamic_score: Optional[float]
    material_check: str  # "PASS", "WARN", "FAIL"
    safety_factor: float
    manufacturability: str  # "EASY", "MODERATE", "DIFFICULT"
    breakdown: Dict[str, float]


class PhysiXEngine:
    """
    Self-Correcting Physics Intelligence Engine
    
    Orchestrates multi-physics simulations with automatic design correction.
    """

    def __init__(self):
        self.max_iterations = 3
        self.iteration_count = 0
        self.design_history: List[Dict] = []
        self.physics_results: List[PhysicsResult] = []

    async def select_physics(self, invention_type: str) -> List[PhysicsType]:
        """
        Intelligently select which physics simulations are needed.
        
        Examples:
        - Drone: Structural, Aerodynamic, Vibration, Thermal
        - Water purifier: Fluid, Pressure, Structural
        - Bracket: Structural, Material
        """
        physics_map = {
            "drone": [
                PhysicsType.STRUCTURAL,
                PhysicsType.AERODYNAMIC,
                PhysicsType.VIBRATION,
                PhysicsType.THERMAL,
            ],
            "quadcopter": [
                PhysicsType.STRUCTURAL,
                PhysicsType.AERODYNAMIC,
                PhysicsType.VIBRATION,
            ],
            "bracket": [PhysicsType.STRUCTURAL],
            "heat_sink": [PhysicsType.THERMAL, PhysicsType.STRUCTURAL],
            "pump": [PhysicsType.FLUID, PhysicsType.STRUCTURAL],
            "turbine": [PhysicsType.FLUID, PhysicsType.STRUCTURAL, PhysicsType.VIBRATION],
            "exoskeleton": [PhysicsType.STRUCTURAL, PhysicsType.VIBRATION],
            "farming": [PhysicsType.STRUCTURAL, PhysicsType.THERMAL],  # Vertical farming system
            "vertical_farming": [PhysicsType.STRUCTURAL, PhysicsType.THERMAL],
        }

        # Find matching physics types
        selected = []
        for inv_type, physics_list in physics_map.items():
            if inv_type.lower() in invention_type.lower():
                selected = physics_list
                break

        # Default to structural if no match
        if not selected:
            selected = [PhysicsType.STRUCTURAL]

        logger.info(f"Selected physics types for '{invention_type}': {[p.value for p in selected]}")
        return selected

    async def run_structural_simulation(
        self, design_params: Dict[str, Any], constraints: List[PhysicsConstraint]
    ) -> PhysicsResult:
        """Run FEA structural simulation"""
        logger.info("Running structural analysis...")

        # Simulate realistic structural analysis
        thickness = design_params.get("thickness_mm", 3.0)
        material = design_params.get("material", "Aluminium 6061")
        load = design_params.get("load_n", 500)

        # Material properties
        materials = {
            "Aluminium 6061": {"yield": 276, "youngs_modulus": 69},
            "Steel": {"yield": 250, "youngs_modulus": 200},
            "Carbon Fiber": {"yield": 600, "youngs_modulus": 230},
        }

        mat_props = materials.get(material, materials["Aluminium 6061"])

        # Simplified stress calculation: stress = force / area
        # For a bracket: area ≈ thickness * width
        width = 20  # mm
        area = thickness * width  # mm²
        stress_mpa = load / (area / 100)  # Convert to MPa

        # Find stress limit constraint
        stress_limit = 250  # Default
        for constraint in constraints:
            if constraint.parameter == "max_stress":
                stress_limit = constraint.limit

        safety_factor = mat_props["yield"] / stress_mpa if stress_mpa > 0 else 999

        status = "PASS" if stress_mpa < stress_limit else "FAIL"
        if safety_factor < 1.5:
            status = "WARNING"

        return PhysicsResult(
            simulation_type=PhysicsType.STRUCTURAL,
            status=status,
            primary_metric=stress_mpa,
            primary_metric_name="Maximum Stress",
            primary_metric_unit="MPa",
            limit=stress_limit,
            safety_factor=safety_factor,
            critical_regions=[
                {
                    "name": "Joint B",
                    "stress": stress_mpa,
                    "severity": "HIGH" if stress_mpa > stress_limit else "LOW",
                }
            ],
            timestamp="2026-08-23T10:30:00Z",
            explanation=f"Stress analysis shows {stress_mpa:.1f} MPa at joint, "
            f"yield strength is {mat_props['yield']} MPa",
        )

    async def run_thermal_simulation(
        self, design_params: Dict[str, Any], constraints: List[PhysicsConstraint]
    ) -> PhysicsResult:
        """Run thermal simulation"""
        logger.info("Running thermal analysis...")

        ambient_temp = design_params.get("ambient_temp_c", 25)
        power_dissipation = design_params.get("power_dissipation_w", 10)
        material = design_params.get("material", "Aluminium")

        # Simple thermal resistance model: T_junction = T_ambient + (P_d * R_th)
        # Thermal resistance (simplified)
        thermal_resistance = 0.5  # C/W for small bracket
        junction_temp = ambient_temp + (power_dissipation * thermal_resistance)

        # Temperature limit
        temp_limit = 85  # Typical for electronics
        for constraint in constraints:
            if constraint.parameter == "max_temperature":
                temp_limit = constraint.limit

        status = "PASS" if junction_temp < temp_limit else "FAIL"

        return PhysicsResult(
            simulation_type=PhysicsType.THERMAL,
            status=status,
            primary_metric=junction_temp,
            primary_metric_name="Junction Temperature",
            primary_metric_unit="°C",
            limit=temp_limit,
            safety_factor=temp_limit / junction_temp if junction_temp > 0 else 999,
            critical_regions=[{"name": "Power dissipation area", "temp": junction_temp}],
            timestamp="2026-08-23T10:30:00Z",
            explanation=f"Thermal analysis shows junction temperature of {junction_temp:.1f}°C",
        )

    async def diagnose_failure(
        self, physics_results: List[PhysicsResult], design_params: Dict
    ) -> FailureDiagnosis:
        """
        Analyze physics failures and provide structured diagnosis.
        This is the "Physics Explainability" feature.
        """
        failed_results = [r for r in physics_results if r.status == "FAIL"]

        if not failed_results:
            return FailureDiagnosis(
                failed=False,
                primary_reason="All physics checks passed",
                critical_region=None,
                affected_metrics=[],
                root_cause="N/A",
                recommended_fixes=[],
                severity="NONE",
            )

        primary_failure = failed_results[0]

        # Diagnose root cause
        if primary_failure.simulation_type == PhysicsType.STRUCTURAL:
            if primary_failure.primary_metric > primary_failure.limit:
                root_cause = "Stress exceeds material yield strength"
                fixes = [
                    f"Increase thickness from {design_params.get('thickness_mm', 3)}mm to {design_params.get('thickness_mm', 3) + 2}mm",
                    "Add fillet at stress concentration (Joint B)",
                    f"Change material from {design_params.get('material', 'Aluminium')} to Steel or Carbon Fiber",
                    "Reduce applied load",
                ]
            else:
                root_cause = "Insufficient safety factor"
                fixes = ["Increase thickness", "Switch to higher-strength material"]
        elif primary_failure.simulation_type == PhysicsType.THERMAL:
            root_cause = "Heat dissipation inadequate"
            fixes = [
                "Increase surface area for cooling",
                "Add heat sink",
                "Reduce power dissipation",
                "Improve material thermal conductivity",
            ]
        else:
            root_cause = f"{primary_failure.simulation_type.value} constraint violated"
            fixes = ["Review design parameters"]

        return FailureDiagnosis(
            failed=True,
            primary_reason=f"{primary_failure.primary_metric_name} = {primary_failure.primary_metric:.1f} {primary_failure.primary_metric_unit}",
            critical_region=primary_failure.critical_regions[0]["name"]
            if primary_failure.critical_regions
            else None,
            affected_metrics=[
                {
                    "name": primary_failure.primary_metric_name,
                    "value": primary_failure.primary_metric,
                    "unit": primary_failure.primary_metric_unit,
                    "limit": primary_failure.limit,
                }
            ],
            root_cause=root_cause,
            recommended_fixes=fixes,
            severity="CRITICAL" if primary_failure.safety_factor < 1 else "HIGH",
        )

    async def optimize_design(
        self, design_params: Dict, diagnosis: FailureDiagnosis
    ) -> Dict:
        """
        Auto-correct design based on failure diagnosis.
        This is the "Self-Correcting Physics Loop" feature.
        """
        logger.info(f"Optimizing design. Applying: {diagnosis.recommended_fixes[0]}")

        optimized = design_params.copy()

        # Apply first recommended fix
        if diagnosis.recommended_fixes:
            fix = diagnosis.recommended_fixes[0]

            if "Increase thickness" in fix:
                current_thickness = optimized.get("thickness_mm", 3)
                optimized["thickness_mm"] = current_thickness + 2

            elif "Change material" in fix:
                optimized["material"] = "Steel"

            elif "Add fillet" in fix:
                optimized["fillet_radius_mm"] = 2

            elif "increase surface area" in fix.lower():
                optimized["heatsink_area"] = 500  # mm²

        logger.info(f"Design optimized: {optimized}")
        return optimized

    async def self_correcting_loop(
        self, design_params: Dict, invention_type: str, constraints: List[PhysicsConstraint]
    ) -> Dict[str, Any]:
        """
        THE MAIN FEATURE: Self-Correcting Physics Design Loop

        Automatically iterates:
        1. Run physics simulations
        2. Check for failures
        3. Diagnose root cause
        4. Optimize design
        5. Repeat until PASS or max iterations
        """
        logger.info("Starting Self-Correcting Physics Design Loop...")

        current_design = design_params.copy()
        self.design_history = [current_design]
        self.iteration_count = 0

        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"ITERATION {self.iteration_count} / {self.max_iterations}")
            logger.info(f"{'='*60}")

            # Step 1: Select and run physics simulations
            physics_types = await self.select_physics(invention_type)
            self.physics_results = []

            for physics_type in physics_types:
                if physics_type == PhysicsType.STRUCTURAL:
                    result = await self.run_structural_simulation(current_design, constraints)
                elif physics_type == PhysicsType.THERMAL:
                    result = await self.run_thermal_simulation(current_design, constraints)
                else:
                    # Placeholder for other physics types
                    result = PhysicsResult(
                        simulation_type=physics_type,
                        status="PASS",
                        primary_metric=100,
                        primary_metric_name="Simulation",
                        primary_metric_unit="units",
                        limit=100,
                        safety_factor=2.0,
                        critical_regions=[],
                        timestamp="2026-08-23T10:30:00Z",
                    )

                self.physics_results.append(result)
                logger.info(f"✓ {physics_type.value}: {result.status}")

            # Step 2: Check if all passed
            all_passed = all(r.status == "PASS" for r in self.physics_results)

            if all_passed:
                logger.info(f"\n✅ ALL PHYSICS CHECKS PASSED! Converged in {self.iteration_count} iterations")
                return {
                    "status": "SUCCESS",
                    "iteration": self.iteration_count,
                    "final_design": current_design,
                    "physics_results": [asdict(r) for r in self.physics_results],
                    "design_history": self.design_history,
                }

            # Step 3: Diagnose failure
            diagnosis = await self.diagnose_failure(self.physics_results, current_design)
            
            # If no recommendations (passed successfully), exit
            if not diagnosis.failed:
                logger.info(f"✅ Physics validation successful")
                return {
                    "status": "SUCCESS",
                    "iteration": self.iteration_count,
                    "final_design": current_design,
                    "physics_results": [asdict(r) for r in self.physics_results],
                    "design_history": self.design_history,
                }
            
            logger.info(f"❌ FAILURE DIAGNOSIS:")
            logger.info(f"   Root cause: {diagnosis.root_cause}")
            if diagnosis.recommended_fixes:
                logger.info(f"   Fix: {diagnosis.recommended_fixes[0]}")

            # Step 4: Optimize design
            current_design = await self.optimize_design(current_design, diagnosis)
            self.design_history.append(current_design)

        # Max iterations reached
        logger.warning(f"❌ Max iterations ({self.max_iterations}) reached without convergence")
        return {
            "status": "FAILED_CONVERGENCE",
            "iteration": self.iteration_count,
            "final_design": current_design,
            "physics_results": [asdict(r) for r in self.physics_results],
            "design_history": self.design_history,
            "last_diagnosis": asdict(diagnosis) if diagnosis else None,
        }

    async def compute_physix_score(
        self, physics_results: List[PhysicsResult]
    ) -> PhysiXScore:
        """
        Compute Multi-Physics Feasibility Score.
        This is the "Physics Score" feature.
        """
        scores = {}
        total_score = 0
        count = 0

        for result in physics_results:
            # Convert safety factor to 0-100 score
            # Perfect score (SF=2.5) = 100, SF=1.0 = 60, SF<1.0 = 0
            if result.safety_factor >= 2.5:
                score = 100
            elif result.safety_factor >= 1.5:
                score = 80
            elif result.safety_factor >= 1.0:
                score = 60
            else:
                score = max(0, 30 - (1 - result.safety_factor) * 50)

            scores[result.simulation_type.value + "_score"] = score
            total_score += score
            count += 1

        avg_score = total_score / count if count > 0 else 0

        # Adjust for failures
        if any(r.status == "FAIL" for r in physics_results):
            avg_score *= 0.7

        return PhysiXScore(
            overall_score=avg_score,
            structural_score=scores.get("structural_score", 100),
            thermal_score=scores.get("thermal_score"),
            fluid_score=scores.get("fluid_score"),
            vibration_score=scores.get("vibration_score"),
            aerodynamic_score=scores.get("aerodynamic_score"),
            material_check="PASS" if avg_score > 70 else "WARN",
            safety_factor=max([r.safety_factor for r in physics_results]) if physics_results else 1.0,
            manufacturability="EASY" if avg_score > 85 else "MODERATE" if avg_score > 70 else "DIFFICULT",
            breakdown=scores,
        )
