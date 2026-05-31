from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.interfaces.user_repository import UserRepository
from app.application.services.user_service import UserService
from app.core.security import decode_access_token
from app.domain.entities import UserEntity
from app.domain.enums import UserRole
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository


# Bearer token scheme yaratamiz
bearer_scheme = HTTPBearer()


# UserRepository dependency
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return SqlAlchemyUserRepository(db)


# UserService dependency
def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository)


# Token orqali current userni olish
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserEntity:
    # Bearer tokenni olamiz
    token = credentials.credentials

    try:
        # Tokenni decode qilamiz
        payload = decode_access_token(token)

        # Tokendan user id ni olamiz
        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Missing subject")

        # User id ni UUID ga aylantiramiz
        parsed_user_id = UUID(user_id)

    except Exception:
        # Token noto'g'ri bo'lsa
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # Userni DBdan topamiz
    user = user_service.user_repository.get_by_id(parsed_user_id)

    if not user:
        # User topilmasa
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        # User inactive bo'lsa
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    return user


# Faqat admin access uchun dependency
def require_admin(
    current_user: UserEntity = Depends(get_current_user),
) -> UserEntity:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user