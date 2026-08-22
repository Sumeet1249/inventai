# InventAI Patent Intelligence Engine

This is the first primary Domain Microservice in the InventAI ecosystem. It provides the core business logic for semantic patent search, prior-art detection, and novelty scoring.

## Architecture

This service strictly follows Domain-Driven Design (DDD) and Clean Architecture:

- **`domain/`**: SQLAlchemy models (`Patent`, `Inventor`, `AnalysisResult`).
- **`repositories/`**: Abstracts DB access.
- **`application/`**: Orchestrates use cases by linking repositories to AI Workflows.
- **`tools/`**: AI-Core compliant tools (`PatentSearchTool`, `NoveltyAnalysisTool`).
- **`workflows/`**: LangGraph state machines orchestrating `ai-core` agents (`PlannerAgent`, `ReviewerAgent`).
- **`api/`**: FastAPI endpoints.

## AI Core Integration

This service **does not** call OpenAI directly or write generic LLM wrappers.
All AI capabilities are executed by instantiating enterprise agents from `packages/ai-core/agents/` and tools from `packages/ai-core/tools/`. The orchestration loop runs inside `packages/ai-core/workflows/`.
