from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from app.schemas import UserCreate, UserLogin, Token
from app.repositories.user_repo import user_repo, session_repo
from app.core.security import get_password_hash, verify_password, generate_refresh_token
from packages.auth.jwt_utils import create_access_token

class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate):
        user = user_repo.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_pwd = get_password_hash(user_in.password)
        new_user = user_repo.create(db, obj_in={"email": user_in.email, "password_hash": hashed_pwd})
        return new_user

    @staticmethod
    def login_user(db: Session, user_in: UserLogin, request: Request) -> Token:
        user = user_repo.get_by_email(db, email=user_in.email)
        if not user or not verify_password(user_in.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create Tokens
        access_token = create_access_token(data={"sub": str(user.id), "role": "USER"})
        refresh_token = generate_refresh_token()
        
        # Save Session
        expires_at = datetime.utcnow() + timedelta(days=7)
        session_repo.create(db, obj_in={
            "user_id": user.id,
            "refresh_token": refresh_token,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "expires_at": expires_at
        })
        
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    @staticmethod
    def refresh_token(db: Session, refresh_token: str) -> Token:
        db_session = session_repo.get_by_refresh_token(db, refresh_token)
        if not db_session or db_session.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
        access_token = create_access_token(data={"sub": str(db_session.user_id), "role": "USER"})
        new_refresh = generate_refresh_token()
        
        # Rotate token
        session_repo.update(db, db_obj=db_session, obj_in={"refresh_token": new_refresh})
        
        return Token(access_token=access_token, refresh_token=new_refresh, token_type="bearer")
