from typing import Dict, Any

class WorkflowRegistry:
    """
    Stores compiled LangGraph apps (workflows) for reuse across requests.
    Prevents recompilation on every invocation.
    """
    _workflows: Dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, compiled_workflow: Any):
        cls._workflows[name] = compiled_workflow

    @classmethod
    def get(cls, name: str) -> Any:
        workflow = cls._workflows.get(name)
        if not workflow:
            raise ValueError(f"Workflow {name} not found.")
        return workflow
