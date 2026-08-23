"""
PhysiX Physics Service — FastAPI Integration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FastAPI endpoints for self-correcting physics simulations.
"""

import logging
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from datetime import datetime

from .physix_engine import (
    PhysiXEngine,
    PhysicsType,
    PhysicsConstraint,
    PhysiXScore,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PhysiX Physics Service",
    description="Self-Correcting Physics Intelligence Engine",
    version="1.0.0",
)

# ============================================================================
# Request/Response Models
# ============================================================================


class PhysicsConstraintRequest(BaseModel):
    """Physics constraint from requirements"""

    type: str  # Accept as string, will convert to enum
    parameter: str  # "max_stress", "temperature", etc.
    limit: float
    unit: str
    description: Optional[str] = ""


class DesignParamsRequest(BaseModel):
    """Design parameters for simulation"""

    thickness_mm: Optional[float] = 3.0
    material: Optional[str] = "Aluminium 6061"
    load_n: Optional[float] = 500
    ambient_temp_c: Optional[float] = 25
    power_dissipation_w: Optional[float] = 10
    fillet_radius_mm: Optional[float] = 0
    heatsink_area: Optional[float] = 0
    custom_params: Optional[Dict[str, Any]] = {}


class PhysiXSelfCorrectionRequest(BaseModel):
    """Request for self-correcting physics loop"""

    project_id: str
    invention_type: str  # "drone", "exoskeleton", "bracket", etc.
    design_params: DesignParamsRequest
    constraints: List[PhysicsConstraintRequest] = []
    max_iterations: int = 3


class PhysiXScoreResponse(BaseModel):
    """Multi-physics feasibility score response"""

    overall_score: float
    structural_score: Optional[float] = None
    thermal_score: Optional[float] = None
    fluid_score: Optional[float] = None
    vibration_score: Optional[float] = None
    aerodynamic_score: Optional[float] = None
    material_check: str
    safety_factor: float
    manufacturability: str
    breakdown: Dict[str, float]


class IterationResult(BaseModel):
    """Single iteration result"""

    iteration: int
    design_params: Dict[str, Any]
    physics_results: List[Dict[str, Any]]
    status: str  # "RUNNING", "PASS", "FAIL"
    diagnosis: Optional[Dict[str, Any]] = None


class PhysiXSelfCorrectionResponse(BaseModel):
    """Response from self-correcting physics loop"""

    project_id: str
    status: str  # "SUCCESS", "FAILED_CONVERGENCE", "ERROR"
    final_iteration: int
    final_design: Dict[str, Any]
    physics_results: List[Dict[str, Any]]
    design_history: List[Dict[str, Any]]
    physix_score: Dict[str, Any]
    convergence_time_seconds: float
    last_diagnosis: Optional[Dict[str, Any]] = None
    iteration_details: List[IterationResult] = []


# ============================================================================
# Global Engine Instance
# ============================================================================

physix_engine = PhysiXEngine()

# ============================================================================
# Endpoints
# ============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PhysiX Physics Service"}


@app.post("/api/v1/physics/self-correct", response_model=PhysiXSelfCorrectionResponse)
async def self_correct_physics(request: PhysiXSelfCorrectionRequest):
    """
    Run self-correcting physics loop.

    This endpoint:
    1. Selects appropriate physics simulations for invention type
    2. Runs initial physics checks
    3. On failure: diagnoses root cause → optimizes design → re-runs
    4. Repeats until design passes or max iterations reached
    5. Returns complete iteration history with final score

    Example request:
    ```json
    {
      "project_id": "proj-123",
      "invention_type": "exoskeleton",
      "design_params": {
        "thickness_mm": 3.0,
        "material": "Aluminium 6061",
        "load_n": 500
      },
      "constraints": [
        {
          "type": "structural",
          "parameter": "max_stress",
          "limit": 250,
          "unit": "MPa"
        }
      ]
    }
    ```
    """
    import time

    start_time = time.time()

    try:
        logger.info(f"Starting PhysiX self-correction for project {request.project_id}")

        # Convert constraints
        constraints = [
            PhysicsConstraint(
                type=PhysicsType[c.type.upper()] if hasattr(PhysicsType, c.type.upper()) else PhysicsType.STRUCTURAL,
                parameter=c.parameter,
                limit=c.limit,
                unit=c.unit,
                description=c.description,
            )
            for c in request.constraints
        ]

        # Set max iterations
        physix_engine.max_iterations = request.max_iterations

        # Run self-correcting loop
        result = await physix_engine.self_correcting_loop(
            design_params=request.design_params.dict(),
            invention_type=request.invention_type,
            constraints=constraints,
        )

        # Compute PhysiX Score
        physix_score = await physix_engine.compute_physix_score(physix_engine.physics_results)

        convergence_time = time.time() - start_time

        logger.info(
            f"✅ PhysiX loop completed: {result['status']} in {physix_engine.iteration_count} iterations, "
            f"time: {convergence_time:.2f}s, score: {physix_score.overall_score:.1f}/100"
        )

        return PhysiXSelfCorrectionResponse(
            project_id=request.project_id,
            status=result["status"],
            final_iteration=result["iteration"],
            final_design=result["final_design"],
            physics_results=result["physics_results"],
            design_history=result["design_history"],
            physix_score={
                "overall_score": physix_score.overall_score,
                "structural_score": physix_score.structural_score,
                "thermal_score": physix_score.thermal_score,
                "fluid_score": physix_score.fluid_score,
                "vibration_score": physix_score.vibration_score,
                "aerodynamic_score": physix_score.aerodynamic_score,
                "material_check": physix_score.material_check,
                "safety_factor": physix_score.safety_factor,
                "manufacturability": physix_score.manufacturability,
                "breakdown": physix_score.breakdown,
            },
            convergence_time_seconds=convergence_time,
            last_diagnosis=result.get("last_diagnosis"),
        )

    except Exception as e:
        logger.error(f"Error in self-correction loop: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Physics simulation error: {str(e)}")


@app.post("/api/v1/physics/simulate")
async def run_physics_simulation(
    project_id: str,
    invention_type: str,
    design_params: DesignParamsRequest,
    physics_types: Optional[List[str]] = None,
):
    """
    Run a single physics simulation (no auto-correction).

    Useful for quick validation of a design without self-correction loop.
    """
    try:
        logger.info(f"Running physics simulation for {invention_type}")

        # Select physics types
        if physics_types:
            selected_physics = [PhysicsType[p.upper()] for p in physics_types if hasattr(PhysicsType, p.upper())]
        else:
            selected_physics = await physix_engine.select_physics(invention_type)

        results = []

        # Run simulations
        for physics_type in selected_physics:
            if physics_type == PhysicsType.STRUCTURAL:
                result = await physix_engine.run_structural_simulation(design_params.dict(), [])
            elif physics_type == PhysicsType.THERMAL:
                result = await physix_engine.run_thermal_simulation(design_params.dict(), [])
            else:
                continue

            results.append(
                {
                    "type": result.simulation_type.value,
                    "status": result.status,
                    "metric": result.primary_metric,
                    "metric_name": result.primary_metric_name,
                    "unit": result.primary_metric_unit,
                    "limit": result.limit,
                    "safety_factor": result.safety_factor,
                    "explanation": result.explanation,
                }
            )

        # Compute score
        physix_score = await physix_engine.compute_physix_score(physix_engine.physics_results)

        return {
            "project_id": project_id,
            "invention_type": invention_type,
            "physics_results": results,
            "physix_score": {
                "overall_score": physix_score.overall_score,
                "structural_score": physix_score.structural_score,
                "thermal_score": physix_score.thermal_score,
                "safety_factor": physix_score.safety_factor,
                "manufacturability": physix_score.manufacturability,
            },
        }

    except Exception as e:
        logger.error(f"Physics simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/physics/test")
async def test_physix():
    """Test endpoint with sample physics simulation"""
    logger.info("Running PhysiX test...")

    test_request = PhysiXSelfCorrectionRequest(
        project_id="test-drone-001",
        invention_type="drone",
        design_params=DesignParamsRequest(
            thickness_mm=2.0,
            material="Aluminium 6061",
            load_n=1000,
        ),
        constraints=[
            PhysicsConstraintRequest(
                type="structural",
                parameter="max_stress",
                limit=250,
                unit="MPa",
                description="Maximum allowed stress",
            )
        ],
        max_iterations=3,
    )

    return await self_correct_physics(test_request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
