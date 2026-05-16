from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Passenger register request DTO
class RegisterPassengerRequest(BaseModel):

    # User telefon raqami
    phone: str = Field(min_length=5, max_length=32)

    # User emaili
    email: EmailStr | None = None

    # User paroli
    password: str = Field(min_length=6, max_length=128)

    # User to'liq ismi
    full_name: str | None = Field(default=None, max_length=255)


# Driver register request DTO
class RegisterDriverRequest(BaseModel):

    # Driver telefon raqami
    phone: str = Field(min_length=5, max_length=32)

    # Driver emaili
    email: EmailStr | None = None

    # Driver paroli
    password: str = Field(min_length=6, max_length=128)

    # Driver to'liq ismi
    full_name: str | None = Field(default=None, max_length=255)

    # Haydovchilik guvohnomasi raqami
    license_number: str = Field(min_length=1, max_length=64)


# Admin yaratish request DTO
class CreateAdminRequest(BaseModel):

    # Admin telefon raqami
    phone: str = Field(min_length=5, max_length=32)

    # Admin emaili
    email: EmailStr | None = None

    # Admin paroli
    password: str = Field(min_length=6, max_length=128)

    # Admin to'liq ismi
    full_name: str | None = Field(default=None, max_length=255)

    # Admin leveli
    admin_level: str = Field(min_length=1, max_length=32)


# Login request DTO
class LoginRequest(BaseModel):

    # Login uchun telefon
    phone: str

    # Login uchun parol
    password: str


# Current user update request DTO
class UpdateMeRequest(BaseModel):

    # Yangi email
    email: EmailStr | None = None

    # Yangi full name
    full_name: str | None = Field(default=None, max_length=255)


# Admin user update request DTO
class AdminUpdateUserRequest(BaseModel):

    # User telefon raqami
    phone: str | None = Field(default=None, min_length=5, max_length=32)

    # User emaili
    email: EmailStr | None = None

    # User to'liq ismi
    full_name: str | None = Field(default=None, max_length=255)

    # User active statusi
    is_active: bool | None = None


# Wallet response DTO
class WalletResponse(BaseModel):

    # Wallet balance
    balance: Decimal

    # Wallet currency
    currency: str


# Oddiy user response DTO
class UserResponse(BaseModel):

    # User ID
    id: UUID

    # User roli
    role: str

    # User telefon raqami
    phone: str

    # User emaili
    email: EmailStr | None

    # User full name
    full_name: str | None

    # User active holati
    is_active: bool

    # User yaratilgan vaqti
    created_at: datetime

    # User wallet ma'lumoti
    wallet: WalletResponse | None = None


# Driver response DTO
class DriverResponse(UserResponse):

    # Driver license raqami
    license_number: str

    # Driver verification statusi
    is_verified: bool


# Admin response DTO
class AdminResponse(UserResponse):

    # Admin leveli
    admin_level: str


# JWT token response DTO
class TokenResponse(BaseModel):

    # Access token
    access_token: str

    # Token type
    token_type: str = "bearer"

# Admin wallet balance update request DTO
class AdminWalletAdjustRequest(BaseModel):

    # Miqdor
    amount: Decimal = Field(gt=0)

    # Operation: increase yoki decrease
    operation: str = Field(pattern="^(increase|decrease)$")

    # Sabab / izoh
    description: str | None = Field(default=None, max_length=500)


# Admin wallet balance update response DTO
class AdminWalletAdjustResponse(BaseModel):

    # Wallet ID
    wallet_id: UUID

    # User ID
    user_id: UUID

    # Oldingi balance
    balance_before: Decimal

    # Yangi balance
    balance_after: Decimal

    # Currency
    currency: str

    # Transaction type
    transaction_type: str

    # Izoh
    description: str | None