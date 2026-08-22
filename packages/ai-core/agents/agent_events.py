from packages.ai_core.events.event_system import EventSystem

class AgentEvents:
    """Standardized event names for Agent telemetry."""
    STARTED = "agent_started"
    FINISHED = "agent_finished"
    FAILED = "agent_failed"
    TOOL_CALLED = "agent_tool_called"
    DELEGATED = "agent_delegated_task"

async def publish_agent_event(event_type: str, **kwargs):
    """Helper to publish agent events."""
    await EventSystem.publish(event_type, **kwargs)
