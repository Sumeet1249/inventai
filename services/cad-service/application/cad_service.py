from fastapi import FastAPI
from services.cad_service.schemas.cad_schemas import CADGenerationRequest, CADModelResponse
from packages.ai_core.memory.memory_manager import MemoryManager
from services.cad_service.planners.cad_planner import CADPlanner
from services.cad_service.generators.drone import generate_drone
from services.cad_service.validators.geometry_validator import GeometryValidator
from services.cad_service.exporters.step_exporter import StepExporter
from services.cad_service.exporters.gltf_exporter import GLTFExporter
from services.cad_service.exporters.stl_exporter import STLExporter
import os
import uuid
import json
import asyncio

class CADApplicationService:
    """
    Business use case orchestrator for CAD generation.
    Ties together Repositories, AI Workflows, and CadQuery execution.
    """
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.planner = CADPlanner(memory_manager)

    async def generate_model_stream(self, request: CADGenerationRequest):
        """
        Triggers the AI CAD orchestration and yields SSE events.
        """
        unique_id = str(uuid.uuid4())[:8]
        
        # Step 1: Planning
        yield f"data: {json.dumps({'status': 'Analyzing Idea'})}\n\n"
        await asyncio.sleep(0.5) # simulate work
        idea_text = request.prompt
        params = await self.planner.generate_parameters(idea_text)
        
        # Step 2: Generation
        yield f"data: {json.dumps({'status': 'Generating CAD Parameters'})}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'status': 'Building Geometry'})}\n\n"
        model = generate_drone(params)
        await asyncio.sleep(0.5)
        
        # Step 3: Validation
        yield f"data: {json.dumps({'status': 'Validating Geometry'})}\n\n"
        GeometryValidator.validate(model)
        await asyncio.sleep(0.5)
        
        # Step 4: Exporting
        yield f"data: {json.dumps({'status': 'Exporting Files'})}\n\n"
        os.makedirs('/tmp/cad_exports', exist_ok=True)
        step_filename = f"/tmp/cad_exports/model_{unique_id}.step"
        gltf_filename = f"/tmp/cad_exports/model_{unique_id}.gltf"
        stl_filename = f"/tmp/cad_exports/model_{unique_id}.stl"
        
        StepExporter.export(model, step_filename)
        GLTFExporter.export(model, gltf_filename)
        STLExporter.export(model, stl_filename)
        
        # Step 5: Uploading (mock)
        yield f"data: {json.dumps({'status': 'Uploading Artifacts'})}\n\n"
        await asyncio.sleep(0.5)
        
        final_payload = {
            "id": unique_id,
            "parameters": params,
            "status": "Completed",
            "gltf_url": f"/api/v1/cad/download/model_{unique_id}.gltf",
            "step_url": f"/api/v1/cad/download/model_{unique_id}.step",
            "stl_url": f"/api/v1/cad/download/model_{unique_id}.stl"
        }
        
        yield f"data: {json.dumps(final_payload)}\n\n"

# Create and configure FastAPI app
app = FastAPI(
    title="InventAI CAD Service",
    description="Text-to-3D CAD generation using CadQuery",
    version="1.0.0"
)

# Lazy import to avoid circular dependencies
from services.cad_service.api.routers import router
app.include_router(router)
