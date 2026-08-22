# InventAI Enterprise Tool Framework

The `packages/ai-core/tools/` module provides a hardened sandbox for all external AI operations.

Domain Services (Patent, CAD, Research) **MUST NEVER** allow agents to call APIs directly. All capabilities must be registered as tools in this framework.

## Core Features

- **Strict I/O Validation**: The `ToolValidator` uses Pydantic schemas to validate inputs before execution and outputs before returning them to the LLM.
- **Permission Sandbox**: The `ToolPermissionManager` ensures agents only execute tools they have explicit authorization for (e.g., stopping a read-only agent from executing a database write tool).
- **Resilient Execution**: The `ToolExecutor` wraps all calls in Tenacity retries and strict `asyncio` timeouts.
- **Semantic Caching**: Deterministic tool outputs are cached in Redis via `ToolCache`, saving latency and API costs.
- **LangChain Integration**: The `ToolFactory` dynamically compiles our strict `BaseTool` objects into native LangChain `StructuredTool` objects for seamless injection into the Workflow Engine.

## Usage

```python {"metadata":"[object Object]"}
from packages.ai_core.tools.factory import ToolFactory
from packages.ai_core.tools.context import ToolContext

# Create Context
context = ToolContext(session_id="123", workflow_id="abc", agent_id="planner", roles=["admin"])

# Build LangChain Tool
lc_tool = ToolFactory.to_langchain_tool(my_custom_tool, context)

# Pass to Workflow
workflow.build_standard_edges(tools=[lc_tool])
```
