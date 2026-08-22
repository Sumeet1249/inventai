import chromadb
from typing import List, Dict, Any
import os

class ChromaVectorStore:
    """
    Manages connection and querying against ChromaDB for local patent caching.
    """
    def __init__(self, persist_directory: str = "./chroma_data"):
        # For local development, we use PersistentClient.
        # In production, we would use chromadb.HttpClient to a real DB.
        db_path = os.getenv("CHROMADB_PATH", persist_directory)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = "patent_prior_art"
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_patents(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], documents: List[str]):
        """Indexes patents into ChromaDB."""
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Searches for similar patents based on dense vector embedding."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format the results
        formatted_results = []
        if results and results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        return formatted_results

vector_store = ChromaVectorStore()
