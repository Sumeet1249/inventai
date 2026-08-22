# 🚀 InventAI Backend Services - Startup Guide

## Overview

InventAI is a **Docker-based microservices architecture** with 11 backend services and multiple supporting infrastructure components. All services are designed to run in Docker containers.

## 📋 Architecture

### **Microservices (11 total)**
1. **auth-service** (Port 8001) - Authentication & JWT tokens
2. **business-service** (Port 8002) - Business & venture analysis
3. **cad-service** (Port 8005) - CAD generation & design
4. **patent-service** (Port 8003) - Patent search & analysis
5. **physics-service** (Port 8006) - Physics simulation
6. **research-service** (Port 8004) - Research & RAG
7. **report-service** (Port 8008) - Report generation
8. **graph-service** (Port 8009) - Knowledge graph
9. **innovation-engine** (Port 8010) - Master innovation workflow
10. **ai-agent-service** - AI agent orchestration
11. **business-service** - Business metrics

### **Infrastructure (via Docker Compose)**
- **PostgreSQL** (Port 5432) - Primary database
- **Neo4j** (Port 7687) - Knowledge graph database
- **Redis** (Port 6379) - Cache & message broker
- **RabbitMQ** (Port 5672) - Message queue
- **ChromaDB** (Port 8000) - Vector database
- **MinIO** (Port 9000) - Object storage
- **Prometheus** (Port 9090) - Metrics
- **Grafana** (Port 3000) - Dashboards
- **Jaeger** (Port 16686) - Distributed tracing

---

## 🐳 Quick Start with Docker Compose

### Prerequisites
- Docker & Docker Compose installed
- Git cloned: `https://github.com/Sumeet1249/inventai`
- `.env` file configured (see Environment Setup below)

### 1️⃣ Start All Services

```bash
# Navigate to project root
cd inventAI-main

# Start all services (databases, microservices, frontend)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2️⃣ Verify Services Are Running

```bash
# Check health of each service
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8002/health  # Business Service
curl http://localhost:8005/health  # CAD Service
curl http://localhost:8004/health  # Research Service
curl http://localhost:8003/health  # Patent Service
```

### 3️⃣ Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3001 | Web UI |
| API Gateway (Nginx) | http://localhost:8080 | API endpoints |
| Auth Service | http://localhost:8001 | Authentication |
| CAD Service | http://localhost:8005 | CAD generation |
| Neo4j Browser | http://localhost:7474 | Graph database UI |
| RabbitMQ UI | http://localhost:15672 | Message queue UI |
| MinIO Console | http://localhost:9001 | Object storage UI |
| Grafana | http://localhost:3000 | Dashboards |

---

## 🔧 Environment Setup

### Create `.env` File

```bash
# Copy from example
cp .env.example .env

# Edit .env with your values
nano .env  # or vim, code, etc.
```

### Required Environment Variables

```env
# LLM Providers
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
HF_TOKEN=hf_...
DEFAULT_LLM_MODEL=gemini-2.0-flash
DEFAULT_LLM_PROVIDER=gemini

# LangSmith Observability
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=InventAI-Dev

# Database
POSTGRES_USER=inventai
POSTGRES_PASSWORD=supersecret
POSTGRES_DB=inventai
DATABASE_URL=postgresql://inventai:supersecret@postgres:5432/inventai

# Neo4j
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Cache & Message Broker
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Storage
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=password123

# Security
JWT_SECRET=inventai-jwt-secret-key-2024-change-in-production
JWT_ALGORITHM=HS256
```

---

## 📊 Service Details

### Auth Service
- **Path**: `services/auth-service/`
- **Main**: `app/main.py`
- **Dependencies**: FastAPI, SQLAlchemy, Pydantic, JWT
- **Entry**: `uvicorn app.main:app`
- **Port**: 8000 (in container)

### CAD Service
- **Path**: `services/cad-service/`
- **Main**: `app/main.py`
- **Dependencies**: FastAPI, CadQuery, transformers, torch (GPU)
- **Entry**: `uvicorn app.main:app`
- **Port**: 8000 (in container)
- **GPU**: Requires NVIDIA GPU for inference

### Innovation Engine
- **Path**: `services/innovation-engine/`
- **Dependencies**: LangGraph, LangChain, ChromaDB
- **Main Entry**: Master workflow orchestrator
- **Port**: 8000 (in container)

### Research Service
- **Path**: `services/research-service/`
- **Main**: `application/research_service.py:app`
- **Dependencies**: LangChain, ChromaDB, LlamaIndex
- **Entry**: `uvicorn services.research_service.application.research_service:app`
- **Port**: 8000 (in container)

### Patent Service
- **Path**: `services/patent-service/`
- **Dependencies**: FastAPI, LangChain, embeddings
- **Main**: `app/main.py`
- **Port**: 8000 (in container)

### Physics Service
- **Path**: `services/physics-service/`
- **Dependencies**: FastAPI, DeepXDE, NumPy, SciPy
- **Main**: `application/physics_service.py:app`
- **Entry**: `uvicorn services.physics_service.application.physics_service:app`
- **Port**: 8000 (in container)

### Report Service
- **Path**: `services/report-service/`
- **Dependencies**: FastAPI, Jinja2, ReportLab, DOCX
- **Main**: `application/report_service.py:app`
- **Entry**: `uvicorn services.report_service.application.report_service:app`
- **Port**: 8000 (in container)

### Graph Service
- **Path**: `services/graph-service/`
- **Dependencies**: FastAPI, Neo4j, LangChain
- **Port**: 8000 (in container)

### Business Service
- **Path**: `services/business-service/`
- **Main**: `app/main.py`
- **Port**: 8000 (in container)

---

## 🛠️ Common Operations

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service
docker-compose logs -f cad-service

# Last 100 lines
docker-compose logs --tail=100 research-service
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific
docker-compose restart auth-service cad-service

# Rebuild and restart
docker-compose up -d --build auth-service
```

### Stop Services
```bash
# Stop all
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Stop without removing
docker-compose stop
```

### Enter Service Container
```bash
docker-compose exec auth-service bash
docker-compose exec cad-service bash
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U inventai -d inventai

# Access Neo4j
# Via browser: http://localhost:7474

# Access Redis
docker-compose exec redis redis-cli
```

---

## 🔍 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs auth-service

# Common issues:
# 1. Port already in use
netstat -an | grep LISTEN

# 2. Volume permission error
sudo chown -R $(id -u):$(id -g) ./volumes

# 3. Out of memory
# Increase Docker memory allocation
```

### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose exec postgres pg_isready

# Check connection string in .env
DATABASE_URL=postgresql://user:password@postgres:5432/inventai

# Verify networks
docker network ls
```

### Model Download Timeout (CAD Service)
```bash
# Download models before building
python download_cad_model.py

# Or increase timeout in Dockerfile
timeout 3600 python -m transformers.utils.import_utils ...
```

### GPU Not Detected (CAD Service)
```bash
# Check if NVIDIA Docker is installed
nvidia-docker version

# Verify GPU access
docker-compose exec cad-service nvidia-smi
```

---

## 📈 Monitoring

### Prometheus
- **URL**: http://localhost:9090
- **Metrics**: All services expose `/metrics`

### Grafana
- **URL**: http://localhost:3000
- **Default**: admin/admin
- **Dashboards**: Pre-configured for Prometheus

### Jaeger Tracing
- **URL**: http://localhost:16686
- **Traces**: Distributed tracing for requests

### RabbitMQ Management
- **URL**: http://localhost:15672
- **Default**: guest/guest
- **Queues**: Monitor message queues

---

## 🧪 Testing Services

### Test API Endpoint
```bash
# Auth Service
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"pass123"}'

# Health check
curl http://localhost:8001/health
```

### Run Python Tests
```bash
# Test innovation-engine
docker-compose exec innovation-engine pytest services/innovation-engine/tests/ -v

# Test research-service
docker-compose exec research-service pytest services/research_service/tests/ -v
```

---

## 🚨 Known Issues & Solutions

### Issue 1: Service Import Errors
**Problem**: `ModuleNotFoundError: No module named 'services'`
**Solution**: Dockerfiles automatically rename folders (ai-core → ai_core, etc.)
**Status**: ✅ Fixed in Dockerfiles

### Issue 2: Port Conflicts
**Problem**: Port 3000/8000 already in use
**Solution**: Change ports in docker-compose.yml or kill process
```bash
# Kill process on port 3000
lsof -ti :3000 | xargs kill -9
```

### Issue 3: Out of Memory
**Problem**: Docker runs out of memory
**Solution**: Increase Docker memory or reduce services
```bash
# Remove specific services
docker-compose down
docker-compose up -d --scale cad-service=0
```

---

## 📞 Support

### Debug Mode
```bash
# Enable verbose logging
export DEBUG=true
docker-compose up

# Or in docker-compose.yml:
environment:
  - DEBUG=true
  - LOG_LEVEL=DEBUG
```

### Check Service Health
```bash
#!/bin/bash
for service in auth-service cad-service research-service patent-service physics-service report-service graph-service business-service; do
  echo "Checking $service..."
  curl -s http://localhost:8080/api/$service/health || echo "Failed"
done
```

---

## ✅ Deployment Checklist

- [ ] All `.env` variables configured
- [ ] Docker & Docker Compose installed
- [ ] Enough disk space (CAD models ~5GB)
- [ ] GPU available for CAD service (optional)
- [ ] PostgreSQL initialized
- [ ] All services showing "Running" status
- [ ] Health checks passing
- [ ] Logs show no errors

---

## 🎯 Next Steps

1. **Start Docker Compose**: `docker-compose up -d`
2. **Verify Services**: Check `/health` endpoints
3. **Access Frontend**: http://localhost:3001
4. **Explore APIs**: http://localhost:8080/api/v1
5. **Monitor Metrics**: http://localhost:3000 (Grafana)

---

## 📚 Additional Resources

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://python.langchain.com/)
- [Neo4j Docs](https://neo4j.com/docs/)

---

**Last Updated**: August 22, 2026
**Version**: 1.0.0
**Status**: Production Ready 🚀
