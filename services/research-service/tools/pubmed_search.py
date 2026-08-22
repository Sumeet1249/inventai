import urllib.request
import urllib.parse
import json
from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext

class PubmedSearchInput(BaseModel):
    query: str = Field(description="The medical/scientific search query for PubMed/EuropePMC.")
    top_k: int = Field(default=5, description="Number of papers to retrieve.")

class PubmedSearchOutput(BaseModel):
    results: list[Dict[str, Any]]

class PubmedSearchTool(BaseTool):
    name = "pubmed_search"
    description = "Searches the PubMed database for medical and biological research papers."
    tags = ["search", "rag", "research", "pubmed", "biology", "medical"]
    input_schema = PubmedSearchInput
    output_schema = PubmedSearchOutput

    async def execute(self, inputs: PubmedSearchInput, context: ToolContext) -> PubmedSearchOutput:
        # Using Europe PMC API which aggregates PubMed and provides an easy JSON response
        base_url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'
        search_query = urllib.parse.quote(inputs.query)
        url = f'{base_url}query={search_query}&format=json&resultType=core'
        
        results = []
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                result_list = data.get('resultList', {}).get('result', [])
                for entry in result_list[:inputs.top_k]:
                    title = entry.get('title', '')
                    abstract = entry.get('abstractText', '')
                    # Some don't have abstract, fallback to title
                    text = abstract if abstract else title
                    
                    link = f"https://europepmc.org/article/MED/{entry.get('pmid')}" if entry.get('pmid') else ""
                    
                    results.append({
                        "title": title,
                        "text": text,  # map to 'text' for workflow
                        "source": link,
                        "authors": entry.get('authorString', '')
                    })
        except Exception as e:
            results.append({"error": f"Failed to fetch from PubMed/EuropePMC: {str(e)}"})
            
        return PubmedSearchOutput(results=results)
