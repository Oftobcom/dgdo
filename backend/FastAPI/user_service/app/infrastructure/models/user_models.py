import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import UserRole, WalletOwnerType
from app.infrastructure.database import Base


# PostgreSQL user_role ENUM type
user_role_enum = ENUM(
    UserRole,
    name="user_role",
    create_type=False,
)


# PostgreSQL wallet_owner_type ENUM type
wallet_owner_type_enum = ENUM(
    WalletOwnerType,
    name="wallet_owner_type",
    create_type=False,
)


# Users table modeli
class UserModel(Base):
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
        default=True,
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

    # Passenger relation
    passenger: Mapped["PassengerModel | None"] = relationship(
        "PassengerModel",
        back_populates="user",
        uselist=False,
    )

    # Driver relation
    driver: Mapped["DriverModel | None"] = relationship(
        "DriverModel",
        back_populates="user",
        uselist=False,
    )

    # Admin relation
    admin: Mapped["AdminModel | None"] = relationship(
        "AdminModel",
        back_populates="user",
        uselist=False,
    )

    # Wallet relation
    wallet: Mapped["WalletModel | None"] = relationship(
        "WalletModel",
        back_populates="user",
        uselist=False,
    )


# Passengers table modeli
class PassengerModel(Base):
    __tablename__ = "passengers"

    # User foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Passenger full name
    full_name: Mapped[str | None] = mapped_column(
        VARCHAR(255),
        nullable=True,
    )

    # Passenger rating
    rating: Mapped[float | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        default=5.0,
    )

    # Passenger yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    # User relationship
    user: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="passenger",
    )


# Drivers table modeli
class DriverModel(Base):
    __tablename__ = "drivers"

    # User foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Driver full name
    full_name: Mapped[str | None] = mapped_column(
        VARCHAR(255),
        nullable=True,
    )

    # Driver license raqami
    license_number: Mapped[str] = mapped_column(
        VARCHAR(64),
        nullable=False,
        unique=True,
    )

    # Driver verify statusi
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Driver rating
    rating: Mapped[float | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        default=5.0,
    )

    # Driver yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    # User relationship
    user: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="driver",
    )


# Admins table modeli
class AdminModel(Base):
    __tablename__ = "admins"

    # User foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Admin full name
    full_name: Mapped[str | None] = mapped_column(
        VARCHAR(255),
        nullable=True,
    )

    # Admin level
    admin_level: Mapped[str] = mapped_column(
        VARCHAR(32),
        nullable=False,
    )

    # Admin yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    # User relationship
    user: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="admin",
    )


# Wallets table modeli
class WalletModel(Base):
    __tablename__ = "wallets"

    # Wallet unique ID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    # User foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Wallet owner type
    owner_type: Mapped[WalletOwnerType] = mapped_column(
        wallet_owner_type_enum,
        nullable=False,
    )

    # Wallet balance
    balance: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    # Wallet currency
    currency: Mapped[str] = mapped_column(
        VARCHAR(8),
        nullable=False,
        default="TJS",
    )

    # Wallet active statusi
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Wallet yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    # Wallet update qilingan vaqt
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # User relationship
    user: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="wallet",
    )