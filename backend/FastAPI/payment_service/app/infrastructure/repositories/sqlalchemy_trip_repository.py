from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.trip import Trip
from app.domain.repositories.trip_repository import TripRepository


# SQLAlchemy trip repository implementatsiyasi
class SqlAlchemyTripRepository(TripRepository):

    # Constructor
    def __init__(self, db: Session) -> None:
        self.db = db

    # Tripni ID orqali olish
    def get_by_id(self, trip_id: UUID) -> Trip | None:

        return (
            self.db.query(Trip)
            .filter(Trip.id == trip_id)
            .first()
        )