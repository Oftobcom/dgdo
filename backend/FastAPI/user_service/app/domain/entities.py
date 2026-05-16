from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.domain.enums import UserRole


# Asosiy user entity
@dataclass
class UserEntity:

    # User unique ID
    id: UUID

    # User roli
    role: UserRole

    # User telefon raqami
    phone: str

    # User emaili
    email: str | None

    # Hash qilingan password
    password_hash: str

    # User active statusi
    is_active: bool

    # User yaratilgan vaqt
    created_at: datetime

    # User update qilingan vaqt
    updated_at: datetime | None


# Passenger entity
@dataclass
class PassengerEntity:

    # Bog'langan user ID
    user_id: UUID

    # Passenger full name
    full_name: str | None

    # Passenger rating
    rating: float | None

    # Passenger yaratilgan vaqt
    created_at: datetime


# Driver entity
@dataclass
class DriverEntity:

    # Bog'langan user ID
    user_id: UUID

    # Driver full name
    full_name: str | None

    # Driver license raqami
    license_number: str

    # Driver verify statusi
    is_verified: bool

    # Driver rating
    rating: float | None

    # Driver yaratilgan vaqt
    created_at: datetime


# Admin entity
@dataclass
class AdminEntity:

    # Bog'langan user ID
    user_id: UUID

    # Admin full name
    full_name: str | None

    # Admin leveli
    admin_level: str

    # Admin yaratilgan vaqt
    created_at: datetime

# Wallet entity
@dataclass
class WalletEntity:

    # Wallet unique ID
    id: UUID

    # Bog'langan user ID
    user_id: UUID

    # Wallet owner type
    owner_type: str

    # Wallet balance
    balance: Decimal

    # Wallet currency
    currency: str

    # Wallet active statusi
    is_active: bool

    # Wallet yaratilgan vaqt
    created_at: datetime

    # Wallet update qilingan vaqt
    updated_at: datetime | None