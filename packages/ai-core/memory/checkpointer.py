from packages.ai_core.interfaces.core_interfaces import BaseCheckpoint
from langgraph.checkpoint.memory import MemorySaver
# In production, swap with PostgresSaver or RedisSaver
# from langgraph.checkpoint.postgres import PostgresSaver

class CheckpointManager(BaseCheckpoint):
    def __init__(self):
        # We hold the saver in memory for the lifecycle of the factory
        self.saver = MemorySaver()
        
    def get_saver(self):
        return self.saver
