import time
from typing import Callable, Any
import logging

logger = logging.getLogger("ai_metrics")

class ModelMetrics:
    """
    Observability wrapper for tracing latency, token usage, and provider health.
    """
    @staticmethod
    async def track_latency(provider: str, func: Callable, *args, **kwargs) -> Any:
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            latency = (time.time() - start) * 1000
            logger.info(f"[{provider}] Call succeeded in {latency:.2f}ms")
            
            # Attach latency to result if it's a NormalizedAIResponse
            if hasattr(result, 'latency_ms'):
                result.latency_ms = latency
                
            return result
        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"[{provider}] Call failed after {latency:.2f}ms. Error: {str(e)}")
            raise
