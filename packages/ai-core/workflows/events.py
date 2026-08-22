from typing import Dict, Any

# Leveraging our existing event system from ai-core/events
from packages.ai_core.events.event_system import EventSystem

class WorkflowEvents:
    """Standardized event names for the Workflow Engine."""
    STARTED = "workflow_started"
    FINISHED = "workflow_finished"
    FAILED = "workflow_failed"
    
    NODE_STARTED = "node_started"
    NODE_FINISHED = "node_finished"
    NODE_RETRY = "node_retry"
    
    CHECKPOINT_SAVED = "checkpoint_saved"
    CHECKPOINT_LOADED = "checkpoint_loaded"

async def publish_workflow_event(event_type: str, **kwargs):
    """Helper to publish workflow events."""
    await EventSystem.publish(event_type, **kwargs)
