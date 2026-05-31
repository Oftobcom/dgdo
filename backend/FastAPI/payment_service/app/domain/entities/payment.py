import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import ENUM, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.enums.payment_status import PaymentStatus


# PostgreSQL payment_status ENUM type
payment_status_enum = ENUM(
    PaymentStatus,
    name="payment_status",
    create_type=False,
)


# Payments table modeli
class Payment(Base):
    __tablename__ = "payments"

    # Payment unique ID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    # Trip foreign key
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Wallet transaction foreign key
    wallet_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wallet_transactions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Payment summasi
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Payment currency
    currency: Mapped[str] = mapped_column(
        VARCHAR(8),
        nullable=False,
    )

    # Payment method
    payment_method: Mapped[str] = mapped_column(
        VARCHAR(32),
        nullable=False,
    )

    # Payment statusi
    status: Mapped[PaymentStatus] = mapped_column(
        payment_status_enum,
        nullable=False,
    )

    # Payment yaratilgan vaqt
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )