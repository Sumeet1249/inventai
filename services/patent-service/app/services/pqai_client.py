import httpx
from packages.schemas.models import Patent

class PQAIClient:
    def __init__(self):
        self.base_url = "https://api.projectq.org/v1"
        
    async def search_prior_art(self, query: str) -> list[Patent]:
        import logging
        
        async with httpx.AsyncClient() as client:
            try:
                # Use PatentsView API as a reliable open endpoint
                url = f'https://api.patentsview.org/patents/query?q={{"_text_any":{{"patent_title":"{query}"}}}}&f=["patent_id","patent_title","patent_abstract"]'
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    patents = []
                    for p in data.get("patents", [])[:3]:
                        patents.append(Patent(
                            id=p.get("patent_id", "Unknown"),
                            title=p.get("patent_title", "Unknown"),
                            abstract=p.get("patent_abstract", "Unknown"),
                            technology_domain="Mixed"
                        ))
                    if patents:
                        return patents
                else:
                    logging.warning(f"Patents API returned {response.status_code}")
            except Exception as e:
                logging.warning(f"Patents API error: {e}")
                
        # Degraded Mode Fallback
        logging.warning("Falling back to degraded mock patent data.")
        return [
            Patent(
                id="US-FALLBACK",
                title=f"[Degraded Mode] Prior Art for: {query}",
                abstract="The external patent API is currently unavailable. This is a degraded mode fallback.",
                technology_domain="AI"
            )
        ]
