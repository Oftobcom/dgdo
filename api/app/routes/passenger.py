from fastapi import APIRouter, HTTPException
from ..domain.passenger import Passenger

router = APIRouter(prefix="/passengers", tags=["passengers"])

# In-memory store for MVP
_passengers = {}

@router.post("/register", response_model=Passenger)
def register_passenger(p: Passenger):
    _passengers[str(p.id)] = p
    return p

@router.get("/{passenger_id}", response_model=Passenger)
def get_passenger(passenger_id: str):
    p = _passengers.get(passenger_id)
    if not p:
        raise HTTPException(status_code=404, detail="Passenger not found")
    return p