import os
import asyncio
from neo4j import AsyncGraphDatabase
import logging

logger = logging.getLogger(__name__)

class Neo4jDriver:
    """
    Handles connection pooling and transaction execution against the Neo4j database.
    """
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        
        try:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Exception as e:
            logger.error(f"Failed to create Neo4j driver: {e}")
            self.driver = None

    async def init_db(self):
        """Creates indexes and constraints."""
        if not self.driver:
            return
            
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Patent) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:ResearchPaper) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Technology) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Inventor) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Organization) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Project) REQUIRE n.id IS UNIQUE"
        ]
        
        for q in queries:
            await self.execute_write(q)

    async def execute_read(self, query: str, parameters: dict = None) -> list:
        """Executes a Cypher read transaction."""
        if not self.driver:
            logger.warning("Neo4j driver not initialized. Returning empty mock data.")
            return []
            
        parameters = parameters or {}
        try:
            async with self.driver.session() as session:
                result = await session.run(query, parameters)
                records = await result.data()
                return records
        except Exception as e:
            logger.error(f"Error executing Cypher read: {e}")
            return []

    async def execute_write(self, query: str, parameters: dict = None) -> list:
        """Executes a Cypher write transaction."""
        if not self.driver:
            logger.warning("Neo4j driver not initialized.")
            return []
            
        parameters = parameters or {}
        try:
            async with self.driver.session() as session:
                result = await session.run(query, parameters)
                records = await result.data()
                return records
        except Exception as e:
            logger.error(f"Error executing Cypher write: {e}")
            return []

    async def close(self):
        if self.driver:
            await self.driver.close()

