from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


# SQLAlchemy user repository implementatsiyasi
class SqlAlchemyUserRepository(UserRepository):

    # Constructor
    def __init__(self, db: Session) -> None:
        self.db = db

    # Userni ID orqali olish
    def get_by_id(self, user_id: UUID) -> User | None:

        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )