from services.graph_service.infrastructure.neo4j_driver import Neo4jDriver
from services.graph_service.models.schema import NodeBase, EdgeBase
import logging

logger = logging.getLogger(__name__)

class Neo4jRepository:
    def __init__(self, driver: Neo4jDriver):
        self.neo4j = driver

    async def merge_node(self, node: NodeBase):
        """Merges a node into the graph using its ID."""
        props = node.model_dump(exclude={"label"})
        
        # Build property assignments dynamically
        set_clause = ", ".join([f"n.{k} = ${k}" for k in props.keys()])
        
        query = f"""
        MERGE (n:{node.label} {{id: $id}})
        SET {set_clause}
        RETURN n
        """
        
        return await self.neo4j.execute_write(query, props)

    async def merge_edge(self, edge: EdgeBase, source_label: str = "Node", target_label: str = "Node"):
        """Merges a relationship between two nodes."""
        props = edge.model_dump(exclude={"source_id", "target_id", "type"})
        
        query = f"""
        MATCH (a:{source_label} {{id: $source_id}})
        MATCH (b:{target_label} {{id: $target_id}})
        MERGE (a)-[r:{edge.type}]->(b)
        """
        if props and props.get("properties"):
            set_clause = ", ".join([f"r.{k} = $properties.{k}" for k in props.get("properties").keys()])
            if set_clause:
                 query += f" SET {set_clause}"
        query += " RETURN r"
        
        params = {
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "properties": edge.properties
        }
        
        return await self.neo4j.execute_write(query, params)
