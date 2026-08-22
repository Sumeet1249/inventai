# InventAI Physics Intelligence Engine

This Domain Microservice converts generic 3D models into validated engineering designs. It uses Physics-Informed Neural Networks (PINNs) via **DeepXDE** to solve PDEs for stress and heat transfer, replacing traditional slow FEA (Finite Element Analysis) solvers.

## Architecture

This service strictly follows Domain-Driven Design (DDD) and Clean Architecture:

- **`domain/`**: SQLAlchemy models (`Simulation`, `Material`, `Results`).
- **`simulations/`**: Python wrappers for DeepXDE neural network solvers.
- **`materials/`**: Database of material properties required for solving physical equations.
- **`application/`**: Orchestrates use cases by linking physics engines to AI Workflows.
- **`tools/`**: AI-Core compliant tools (`PhysicsSimulationTool`).
- **`workflows/`**: LangGraph state machines orchestrating `ai-core` agents (`PlannerAgent`, `ReviewerAgent`) to set up boundary conditions and review the safety factor.
- **`api/`**: FastAPI endpoints for triggering simulations.

## AI Core Integration

This service **does not** call OpenAI directly.
It uses our enterprise `ai-core` to safely sandbox the highly deterministic mathematical computing (DeepXDE) inside an intelligent agentic review loop.
