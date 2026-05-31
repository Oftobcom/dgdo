import enum
from sqlalchemy import Column, String, DateTime, Numeric, text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
from sqlalchemy import Column, String, Boolean, DateTime # <-- Bular import qilinganiga ishonch hosil qiling

class TripStatus(str, enum.Enum):
    requested = "requested"
    accepted = "accepted"
    arrived = "arrived"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    passenger_id = Column(UUID(as_uuid=True), nullable=False)
    driver_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(32), nullable=False, default="requested", server_default="requested")
    
    pickup_location = Column(String(255), nullable=False)
    dropoff_location = Column(String(255), nullable=False)
    
    distance = Column(Numeric(10, 2), nullable=False)
    
    estimated_fare = Column(Numeric(10, 2), nullable=False)
    final_fare = Column(Numeric(10, 2))
    
    requested_at = Column(DateTime, server_default=text("now()"))
    accepted_at = Column(DateTime)
    arrived_at = Column(DateTime, nullable=True)  # arrived_at maydoni aniqlandi
    completed_at = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)

class DriverStatus(Base):
    __tablename__ = "driver_status"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    driver_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    status = Column(String(32), server_default="offline")
    current_location = Column(String(255), nullable=False)
    updated_at = Column(DateTime, server_default=text("now()"), onupdate=text("now()"))

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    trip_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), server_default="TJS")
    # nullable=True ga o'zgartirildi
    payment_method = Column(String(32), nullable=True, server_default="cash")
    status = Column(String(32), server_default="success")
    created_at = Column(DateTime, server_default=text("now()"))