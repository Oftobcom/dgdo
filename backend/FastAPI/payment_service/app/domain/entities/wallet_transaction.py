import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.enums.wallet_transaction_status import WalletTransactionStatus
from app.domain.enums.wallet_transaction_type import WalletTransactionType


# PostgreSQL wallet_transaction_type ENUM type
wallet_transaction_type_enum = ENUM(
    WalletTransactionType,
    name="wallet_transaction_type",
    create_type=False,
)


# PostgreSQL wallet_transaction_status ENUM type
wallet_transaction_status_enum = ENUM(
    WalletTransactionStatus,
    name="wallet_transaction_status",
    create_type=False,
)


# Wallet transactions table modeli
class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    # Transaction unique ID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    # Wallet foreign key
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Trip foreign key
    trip_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Transaction turi
    type: Mapped[WalletTransactionType] = mapped_column(
        wallet_transaction_type_enum,
        nullable=False,
    )

    # Transaction statusi
    status: Mapped[WalletTransactionStatus] = mapped_column(
        wallet_transaction_status_enum,
        nullable=False,
    )

    # Transaction summasi
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Transaction currency
    currency: Mapped[str] = mapped_column(
        VARCHAR(8),
        nullable=False,
    )

    # Transactiondan oldingi balance
    balance_before: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Transactiondan keyingi balance
    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # Transaction description
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Transaction yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )