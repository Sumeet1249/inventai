from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from services.patent_service.domain.models import Patent, Inventor
from services.patent_service.schemas.patent_schemas import PatentCreate
from typing import List, Optional

class PatentRepository:
    """Repository pattern for abstracting database logic."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, patent_in: PatentCreate) -> Patent:
        db_patent = Patent(
            title=patent_in.title,
            abstract=patent_in.abstract,
            claims=patent_in.claims
        )
        
        for inv in patent_in.inventors:
            db_inventor = Inventor(name=inv.name, company=inv.company)
            db_patent.inventors.append(db_inventor)
            
        self.session.add(db_patent)
        await self.session.commit()
        await self.session.refresh(db_patent)
        return db_patent

    async def get_by_id(self, patent_id: str) -> Optional[Patent]:
        stmt = select(Patent).options(selectinload(Patent.inventors)).where(Patent.id == patent_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 10, offset: int = 0) -> List[Patent]:
        stmt = select(Patent).options(selectinload(Patent.inventors)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
