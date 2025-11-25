from fastapi import APIRouter, HTTPException
from ..domain.trip import Trip
from ..services.matching_service import MatchingService

router = APIRouter(prefix="/trips", tags=["trips"])

_trips = {}

matching = MatchingService()

@router.post("/request", response_model=Trip)
def create_trip(trip: Trip):
    # store
    _trips[str(trip.id)] = trip
    # call matching service (sync HTTP to C++ stub)
    try:
        assigned = matching.assign_driver(trip)
        if assigned:
            trip.driver_id = assigned
            trip.status = "assigned"
    except Exception as e:
        # on error, leave as requested
        print("matching error", e)
    return trip

@router.post("/{id}/status")
def update_status(id: str, payload: dict):
    t = _trips.get(id)
    if not t:
        raise HTTPException(status_code=404, detail="Trip not found")
    status = payload.get("status")
    if status:
        t.status = status
    return {"ok": True, "status": t.status}