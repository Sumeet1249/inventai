# InventAI Research Intelligence Engine

This Domain Microservice transforms the InventAI platform into an Enterprise Retrieval-Augmented Generation (RAG) assistant, replacing previous mocked stubs with real intelligence pipelines.

## Architecture

This service strictly follows Domain-Driven Design (DDD) and Clean Architecture:

- **`api/`**: FastAPI endpoints for uploading papers, querying the knowledge base, fetching citations, and getting history.
- **`application/`**: Orchestrates use cases by linking repositories to RAG AI Workflows and the Citation Engine.
- **`citations/`**: Graph-based citation tracking and relation building using `NetworkX`.
- **`domain/`**: SQLAlchemy models (`ResearchPaper`, `Document`, `Analysis`).
- **`embeddings/`**: Vector embedding generation powered by `sentence-transformers`.
- **`indexing/`**: Real vector storage and semantic search powered by `ChromaDB`.
- **`infrastructure/`**: Database integration and dependency injection.
- **`ingestion/`**: Document parsing and chunking powered by `LlamaIndex` and `PyMuPDF`.
- **`tools/`**: AI-Core compliant tools (`DocumentSearchTool`, `SummarizationTool`) that interface with LangChain and LlamaIndex.
- **`workflows/`**: LangGraph state machines orchestrating `ai-core` agents (`PlannerAgent`, `WorkerAgent`) for extracting and synthesizing knowledge.

## AI Core Integration

This service utilizes `packages/ai-core/agents/` and tools from `packages/ai-core/tools/`. The multi-step reasoning RAG loop runs inside `packages/ai-core/workflows/`.
It leverages `LangChain` for orchestration and `LlamaIndex` for document management.
