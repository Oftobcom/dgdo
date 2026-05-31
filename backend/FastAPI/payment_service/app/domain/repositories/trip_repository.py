from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.trip import Trip


# TripRepository abstract interface
class TripRepository(ABC):

    # Tripni ID orqali olish
    @abstractmethod
    def get_by_id(self, trip_id: UUID) -> Trip | None:
        pass