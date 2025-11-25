from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Trip(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    passenger_id: UUID
    driver_id: UUID | None = None
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    status: str = "requested"