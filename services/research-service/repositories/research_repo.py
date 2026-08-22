from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from services.research_service.domain.models import ResearchPaper, Author
from services.research_service.schemas.research_schemas import ResearchPaperCreate
from typing import List, Optional

class ResearchRepository:
    """Repository pattern for abstracting database logic for research papers."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, paper_in: ResearchPaperCreate) -> ResearchPaper:
        db_paper = ResearchPaper(
            title=paper_in.title,
            abstract=paper_in.abstract,
            url=paper_in.url,
            published_date=paper_in.published_date
        )
        
        for auth in paper_in.authors:
            db_author = Author(name=auth.name, affiliation=auth.affiliation)
            db_paper.authors.append(db_author)
            
        self.session.add(db_paper)
        await self.session.commit()
        await self.session.refresh(db_paper)
        return db_paper

    async def get_by_id(self, paper_id: str) -> Optional[ResearchPaper]:
        stmt = select(ResearchPaper).options(selectinload(ResearchPaper.authors)).where(ResearchPaper.id == paper_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 10, offset: int = 0) -> List[ResearchPaper]:
        stmt = select(ResearchPaper).options(selectinload(ResearchPaper.authors)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
