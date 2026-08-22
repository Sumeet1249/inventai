# InventAI Advanced Workflow Engine

The `workflows/` directory contains the highly advanced, LangGraph-powered orchestration engine for InventAI.

## Architecture

The workflow implements a standard orchestration loop:
`Planner -> Router -> Executor -> Router -> Reviewer -> End`

It utilizes LangGraph's advanced features:
- **Conditional Edges**: Handled by `TaskRouter` which routes tasks dynamically based on execution state and errors.
- **Persistence Hooks**: Handled by `WorkflowCheckpointManager` using `MemorySaver` (pluggable with Postgres/Redis).
- **Streaming**: Handled by `WorkflowStreamer` which converts LangGraph's native asynchronous generators into robust Server-Sent Events (SSE).

## Execution Modes
The `ExecutionEngine` wraps the compiled `StateGraph` and exposes:
- `execute_async()`: For standard asynchronous processing.
- `execute_sync()`: For legacy wrapper systems.
- `stream_async()`: For real-time frontend UI updates.
