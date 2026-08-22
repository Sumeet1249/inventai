from sqlalchemy.orm import Session
from app.models import User, Session as UserSession
from .base_repo import BaseRepository
from typing import Optional

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

class SessionRepository(BaseRepository[UserSession]):
    def __init__(self):
        super().__init__(UserSession)

    def get_by_refresh_token(self, db: Session, refresh_token: str) -> Optional[UserSession]:
        return db.query(UserSession).filter(UserSession.refresh_token == refresh_token).first()

user_repo = UserRepository()
session_repo = SessionRepository()
