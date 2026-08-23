"""
Circuit Service — FastAPI
─────────────────────────
POST /api/v1/circuit/generate
  Body: { "project_id": str, "cad_spec": {...} }
  Returns: SSE stream with circuit data

GET /api/v1/circuit/schematic/{project_id}
  Returns: SVG schematic as image/svg+xml

POST /api/v1/circuit/build-it/{project_id}
  Integrates with BUILD IT system for component sourcing
"""

from __future__ import annotations
import asyncio
import json
import logging
import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import Any

from circuit_generator import generate_circuit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InventAI Circuit Service",
    description="CAD → Circuit Design: electronics agent + SVG schematic + BOM",
    version="1.0.0",
)

# In-memory cache: project_id → circuit result
_cache: dict[str, dict] = {}


class CircuitRequest(BaseModel):
    project_id: str
    cad_spec: dict[str, Any] = {}
    idea: str = ""


@app.get("/health")
async def health():
    return {"status": "ok", "service": "circuit-service"}


@app.post("/api/v1/circuit/generate")
async def generate(request: CircuitRequest):
    """
    Generates circuit from CAD spec. Streams SSE progress events.
    """
    async def stream():
        yield f"data: {json.dumps({'status': 'Analysing CAD spec…'})}\n\n"
        await asyncio.sleep(0.2)

        yield f"data: {json.dumps({'status': 'Electronics agent: extracting power requirements…'})}\n\n"

        try:
            result = await generate_circuit(request.cad_spec or {"component_type": "drone_frame"})
            _cache[request.project_id] = result

            yield f"data: {json.dumps({'status': 'SVG schematic generated'})}\n\n"
            await asyncio.sleep(0.1)

            # Final payload — omit SVG from SSE (too large), send everything else
            payload = {
                "status":      "Completed",
                "project_id":  request.project_id,
                "bom":         result["bom"],
                "bom_total":   result["bom_total"],
                "power_rails": result["power_rails"],
                "elec_spec":   result["elec_spec"],
                "schematic_url": f"/api/v1/circuit/schematic/{request.project_id}",
                "component_count": len(result["bom"]),
            }
            yield f"data: {json.dumps(payload)}\n\n"

        except Exception as exc:
            logger.error("Circuit generation failed: %s", exc, exc_info=True)
            yield f"data: {json.dumps({'status': 'Error', 'error': str(exc)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/v1/circuit/schematic/{project_id}")
async def get_schematic(project_id: str):
    """Returns the SVG schematic for a project."""
    result = _cache.get(project_id)
    if not result:
        # Generate a default schematic
        result = await generate_circuit({"component_type": "drone_frame"})
        _cache[project_id] = result

    return Response(
        content=result["svg"],
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-cache"},
    )


@app.post("/api/v1/circuit/build-it/{project_id}")
async def build_it_integration(project_id: str):
    """
    Integrates circuit design with BUILD IT system.
    Extracts BOM from circuit and sends to BOM Service for component sourcing.
    
    This endpoint connects circuit design → BOM extraction → product sourcing.
    """
    try:
        # Get circuit result from cache
        result = _cache.get(project_id)
        if not result:
            raise HTTPException(status_code=404, detail="Project not found. Generate circuit first.")
        
        # Extract BOM components and convert to BUILD IT format
        bom_items = []
        for comp in result.get("bom", []):
            bom_item = {
                "name": comp.get("name", ""),
                "ref": comp.get("ref", ""),
                "type": comp.get("type", ""),
                "voltage": comp.get("voltage", ""),
                "package": comp.get("package", ""),
                "quantity": 1,  # TODO: Parse quantity from ref (e.g., M1-M4)
                "is_required": True
            }
            bom_items.append(bom_item)
        
        # Prepare BOM for BUILD IT BOM Service (port 8009)
        bom_service_url = "http://localhost:8009/api/bom/generate"
        bom_service_payload = {
            "project_id": project_id,
            "design_id": f"circuit-{project_id}",
            "circuit_data": {
                "components": bom_items
            }
        }
        
        # Call BOM Service to generate structured BOM
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                bom_response = await client.post(
                    bom_service_url,
                    json=bom_service_payload,
                    headers={"Content-Type": "application/json"}
                )
                bom_response.raise_for_status()
                bom_data = bom_response.json()
                
                # Prepare response with BUILD IT links
                response = {
                    "project_id": project_id,
                    "status": "Circuit integrated with BUILD IT",
                    "circuit_components": len(bom_items),
                    "build_it_bom_id": bom_data.get("timestamp", "generated"),
                    "bom_summary": {
                        "total_components": bom_data.get("total_components", 0),
                        "required_count": bom_data.get("required_count", 0),
                        "optional_count": bom_data.get("optional_count", 0)
                    },
                    "build_it_links": {
                        "bom_service": "http://localhost:8009/docs",
                        "product_search": "http://localhost:8010/docs",
                        "shopping_list": "http://localhost:8011/docs",
                        "substitutions": "http://localhost:8012/docs"
                    },
                    "workflow": [
                        "Step 1: ✅ Circuit generated (circuit-service)",
                        "Step 2: ✅ BOM extracted (bom-service)",
                        "Step 3: 🔄 Ready for product search",
                        "Step 4: 🔄 Ready for shopping list",
                        "Step 5: 🔄 Ready for substitutions"
                    ],
                    "next_steps": [
                        f"Search products: POST http://localhost:8010/api/products/search",
                        f"Generate shopping list: POST http://localhost:8011/api/shopping-list/generate",
                        f"Find alternatives: POST http://localhost:8012/api/substitutions/find"
                    ]
                }
                
                return response
                
            except httpx.HTTPStatusError as e:
                logger.error(f"BOM Service failed: {e.response.status_code} {e.response.text}")
                raise HTTPException(
                    status_code=502,
                    detail=f"BOM Service integration failed: {e.response.status_code}"
                )
            except httpx.RequestError as e:
                logger.error(f"BOM Service connection failed: {e}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Cannot connect to BOM Service. Is it running on port 8009?"
                )
                
    except Exception as e:
        logger.error(f"Build IT integration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Simple test endpoint to verify circuit BOM format
@app.get("/api/v1/circuit/test-bom/{project_id}")
async def test_bom_format(project_id: str):
    """
    Returns circuit BOM in BUILD IT compatible format.
    Useful for testing the integration.
    """
    result = _cache.get(project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    
    bom_items = []
    for comp in result.get("bom", []):
        bom_item = {
            "name": comp.get("name", ""),
            "ref": comp.get("ref", ""),
            "type": comp.get("type", ""),
            "voltage": comp.get("voltage", ""),
            "package": comp.get("package", ""),
            "quantity": 1,
            "is_required": True,
            "description": f"{comp.get('type', '').replace('_', ' ').title()} - {comp.get('name', '')}"
        }
        bom_items.append(bom_item)
    
    return {
        "project_id": project_id,
        "circuit_bom": result.get("bom", []),
        "build_it_format": bom_items,
        "bom_size": len(bom_items),
        "sample_bom_service_payload": {
            "project_id": project_id,
            "design_id": f"circuit-{project_id}",
            "circuit_data": {
                "components": bom_items[:3]  # First 3 components as sample
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
