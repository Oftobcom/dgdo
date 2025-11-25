from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Driver(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    lat: float
    lon: float
    status: str = "available"  # available | busy