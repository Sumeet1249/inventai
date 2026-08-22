# InventAI Enterprise Model Layer

The `packages/ai-core/models/` module provides a hardened abstraction layer over all external LLM providers. 

InventAI Domain Services (Patent, CAD, Research) **MUST NEVER** call OpenAI, Anthropic, or Groq directly using LangChain or SDKs. They must strictly use the `AIModelFactory`.

## Core Features
- **Automatic Failovers**: If OpenAI goes down or rate-limits, the Factory transparently redirects the request to Anthropic (based on `config.default_failover_chain`).
- **Response Normalization**: All providers (no matter how their APIs differ) return a strict `NormalizedAIResponse` object containing the `content`, exact `TokenUsage`, and calculated `latency_ms`.
- **Semantic Caching**: Identical requests hit the Redis `SemanticCache`, skipping the API call entirely to save latency and costs.
- **Observability**: `ModelMetrics` automatically wraps calls, logging provider latency and health to our central telemetry.

## Usage
```python
from packages.ai_core.models.factory import AIModelFactory
from langchain_core.messages import HumanMessage

# Instantiate the factory (defaults to failover chains in .env)
factory = AIModelFactory(preferred_provider="openai")

# Generate returns a NormalizedAIResponse
response = await factory.generate([HumanMessage(content="Hello")])

print(f"Provider: {response.provider}")
print(f"Total Tokens: {response.usage.total_tokens}")
```
