import enum

from sqlalchemy import Column, String
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class UserRole(str, enum.Enum):
    passenger = "passenger"
    driver = "driver"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    role = Column(String, nullable=False)
    phone = Column(String(32), nullable=False, unique=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime)

    passenger_profile = relationship("Passenger", back_populates="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    driver_profile = relationship("Driver", back_populates="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True)

class Passenger(Base):
    __tablename__ = "passengers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    full_name = Column(String(255))
    rating = Column(Numeric(3, 2), server_default=text("5.0"))
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    user = relationship("User", back_populates="passenger_profile")

class Driver(Base):
    __tablename__ = "drivers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    full_name = Column(String(255))
    license_number = Column(String(64), nullable=False, unique=True)
    is_verified = Column(Boolean, nullable=False, server_default=text("false"))
    rating = Column(Numeric(3, 2), server_default=text("5.0"))
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    user = relationship("User", back_populates="driver_profile")