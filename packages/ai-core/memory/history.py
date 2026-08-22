from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

class HistoryUtils:
    """
    Utilities for extracting, formatting, and truncating conversation histories
    for LLM prompts.
    """
    
    @staticmethod
    def extract_recent(messages: List[BaseMessage], k: int = 5) -> List[BaseMessage]:
        """Returns the last K messages, always preserving the SystemMessage if present."""
        if not messages:
            return []
            
        sys_msg = [m for m in messages if isinstance(m, SystemMessage)]
        recent = messages[-k:] if len(messages) > k else messages
        
        # Ensure we don't duplicate the system message
        if sys_msg and recent[0] != sys_msg[0]:
            return sys_msg + recent
        return recent
