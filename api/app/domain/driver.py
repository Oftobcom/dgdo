from pydantic import BaseModel
from uuid import UUID

class Driver(BaseModel):
    id: UUID
    lat: float
    lon: float
    status: str  # available | busy
