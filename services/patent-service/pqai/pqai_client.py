import httpx
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PQAIClient:
    """
    Client for interacting with the external PQAI Semantic Search API.
    """
    def __init__(self):
        # We assume there is a local proxy or public endpoint for PQAI
        self.base_url = "https://api.projectq.ai/search" # Example endpoint

    async def search_prior_art(self, idea_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries PQAI for prior art based on the invention idea text.
        """
        payload = {
            "q": idea_text,
            "limit": top_k
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # We use a short timeout so that if PQAI fails, we can gracefully degrade to ChromaDB
                response = await client.get(self.base_url, params=payload, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    # Map PQAI response to our internal structure
                    results = []
                    for item in data.get("results", []):
                        results.append({
                            "id": item.get("id", "Unknown"),
                            "title": item.get("title", "No Title"),
                            "abstract": item.get("abstract", ""),
                            "score": item.get("score", 0.0)
                        })
                    return results
                else:
                    logger.warning(f"PQAI returned status {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error querying PQAI: {e}")
            return []

pqai_client = PQAIClient()
