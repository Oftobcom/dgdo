import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric
from sqlalchemy.dialects.postgresql import ENUM, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.enums.wallet_owner_type import WalletOwnerType


# PostgreSQL wallet_owner_type ENUM type
wallet_owner_type_enum = ENUM(
    WalletOwnerType,
    name="wallet_owner_type",
    create_type=False,
)


# Wallets table modeli
class Wallet(Base):
    __tablename__ = "wallets"

    # Wallet unique ID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    # User ID
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
    )

    # Wallet owner type
    owner_type: Mapped[WalletOwnerType] = mapped_column(
        wallet_owner_type_enum,
        nullable=False,
    )

    # Wallet balance
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Wallet currency
    currency: Mapped[str] = mapped_column(
        VARCHAR(8),
        nullable=False,
    )

    # Wallet active statusi
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
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