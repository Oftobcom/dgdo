import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.enums.user_role import UserRole


# PostgreSQL user_role ENUM type
user_role_enum = ENUM(
    UserRole,
    name="user_role",
    create_type=False,
)


# Users table modeli
class User(Base):
    __tablename__ = "users"

    # User unique ID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    # User roli
    role: Mapped[UserRole] = mapped_column(
        user_role_enum,
        nullable=False,
    )

    # Telefon raqami
    phone: Mapped[str] = mapped_column(
        VARCHAR(32),
        nullable=False,
        unique=True,
    )

    # Email address
    email: Mapped[str | None] = mapped_column(
        VARCHAR(255),
        nullable=True,
        unique=True,
    )

    # Hash qilingan password
    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # User active statusi
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    # User yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    # User update qilingan vaqt
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )