# InventAI Enterprise Memory System

The `packages/ai-core/memory/` module is the universal persistence layer for all InventAI agents, workflows, and tools.

## Architecture Tiers

1. **Short-Term Memory**:

   - `CacheMemory`: Ephemeral Key-Value cache used heavily by the `ToolExecutor` and `AIModelFactory` for memoization.
   - `CheckpointMemory`: Native integration with LangGraph's state machine, persisting interrupted execution states.

2. **Long-Term Memory**:

   - `ConversationMemory`: Manages chat histories, utilizing `HistoryUtils` and auto-compression to maintain token limits.
   - `ProjectMemory`: Stores long-running state for entire InventAI projects (e.g., goals, constraints, completed patents).
   - `SessionMemory`: Ephemeral user contexts with strict TTLs.

3. **Knowledge Memory**:

   - `VectorMemory`: Provides RAG abstractions (`index_documents`, `search`). Crucially, this layer is decoupled from specific vendors (ChromaDB, Pinecone). The concrete `VectorStoreProvider` is injected at runtime.

## Usage

```python {"metadata":"[object Object]"}
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.conversation_memory import ConversationMemory

# Inject provider (e.g., RedisProvider)
manager = MemoryManager(provider=my_redis_provider)
conv_mem = ConversationMemory(manager)

await conv_mem.append_message(user_id="u1", thread_id="t1", message=HumanMessage(content="Hello"))
```
