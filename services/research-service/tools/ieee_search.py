import urllib.request
import urllib.parse
import json
import os
from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext

class IeeeSearchInput(BaseModel):
    query: str = Field(description="The search query for IEEE Xplore.")
    top_k: int = Field(default=2, description="Number of papers to retrieve.")

class IeeeSearchOutput(BaseModel):
    results: list[Dict[str, Any]]

class IeeeSearchTool(BaseTool):
    name = "ieee_search"
    description = "Searches the IEEE Xplore database for engineering and technology papers."
    tags = ["search", "rag", "research", "ieee", "engineering"]
    input_schema = IeeeSearchInput
    output_schema = IeeeSearchOutput

    async def execute(self, inputs: IeeeSearchInput, context: ToolContext) -> IeeeSearchOutput:
        api_key = os.getenv("IEEE_API_KEY")
        results = []
        
        if not api_key:
            # Graceful Fallback if no API key is provided
            print("IEEE_API_KEY missing. Using Demo IEEE fallback...")
            results.append({
                "title": f"[Demo IEEE] Recent Advances related to {inputs.query}",
                "text": "This is a demo abstract from IEEE. To get real data, configure IEEE_API_KEY.",
                "source": "https://ieeexplore.ieee.org/",
                "authors": "IEEE Demo Author"
            })
            return IeeeSearchOutput(results=results)

        base_url = 'http://ieeexploreapi.ieee.org/api/v1/search/articles?'
        search_query = urllib.parse.quote(inputs.query)
        url = f'{base_url}apikey={api_key}&format=json&max_records={inputs.top_k}&start_record=1&sort_order=asc&sort_field=article_number&article_title={search_query}'
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                result_list = data.get('articles', [])
                for entry in result_list:
                    title = entry.get('title', '')
                    abstract = entry.get('abstract', '')
                    text = abstract if abstract else title
                    link = entry.get('pdf_url', '')
                    
                    authors = []
                    if 'authors' in entry and 'authors' in entry['authors']:
                        for a in entry['authors']['authors']:
                            authors.append(a.get('full_name', ''))
                            
                    results.append({
                        "title": title,
                        "text": text,
                        "source": link,
                        "authors": ", ".join(authors)
                    })
        except Exception as e:
            results.append({"error": f"Failed to fetch from IEEE Xplore: {str(e)}"})
            
        return IeeeSearchOutput(results=results)
