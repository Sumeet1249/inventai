import json
from typing import AsyncGenerator

class WorkflowStreamer:
    """
    Handles streaming of workflow events and LLM tokens.
    Provides standard SSE (Server-Sent Events) formatting.
    """
    @staticmethod
    async def stream_graph(app, input_state: dict, config: dict) -> AsyncGenerator[str, None]:
        """Streams full graph execution updates."""
        try:
            async for output in app.astream(input_state, config=config):
                for node_name, node_output in output.items():
                    event = {
                        "type": "node_update",
                        "node": node_name,
                        "state_updates": {k: str(v) for k, v in node_output.items()}
                    }
                    yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'details': str(e)})}\n\n"
