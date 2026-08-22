from typing import Optional, Dict
from services.innovation_engine.domain.project_models import ProjectState

class InMemoryProjectRepository:
    """
    Tracks overarching Project states.
    In production, this is a PostgreSQL repository.
    """
    def __init__(self):
        self.db: Dict[str, ProjectState] = {}

    async def create(self, project: ProjectState) -> ProjectState:
        self.db[project.id] = project
        return project

    async def update(self, project: ProjectState) -> ProjectState:
        self.db[project.id] = project
        return project

    async def get_by_id(self, project_id: str) -> Optional[ProjectState]:
        return self.db.get(project_id)
