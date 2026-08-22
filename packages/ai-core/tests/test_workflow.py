import pytest
from packages.ai_core.factories.ai_factory import AIFactory

def test_workflow_compilation():
    """
    Tests that the AIFactory successfully compiles a LangGraph workflow
    with memory and the standard nodes without throwing errors.
    """
    app = AIFactory.create_standard_workflow(provider="openai")
    assert app is not None
    
    nodes = app.nodes
    # Verify standard nodes exist
    assert "planner" in nodes
    assert "executor" in nodes
    assert "tools" in nodes
    assert "fallback" in nodes
