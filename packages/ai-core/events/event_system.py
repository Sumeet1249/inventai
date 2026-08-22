from typing import Callable, List, Dict
import asyncio

class EventSystem:
    """
    Simple Pub/Sub system for tracking AI lifecycle events (e.g., node started, tool executed).
    """
    _listeners: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: str, callback: Callable):
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(callback)

    @classmethod
    async def publish(cls, event_type: str, **kwargs):
        if event_type in cls._listeners:
            tasks = [callback(**kwargs) for callback in cls._listeners[event_type]]
            await asyncio.gather(*tasks, return_exceptions=True)
