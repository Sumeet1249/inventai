import asyncio
from typing import Callable, List
from services.innovation_engine.domain.project_models import WorkflowEvent

class InMemoryEventBus:
    """
    Synchronous/Asynchronous event bus for tracking workflow state.
    In production, this would wrap RabbitMQ or Redis PubSub.
    """
    def __init__(self):
        self.subscribers: List[Callable] = []

    def subscribe(self, callback: Callable):
        self.subscribers.append(callback)

    async def publish(self, event: WorkflowEvent):
        """Broadcasts events to all listeners (e.g., WebSockets for UI)."""
        # Mock printing for now
        print(f"[EVENT BUS] {event.timestamp} | {event.event_type} | {event.node}")
        
        for sub in self.subscribers:
            if asyncio.iscoroutinefunction(sub):
                await sub(event)
            else:
                sub(event)

# Global singleton for the application
event_bus = InMemoryEventBus()
