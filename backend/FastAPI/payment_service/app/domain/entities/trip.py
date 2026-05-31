import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.enums.trip_status import TripStatus


# PostgreSQL trip_status ENUM type
trip_status_enum = ENUM(
    TripStatus,
    name="trip_status",
    create_type=False,
)


# Trips table modeli
class Trip(Base):
    __tablename__ = "trips"

    # Trip unique ID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    # Passenger ID
    passenger_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Driver ID
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Trip statusi
    status: Mapped[TripStatus] = mapped_column(
        trip_status_enum,
        nullable=False,
    )

    # Taxminiy trip narxi
    estimated_fare: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    # Yakuniy trip narxi
    final_fare: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    # Trip request qilingan vaqt
    requested_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    # Driver accept qilgan vaqt
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Trip tugagan vaqt
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Trip cancel qilingan vaqt
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )