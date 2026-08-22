class CypherBuilder:
    """
    Constructs robust Cypher queries for the AI agents to execute.
    """
    @staticmethod
    def build_similarity_search(source_label: str, target_label: str, limit: int = 5) -> str:
        return f"""
        MATCH (s:{source_label})-[r:SIMILAR_TO]-(t:{target_label})
        RETURN s, r, t
        ORDER BY r.score DESC
        LIMIT {limit}
        """

    @staticmethod
    def build_technology_recommendation(patent_id: str) -> str:
        return f"""
        MATCH (p:Patent {{id: '{patent_id}'}})-[:USES]->(t:Technology)<-[:USES]-(rp:ResearchPaper)
        RETURN t.name as Technology, count(rp) as PaperCount
        ORDER BY PaperCount DESC
        LIMIT 10
        """
        
    @staticmethod
    def build_shortest_path(start_id: str, end_id: str) -> str:
        return f"""
        MATCH p=shortestPath((a {{id: '{start_id}'}})-[*]-(b {{id: '{end_id}'}}))
        RETURN p
        """
