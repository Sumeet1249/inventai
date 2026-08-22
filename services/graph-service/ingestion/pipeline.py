from services.graph_service.repositories.neo4j_repository import Neo4jRepository
from services.graph_service.models.schema import PatentNode, ResearchPaperNode, EdgeBase, TechnologyNode
import logging

logger = logging.getLogger(__name__)

class GraphIngestionPipeline:
    def __init__(self, repo: Neo4jRepository):
        self.repo = repo

    async def ingest_patent_data(self, patent_data: dict):
        """
        Consumes structured patent data (e.g. from Patent Service),
        creates nodes for Patent, Technologies, and establishes edges.
        """
        patent_id = patent_data.get("id", "unknown_patent")
        
        # Create Patent Node
        patent = PatentNode(
            id=patent_id,
            title=patent_data.get("title", "Untitled Patent"),
            assignee=patent_data.get("assignee"),
            date=patent_data.get("date")
        )
        await self.repo.merge_node(patent)
        
        # Ingest Technologies mentioned in the patent
        technologies = patent_data.get("technologies", [])
        for tech in technologies:
            tech_id = f"tech_{tech.replace(' ', '_').lower()}"
            tech_node = TechnologyNode(
                id=tech_id,
                name=tech,
                domain=patent_data.get("domain", "General")
            )
            await self.repo.merge_node(tech_node)
            
            # Create Edge: (Patent)-[:USES]->(Technology)
            uses_edge = EdgeBase(
                source_id=patent_id,
                target_id=tech_id,
                type="USES",
                properties={"weight": 1.0}
            )
            await self.repo.merge_edge(uses_edge, source_label="Patent", target_label="Technology")
            
        logger.info(f"Ingested patent {patent_id} and related technologies.")

    async def ingest_research_data(self, research_data: dict):
        """
        Consumes structured research data, creates ResearchPaper nodes and citations.
        """
        paper_id = research_data.get("id", "unknown_paper")
        
        paper = ResearchPaperNode(
            id=paper_id,
            title=research_data.get("title", "Untitled Paper"),
            authors=research_data.get("authors", []),
            year=research_data.get("year"),
            abstract=research_data.get("abstract")
        )
        await self.repo.merge_node(paper)
        
        citations = research_data.get("citations", [])
        for cited_id in citations:
            # We assume the cited paper will also be created, or we can just merge a stub.
            # In a real system, we'd queue the cited paper for full ingestion.
            cited_stub = ResearchPaperNode(id=cited_id, title="Unknown Title")
            await self.repo.merge_node(cited_stub)
            
            cites_edge = EdgeBase(
                source_id=paper_id,
                target_id=cited_id,
                type="CITES",
                properties={"verified": True}
            )
            await self.repo.merge_edge(cites_edge, source_label="ResearchPaper", target_label="ResearchPaper")

        logger.info(f"Ingested research paper {paper_id} and citations.")
