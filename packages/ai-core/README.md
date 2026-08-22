# InventAI Core AI Orchestration Engine

This package (`packages/ai-core`) provides the reusable, domain-agnostic foundation for all AI agents within the InventAI ecosystem. 

It implements **Clean Architecture** and **Dependency Injection** (via `AIFactory`) to ensure that our swarm is testable, decoupled, and highly scalable.

## Key Features
- **LangGraph Integration**: State-machine based orchestration with Redis-backed checkpointing.
- **LangChain Wrappers**: Robust abstractions for LLMs, Parsers, and Prompts.
- **Resilience**: Tenacity-powered exponential backoff and LangGraph fallback nodes.
- **Dynamic Tools**: Decorator-based `ToolRegistry` allowing microservices to safely inject their tools into the graph.

## Usage
Microservices should NEVER instantiate `BaseAgent` directly. Use the `AIFactory`:

```python
from packages.ai_core.factories.ai_factory import AIFactory

app = AIFactory.create_standard_workflow(
    provider="anthropic",
    tools=[my_custom_tool]
)
```
