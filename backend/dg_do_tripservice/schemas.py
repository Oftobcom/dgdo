from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class LocationSchema(BaseModel):
    longitude: float
    latitude: float

class TripCreate(BaseModel):
    passenger_id: UUID
    pickup_location: LocationSchema
    dropoff_location: LocationSchema
    distance: float
    estimated_fare: Decimal

class TripResponse(BaseModel):
    id: UUID
    passenger_id: UUID
    driver_id: Optional[UUID] = None
    status: str
    distance: Optional[float] = None  # <-- Optional ga o'zgartirildi
    estimated_fare: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    trip_id: UUID
    amount: Decimal
    currency: str = "TJS"
    payment_method: Optional[str] = "cash"
    status: Optional[str] = "success"

class PaymentResponse(BaseModel):
    id: UUID
    trip_id: UUID
    amount: Decimal
    currency: str
    status: str

    class Config:
        from_attributes = True

class TripUpdate(BaseModel):
    distance: Optional[float] = None
    estimated_fare: Optional[Decimal] = None
    status: Optional[str] = None
    driver_id: Optional[UUID] = None