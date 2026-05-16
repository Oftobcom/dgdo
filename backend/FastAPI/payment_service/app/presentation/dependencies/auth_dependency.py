from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.domain.enums.user_role import UserRole
from app.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository


# Bearer token scheme
bearer_scheme = HTTPBearer()


# Token orqali current userni olish
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    # Bearer tokenni olamiz
    token = credentials.credentials

    try:
        # Tokenni decode qilamiz
        payload = decode_access_token(token)

        # Tokendan user ID ni olamiz
        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Missing sub")

        # User ID ni UUID ga aylantiramiz
        parsed_user_id = UUID(user_id)

    except Exception:
        # Token noto'g'ri bo'lsa
        raise HTTPException(status_code=401, detail="Invalid token")

    # User repository yaratamiz
    user_repository = SqlAlchemyUserRepository(db)

    # Userni DBdan topamiz
    user = user_repository.get_by_id(parsed_user_id)

    if not user:
        # User topilmasa
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        # User inactive bo'lsa
        raise HTTPException(status_code=403, detail="User is inactive")

    return user


# Faqat admin access uchun dependency
def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user