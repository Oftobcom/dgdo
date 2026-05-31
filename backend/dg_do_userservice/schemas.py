from pydantic import BaseModel, Field
from pydantic import BaseModel, EmailStr
from pydantic.networks import EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime
from models import UserRole

class UserBase(BaseModel):
    phone: str = Field(..., max_length=32)
    email: Optional[EmailStr] = None
    role: UserRole

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., max_length=255)

class UserResponse(BaseModel):
    id: UUID
    role: str
    phone: str
    email: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    full_name: Optional[str] = None