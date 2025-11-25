from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..domain.driver import Driver

router = APIRouter(prefix="/drivers", tags=["drivers"])

_drivers = {}

@router.post("/register", response_model=Driver)
def register_driver(d: Driver):
    _drivers[str(d.id)] = d
    return d

@router.post("/location")
def update_location(payload: dict):
    # payload must contain id, lat, lon, status
    did = str(payload.get("id"))
    if did not in _drivers:
        return {"error": "driver not registered"}
    d = _drivers[did]
    d.lat = payload.get("lat", d.lat)
    d.lon = payload.get("lon", d.lon)
    d.status = payload.get("status", d.status)
    return {"ok": True}