# InventAI Innovation Engine (Master Orchestrator)

This Domain Microservice acts as the central nervous system for the entire InventAI platform. It is responsible for orchestrating the end-to-end invention lifecycle across all other domain microservices.

## Architecture

This service strictly follows Domain-Driven Design (DDD) and Clean Architecture:

- **`domain/`**: Pydantic models tracking overarching `ProjectState`.
- **`events/`**: An `InMemoryEventBus` (precursor to RabbitMQ/Redis) that broadcasts granular state changes (e.g. `NodeStarted`, `NodeCompleted`) so that UIs can track long-running workflow progress.
- **`orchestrator/`**: AI tools (e.g., `CallPatentServiceTool`) that abstract HTTP calls to our other microservices.
- **`workflow/`**: The master LangGraph state machine orchestrating: `Patent -> Research -> Graph -> CAD -> Physics -> Reports`.
- **`application/`**: Coordinates the master workflow and tracks state in the database.
- **`api/`**: FastAPI endpoints to start and resume projects.

## AI Core Integration

This service utilizes the `ai-core` memory system (for workflow checkpointing) and LangGraph to string together multiple independent domain services into one cohesive platform.
