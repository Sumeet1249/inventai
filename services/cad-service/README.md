# InventAI CAD Intelligence & 3D Generation Engine

This Domain Microservice converts natural language and engineering requirements into manufacturable 3D CAD models using the `ai-core` and **CadQuery**.

## Architecture

This service strictly follows Domain-Driven Design (DDD) and Clean Architecture:

- **`domain/`**: SQLAlchemy models (`CADProject`, `CADModel`).
- **`generators/`**: Wraps the Python **CadQuery** geometry kernel.
- **`exporters/`**: Export logic for STEP (Manufacturing) and STL/GLTF (Three.js Web UI).
- **`validators/`**: Geometry rule checking against constraints.
- **`application/`**: Orchestrates use cases by linking generation to AI Workflows.
- **`tools/`**: AI-Core compliant tools (`CADGenerationTool`).
- **`workflows/`**: LangGraph state machines orchestrating `ai-core` agents (`PlannerAgent`, `ReviewerAgent`) to generate parameters and review resulting geometry.
- **`api/`**: FastAPI endpoints for generating and retrieving models.

## AI Core Integration

This service **does not** call OpenAI directly.
It uses our enterprise `ai-core` to securely spawn sandboxed Planner and Reviewer agents that execute the `CADGenerationTool`. This bridges deterministic geometry generation with abstract AI reasoning.
