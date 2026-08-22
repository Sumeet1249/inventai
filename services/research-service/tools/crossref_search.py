import urllib.request
import urllib.parse
import json
from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext

class CrossrefSearchInput(BaseModel):
    query: str = Field(description="The scientific/academic search query for CrossRef.")
    top_k: int = Field(default=2, description="Number of papers to retrieve.")

class CrossrefSearchOutput(BaseModel):
    results: list[Dict[str, Any]]

class CrossrefSearchTool(BaseTool):
    name = "crossref_search"
    description = "Searches the CrossRef database for broad academic metadata and abstracts."
    tags = ["search", "rag", "research", "crossref", "academic"]
    input_schema = CrossrefSearchInput
    output_schema = CrossrefSearchOutput

    async def execute(self, inputs: CrossrefSearchInput, context: ToolContext) -> CrossrefSearchOutput:
        base_url = 'https://api.crossref.org/works?'
        search_query = urllib.parse.quote(inputs.query)
        url = f'{base_url}query={search_query}&select=title,abstract,author,URL&rows={inputs.top_k}'
        
        results = []
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'InventAI/1.0 (mailto:admin@inventai.com)'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                result_list = data.get('message', {}).get('items', [])
                for entry in result_list:
                    title = entry.get('title', [''])[0] if entry.get('title') else ''
                    abstract = entry.get('abstract', '')
                    # Cleanup crossref abstract which might contain XML/JATS tags like <jats:p>
                    if abstract:
                        import re
                        abstract = re.sub(r'<[^>]+>', '', abstract)
                        
                    text = abstract if abstract else title
                    link = entry.get('URL', '')
                    
                    authors = []
                    for a in entry.get('author', []):
                        if 'given' in a and 'family' in a:
                            authors.append(f"{a['given']} {a['family']}")
                            
                    results.append({
                        "title": title,
                        "text": text,
                        "source": link,
                        "authors": ", ".join(authors)
                    })
        except Exception as e:
            results.append({"error": f"Failed to fetch from CrossRef: {str(e)}"})
            
        return CrossrefSearchOutput(results=results)
