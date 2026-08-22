# InventAI Graph Intelligence Service

This Domain Microservice handles the storage and traversal of the enterprise Knowledge Graph.
It links patents, research papers, materials, processes, and products to uncover hidden technological synergies.

## Architecture

This service strictly follows Domain-Driven Design (DDD) and Clean Architecture:

- **`api/`**: FastAPI endpoints for retrieving subgraphs and triggering recommendations.
- **`application/`**: Orchestrates use cases by linking repositories to Neo4j queries and AI Workflows.
- **`cypher/`**: Centralized storage for Neo4j Cypher queries.
- **`domain/`**: SQLAlchemy models (if applicable) and Pydantic schemas.
- **`infrastructure/`**: The `Neo4jDriver` using the official `neo4j` Python driver to manage database connections and transactions.
- **`tools/`**: AI-Core compliant tools for graph traversal.
- **`workflows/`**: LangGraph state machines orchestrating `ai-core` agents (`GraphWalkerAgent`) for deducing insights.

## Integration

- **Backend**: Relies on a Neo4j database instance (configurable via `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`).
- **Frontend**: The `/api/v1/graph/subgraph/{node_id}` endpoint formats the graph output specifically for `Cytoscape.js` visualization on the web dashboard.
- **AI Core**: Integrates with `packages/ai-core` for memory management and orchestration.
