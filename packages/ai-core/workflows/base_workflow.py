from abc import ABC, abstractmethod

class BaseWorkflow(ABC):
    """
    Abstract Workflow Interface. All orchestration engines must implement this.
    """
    
    @abstractmethod
    def build(self):
        """Constructs the nodes and edges."""
        pass
        
    @abstractmethod
    def compile(self):
        """Compiles the workflow into an executable app."""
        pass
