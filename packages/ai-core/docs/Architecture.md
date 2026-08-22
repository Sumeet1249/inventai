# AI Core Architecture

The `ai-core` package enforces a strict separation of concerns:

## 1. Dependency Injection (`factories/ai_factory.py`)
All dependencies (LLMs, Checkpointers, PromptManagers) are initialized in the `AIFactory` and passed into the agents. This allows easy mocking during unit tests.

## 2. Abstractions (`interfaces/`)
Abstract Base Classes (ABCs) enforce strict contracts for `BaseMemory`, `BaseCheckpoint`, and `BaseToolInterface`.

## 3. Resilience (`utils/retry_manager.py` & `error_recovery.py`)
Network calls to LLMs fail. The AI Core handles this gracefully at two levels:
1. **Micro**: The `tenacity` retry manager wraps all `ainvoke` calls with exponential backoff.
2. **Macro**: If the LLM repeatedly fails, the LangGraph `route_on_error` condition routes the state machine to a `fallback_recovery_node` rather than crashing the API.

## 4. Pub/Sub Events (`events/event_system.py`)
Nodes emit lifecycle events (`llm_call_started`, `planner_success`). This allows the `metrics` and `logger` packages to hook into the AI without creating circular dependencies.
