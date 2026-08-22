from llama_index.core import VectorStoreIndex, Document
from packages.embeddings.chroma_client import vector_store

class ResearchRAGService:
    def __init__(self):
        self.collection = vector_store.get_collection("research_papers")
        
    def ingest_paper(self, text: str, metadata: dict):
        # In a real scenario, this connects ChromaDB vector store with LlamaIndex
        doc = Document(text=text, metadata=metadata)
        # index = VectorStoreIndex.from_documents([doc])
        # ... logic to store to chroma ...
        pass
        
    def query(self, question: str):
        # Retrieve chunks from ChromaDB and synthesize response
        # Using LlamaIndex query engine
        results = self.collection.query(
            query_texts=[question],
            n_results=5
        )
        return results
