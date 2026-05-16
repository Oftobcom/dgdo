from pydantic import BaseModel, Field
from enum import Enum
from decimal import Decimal
from uuid import UUID

# 1. Tariflar ro'yxati (Enum)
class RideType(str, Enum):
    ECONOMY = "ECONOMY"
    COMFORT = "COMFORT"
    XL = "XL"
    DELIVERY = "DELIVERY"

# 2. Narxni hisoblash uchun so'rov (Siz so'ragan format, final_fare'siz)
class SingleTariffQuoteRequest(BaseModel):
    passenger_id: UUID
    ride_type: RideType = Field(..., description="Hisoblanishi kerak bo'lgan tarif (ECONOMY, COMFORT va h.k.)")
    estimated_distance_km: float = Field(..., gt=0, description="Masofa km da")
    estimated_time_min: float = Field(..., gt=0, description="Vaqt daqiqada")
    demand_supply_ratio: float = Field(1.0, description="Koeffitsiyent (Surge) uchun, sukut bo'yicha 1.0")

# 3. Serverdan qaytadigan hisoblangan narx javobi
class SingleTariffQuoteResponse(BaseModel):
    passenger_id: UUID
    ride_type: RideType
    estimated_distance_km: float
    estimated_time_min: float
    base_fare: Decimal = Field(..., description="Asosiy tarif narxi (surge'siz)")
    surge_multiplier: Decimal = Field(..., description="Qo'llanilgan surge koeffitsiyenti")
    final_fare: Decimal = Field(..., description="Siz to'laydigan yakuniy narx")
    currency: str