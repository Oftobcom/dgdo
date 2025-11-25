from pydantic import BaseModel
from uuid import UUID

class Trip(BaseModel):
    id: UUID
    passenger_id: UUID
    driver_id: UUID | None
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    status: str
