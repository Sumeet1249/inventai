import pytest
from services.graph_service.ingestion.pipeline import GraphIngestionPipeline
from services.graph_service.repositories.neo4j_repository import Neo4jRepository
from services.graph_service.infrastructure.neo4j_driver import Neo4jDriver
from services.graph_service.models.schema import PatentNode, TechnologyNode

class MockNeo4jDriver:
    async def execute_write(self, query, parameters):
        return []
    async def execute_read(self, query, parameters):
        return []

@pytest.mark.asyncio
async def test_patent_ingestion():
    repo = Neo4jRepository(MockNeo4jDriver())
    pipeline = GraphIngestionPipeline(repo)
    
    mock_patent_data = {
        "id": "pat_999",
        "title": "Quantum Drive",
        "assignee": "Stark Industries",
        "technologies": ["Quantum Physics", "Thrusters"]
    }
    
    # Just checking it doesn't crash on standard schema extraction
    await pipeline.ingest_patent_data(mock_patent_data)
    assert True
