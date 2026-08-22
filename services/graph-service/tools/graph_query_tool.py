from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext
from services.graph_service.cypher.query_builder import CypherBuilder
from services.graph_service.infrastructure.neo4j_driver import Neo4jDriver

class GraphQueryInput(BaseModel):
    query_type: str = Field(description="'recommendation', 'shortest_path', or 'similarity'")
    parameters: Dict[str, Any] = Field(description="Parameters required for the query type")

class GraphQueryOutput(BaseModel):
    results: list[Dict[str, Any]]

class GraphQueryTool(BaseTool):
    """
    Connects the AI Core to the Neo4j Knowledge Graph.
    Safely executes Cypher queries based on AI agent intent.
    """
    name = "graph_query"
    description = "Queries the Neo4j Knowledge Graph for recommendations and relationships."
    tags = ["graph", "neo4j", "cypher"]
    input_schema = GraphQueryInput
    output_schema = GraphQueryOutput

    def __init__(self, db_driver: Neo4jDriver = None):
        self.driver = db_driver or Neo4jDriver()

    async def execute(self, inputs: GraphQueryInput, context: ToolContext) -> GraphQueryOutput:
        query = ""
        if inputs.query_type == "recommendation":
            query = CypherBuilder.build_technology_recommendation(inputs.parameters.get("patent_id"))
        elif inputs.query_type == "shortest_path":
            query = CypherBuilder.build_shortest_path(inputs.parameters.get("start"), inputs.parameters.get("end"))
            
        results = await self.driver.execute_read(query)
        return GraphQueryOutput(results=results)
