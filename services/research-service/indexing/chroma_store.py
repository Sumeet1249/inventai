import chromadb
from typing import List, Dict, Any
from packages.ai_core.memory.interfaces import VectorStoreProvider

class ChromaVectorStore(VectorStoreProvider):
    def __init__(self, collection_name: str = "research_papers", persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    async def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        ids = [doc.get("id", str(i)) for i, doc in enumerate(documents)]
        texts = [doc.get("text", "") for doc in documents]
        metadatas = [{k: v for k, v in doc.items() if k not in ["id", "text"]} for doc in documents]
        
        # Ensure we have metadata for every document, even if empty dicts
        metadatas = [m if m else {"source": "unknown"} for m in metadatas]

        self.collection.upsert(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    async def semantic_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        output = []
        if results and "documents" in results and results["documents"]:
            for i in range(len(results["documents"][0])):
                doc = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "score": results["distances"][0][i] if "distances" in results and results["distances"] else 0.0,
                }
                if "metadatas" in results and results["metadatas"] and results["metadatas"][0]:
                    doc.update(results["metadatas"][0][i])
                output.append(doc)
        return output
