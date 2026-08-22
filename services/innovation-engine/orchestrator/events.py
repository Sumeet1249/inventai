import asyncio
import json
from typing import AsyncGenerator, Dict

class EventStreamer:
    """Manages SSE streams for LangGraph execution."""
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}

    def get_queue(self, project_id: str) -> asyncio.Queue:
        if project_id not in self._queues:
            self._queues[project_id] = asyncio.Queue()
        return self._queues[project_id]

    async def publish(self, project_id: str, event_type: str, payload: dict):
        """Pushes an SSE event to the specific project stream."""
        queue = self.get_queue(project_id)
        message = {
            "event": event_type,
            "data": payload
        }
        await queue.put(message)

    async def subscribe(self, project_id: str) -> AsyncGenerator[str, None]:
        """Yields SSE formatted strings."""
        queue = self.get_queue(project_id)
        try:
            while True:
                message = await queue.get()
                # Server-Sent Events format
                yield f"event: {message['event']}\ndata: {json.dumps(message['data'])}\n\n"
                
                if message['event'] == "WorkflowCompleted" or message['event'] == "WorkflowFailed":
                    break
        finally:
            if project_id in self._queues:
                del self._queues[project_id]

event_streamer = EventStreamer()
