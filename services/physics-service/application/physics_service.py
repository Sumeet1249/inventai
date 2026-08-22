from fastapi import FastAPI
from services.physics_service.schemas.physics_schemas import SimulationRequest
from packages.ai_core.memory.memory_manager import MemoryManager
from services.physics_service.materials.database import MaterialDatabase
from services.physics_service.ingestion.cad_ingester import CadIngester
from services.physics_service.solvers.elasticity import LinearElasticitySolver
from services.physics_service.visualization.plotter import PhysicsPlotter
import asyncio
import json
import uuid
import os
import logging
from services.physics_service.materials.provider import get_provider

class PhysicsApplicationService:
    """
    Business use case orchestrator for Engineering Simulation.
    Ties together Geometry Ingestion, DeepXDE execution, and Plotting.
    """
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    async def run_simulation_stream(self, request: SimulationRequest):
        """
        Triggers the AI orchestration to setup boundary conditions, 
        execute the PINN simulation, and stream SSE progress.
        """
        unique_id = getattr(request, 'cad_model_id', str(uuid.uuid4())[:8])
        
        # 1. Setup Material
        yield f"data: {json.dumps({'status': 'Configuring Materials'})}\n\n"
        await asyncio.sleep(0.5)
        
        material_id = request.material_id or "aluminum"
        
        provider = get_provider()
        material = provider.search(material_id)
        
        if not material:
            # Absolute fallback if provider fails to find anything
            from services.physics_service.materials.database import MaterialDatabase
            material = MaterialDatabase.get_material(material_id)
            
        mat_name = material.get('name', 'Unknown')
        yield f"data: {json.dumps({'status': f'Material ready: {mat_name}'})}\n\n"
        
        # 2. Geometry Ingestion
        yield f"data: {json.dumps({'status': 'Ingesting CAD Geometry'})}\n\n"
        await asyncio.sleep(0.5)
        points = CadIngester.generate_point_cloud(f"/tmp/cad_exports/model_{unique_id}.stl", num_points=2000)
        
        # 3. Boundary Conditions
        yield f"data: {json.dumps({'status': 'Applying Boundary Conditions'})}\n\n"
        await asyncio.sleep(0.5)
        forces = request.boundary_conditions or {"z": -50.0} # default downward force
        
        # 4. PINN Solver
        yield f"data: {json.dumps({'status': 'Running DeepXDE PINN Solver'})}\n\n"
        await asyncio.sleep(1.0) # simulate solver time
        solver = LinearElasticitySolver(E=material["E"], nu=material["nu"])
        results = solver.solve(points, forces)
        
        # 5. Result Post-processing & Visualization
        yield f"data: {json.dumps({'status': 'Generating Stress Heatmap'})}\n\n"
        await asyncio.sleep(0.5)
        heatmap_url = f"/api/v1/physics/download/heatmap_{unique_id}.png"
        PhysicsPlotter.plot_stress_heatmap(results["points"], results["von_mises_stress"], f"/tmp/physics_exports/heatmap_{unique_id}.png")
        
        # 6. Safety Factor & Optimization
        yield f"data: {json.dumps({'status': 'Calculating Safety Factor'})}\n\n"
        safety_factor = material["yield_strength"] / results["max_stress_mpa"]
        
        recommendation = "Design is safe."
        if safety_factor < 1.5:
            recommendation = "Warning: Safety factor too low. Thicken cross-sections or change material to Titanium/Carbon Fiber."
        elif safety_factor > 10.0:
            recommendation = "Design is over-engineered. Use topology optimization to reduce mass by up to 30%."
            
        final_payload = {
            "status": "Completed",
            "material_used": material["name"],
            "max_stress_mpa": round(results["max_stress_mpa"], 2),
            "safety_factor": round(safety_factor, 2),
            "recommendation": recommendation,
            "heatmap_url": heatmap_url
        }
        
        yield f"data: {json.dumps(final_payload)}\n\n"

# Create and configure FastAPI app
app = FastAPI(
    title="InventAI Physics Service",
    description="DeepXDE PINN-based physics simulation and validation",
    version="1.0.0"
)

@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy", "service": "physics-service"}

# Lazy import to avoid circular dependencies
from services.physics_service.api.routers import router
app.include_router(router)
