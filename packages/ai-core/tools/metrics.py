import time
import logging
from typing import Callable, Any
from packages.ai_core.events.event_system import EventSystem

logger = logging.getLogger("tool_metrics")

class ToolMetrics:
    """
    Observability wrapper for tracking tool latency and success rates.
    Logs telemetry via EventSystem.
    """
    @staticmethod
    async def track_execution(tool_name: str, func: Callable, *args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            latency = (time.time() - start_time) * 1000
            
            await EventSystem.publish(
                "tool_execution_success",
                tool=tool_name,
                latency_ms=latency
            )
            return result, latency
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            await EventSystem.publish(
                "tool_execution_failure",
                tool=tool_name,
                latency_ms=latency,
                error=str(e)
            )
            raise e
