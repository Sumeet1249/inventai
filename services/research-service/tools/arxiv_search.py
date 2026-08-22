import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext

class ArxivSearchInput(BaseModel):
    query: str = Field(description="The semantic question or search query for arXiv.")
    top_k: int = Field(default=5, description="Number of papers to retrieve.")

class ArxivSearchOutput(BaseModel):
    results: list[Dict[str, Any]]

class ArxivSearchTool(BaseTool):
    name = "arxiv_search"
    description = "Searches the arXiv database for scientific and academic research papers."
    tags = ["search", "rag", "research", "arxiv"]
    input_schema = ArxivSearchInput
    output_schema = ArxivSearchOutput

    async def execute(self, inputs: ArxivSearchInput, context: ToolContext) -> ArxivSearchOutput:
        # Construct the arXiv API URL
        base_url = 'http://export.arxiv.org/api/query?'
        search_query = urllib.parse.quote(f'all:{inputs.query}')
        url = f'{base_url}search_query={search_query}&start=0&max_results={inputs.top_k}'
        
        results = []
        try:
            with urllib.request.urlopen(url) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                # The arXiv namespace is usually 'http://www.w3.org/2005/Atom'
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns).text.strip()
                    summary_node = entry.find('atom:summary', ns)
                    summary = summary_node.text.strip() if summary_node is not None else ""
                    id_node = entry.find('atom:id', ns)
                    link = id_node.text.strip() if id_node is not None else ""
                    
                    results.append({
                        "title": title,
                        "text": summary,  # map summary to 'text' so the workflow can easily extract chunks
                        "source": link,
                        "authors": [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns) if author.find('atom:name', ns) is not None]
                    })
        except Exception as e:
            # Handle API errors gracefully
            results.append({"error": f"Failed to fetch from arXiv: {str(e)}"})
            
        return ArxivSearchOutput(results=results)
