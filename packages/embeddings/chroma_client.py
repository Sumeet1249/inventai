import chromadb
from chromadb.config import Settings
import os

class ChromaStore:
    def __init__(self):
        host = os.getenv("CHROMA_HOST", "localhost")
        port = os.getenv("CHROMA_PORT", "8000")
        
        self.client = chromadb.HttpClient(
            host=host, 
            port=port, 
            settings=Settings(allow_reset=True)
        )
        
    def get_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

# Singleton instance
vector_store = ChromaStore()
