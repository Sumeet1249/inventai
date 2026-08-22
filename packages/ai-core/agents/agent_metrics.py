import time
import logging
from typing import Callable, Any
from packages.ai_core.agents.agent_events import publish_agent_event

logger = logging.getLogger("agent_metrics")

class AgentMetrics:
    """
    Observability wrapper for tracing agent execution time and success.
    """
    @staticmethod
    async def track_execution(agent_id: str, func: Callable, *args, **kwargs) -> Any:
        start_time = time.time()
        await publish_agent_event("agent_started", agent_id=agent_id)
        
        try:
            result = await func(*args, **kwargs)
            latency = (time.time() - start_time) * 1000
            
            await publish_agent_event("agent_finished", agent_id=agent_id, latency_ms=latency)
            return result
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            await publish_agent_event("agent_failed", agent_id=agent_id, latency_ms=latency, error=str(e))
            logger.error(f"[{agent_id}] Execution failed after {latency:.2f}ms. Error: {str(e)}")
            raise e
