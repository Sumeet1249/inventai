import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="InventAI API Gateway")

# Internal service URLs (in production, these come from env vars or service discovery)
SERVICES = {
    "patents": "http://patent-service:8000/api/v1/patents",
    "research": "http://research-service:8000",
    "cad": "http://cad-service:8000",
    "agents": "http://ai-agent-service:8000"
}

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def reverse_proxy(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        return JSONResponse({"error": "Service not found"}, status_code=404)
        
    base_url = SERVICES[service_name]
    target_url = f"{base_url}/{path}"
    
    async with httpx.AsyncClient() as client:
        req = client.build_request(
            request.method,
            target_url,
            headers=request.headers.raw,
            content=await request.body()
        )
        response = await client.send(req)
        
    return JSONResponse(
        content=response.json() if response.content else None,
        status_code=response.status_code
    )

@app.get("/health")
def health():
    return {"status": "Gateway online"}
