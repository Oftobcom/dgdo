from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.payment import Payment


# PaymentRepository abstract interface
class PaymentRepository(ABC):

    # Payment yaratish
    @abstractmethod
    def create(self, payment: Payment) -> Payment:
        pass

    # Paymentni ID orqali olish
    @abstractmethod
    def get_by_id(self, payment_id: UUID) -> Payment | None:
        pass

    # Paymentni trip ID orqali olish
    @abstractmethod
    def get_by_trip_id(self, trip_id: UUID) -> Payment | None:
        pass

    # Barcha paymentlarni olish
    @abstractmethod
    def get_all(self) -> list[Payment]:
        pass

    # User triplariga tegishli paymentlarni olish
    @abstractmethod
    def get_by_user_trips(self, user_id: UUID, role: str) -> list[Payment]:
        pass

    # Success paymentlar summary olish
    @abstractmethod
    def success_summary(self, date_from: datetime, date_to: datetime) -> tuple:
        pass

    # Paymentni o'chirish
    @abstractmethod
    def delete(self, payment: Payment) -> None:
        pass