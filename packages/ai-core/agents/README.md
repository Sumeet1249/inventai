# InventAI Multi-Agent Framework

The `packages/ai-core/agents/` module is the master abstraction for all business agents in InventAI.

Domain Services (Patent, CAD) **MUST NOT** implement raw LangChain agent loops. They must inherit from this framework or use the pre-built roles.

## Core Architecture
- **Dependency Injection (`agent_factory.py`)**: The Factory automatically injects the `AIModelFactory` (for failovers) and `MemoryManager` (for persistence) into every agent upon creation.
- **Base Enterprise Agent**: The `BaseEnterpriseAgent` wraps all execution in `AgentMetrics`, ensuring telemetry for LLM tokens and execution time is always logged via the `EventSystem`.
- **Specialized Roles**: 
  - `PlannerAgent`: Decomposes tasks.
  - `WorkerAgent`: Executes tools.
  - `ReviewerAgent`: Validates constraints.
  - `SupervisorAgent`: Manages retries and loops.
  - `CriticAgent`, `RouterAgent`, `CoordinatorAgent`: For complex Swarm setups.

## Delegation and State
Agents communicate by passing `AgentState`. 
To prevent infinite delegation loops, the `BaseEnterpriseAgent` enforces a strict `max_delegation_depth` configured in `.env`.
