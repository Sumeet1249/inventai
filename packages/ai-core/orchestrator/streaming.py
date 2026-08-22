import json
from typing import AsyncGenerator

async def stream_graph_updates(app, input_data: dict, config: dict) -> AsyncGenerator[str, None]:
    """
    Streams updates from a compiled LangGraph application using Server-Sent Events (SSE).
    """
    try:
        async for output in app.astream(input_data, config=config):
            # output is a dict mapping node_name to node_output
            for node_name, node_output in output.items():
                event_data = {
                    "node": node_name,
                    "status": "completed",
                    # Clean up complex objects for JSON serialization
                    "details": str(node_output) 
                }
                yield f"data: {json.dumps(event_data)}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
