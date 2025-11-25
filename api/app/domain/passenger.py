from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Passenger(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    phone: str