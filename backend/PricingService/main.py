from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from uuid import UUID
import math

app = FastAPI(title="DG Do — Eng Sodda Pricing Service")

# 1. Tariflar ro'yxati
class RideType(str, Enum):
    ECONOMY = "ECONOMY"
    COMFORT = "COMFORT"
    XL = "XL"
    DELIVERY = "DELIVERY"

# 2. Barcha tarif parametrlari (Hujjat bo'yicha)
TARIFLAR = {
    "ECONOMY": {"base_fee": 5.0, "per_km": 2.5, "per_min": 0.5, "min_fare": 10.0},
    "COMFORT": {"base_fee": 8.0, "per_km": 3.5, "per_min": 0.7, "min_fare": 15.0},
    "XL": {"base_fee": 10.0, "per_km": 4.0, "per_min": 0.8, "min_fare": 20.0},
    "DELIVERY": {"base_fee": 6.0, "per_km": 2.0, "per_min": 0.4, "min_fare": 8.0}
}

# 3. POST so'rovi uchun kiritiladigan ma'lumotlar formati (Siz so'ragandek)
class QuoteRequest(BaseModel):
    passenger_id: UUID
    ride_type: RideType
    estimated_distance_km: float
    estimated_time_min: float

# --- 1-ENDPOINT (GET): HAMMA TARIFLARNI OLISH ---
@app.get("/tariffs")
def get_all_tariffs():
    """Tizimdagi barcha tariflarning asosiy narxlari va minimal narxlarini ko'rish"""
    natija = {}
    for tarif_nomi, parametrlar in TARIFLAR.items():
        natija[tarif_nomi] = {
            "base_fare": parametrlar["base_fee"],
            "minimum_fare": parametrlar["min_fare"],
            "currency": "TJS"
        }
    return natija

# --- 2-ENDPOINT (POST): NARXNI HISOBLASH ---
@app.post("/calculate")
def calculate_fare(request: QuoteRequest):
    """Kiritilgan tarif, masofa va vaqt bo'yicha yakuniy narxni hisoblash"""
    # Tanlangan tarif parametrlarini olamiz
    tarif = TARIFLAR.get(request.ride_type.value)
    
    # 1. Asosiy narxni hisoblash formulasi: base_fee + (km * per_km) + (min * per_min)
    hisoblangan_narx = (
        tarif["base_fee"] + 
        (request.estimated_distance_km * tarif["per_km"]) + 
        (request.estimated_time_min * tarif["per_min"])
    )
    
    # 2. Minimal narx qoidasi: Agar narx minimal faredan kam bo'lsa, minimal fare olinadi
    yakuniy_narx = max(hisoblangan_narx, tarif["min_fare"])
    
    # 3. Hujjat bo'yicha qoida: All fares rounded up to nearest 0.5 TJS (0.5 gacha yuqoriga yaxlitlash)
    # Masalan: 54.9 bo'lsa -> 55.0 qiladi
    yaxlitlangan_narx = math.ceil(yakuniy_narx * 2) / 2
    
    return {
        "passenger_id": request.passenger_id,
        "ride_type": request.ride_type,
        "estimated_distance_km": request.estimated_distance_km,
        "estimated_time_min": request.estimated_time_min,
        "final_price": yaxlitlangan_narx,
        "currency": "TJS"
    }