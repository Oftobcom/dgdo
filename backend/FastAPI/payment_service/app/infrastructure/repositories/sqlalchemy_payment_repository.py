from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.entities.payment import Payment
from app.domain.entities.trip import Trip
from app.domain.enums.payment_status import PaymentStatus
from app.domain.repositories.payment_repository import PaymentRepository


# SQLAlchemy payment repository implementatsiyasi
class SqlAlchemyPaymentRepository(PaymentRepository):

    # Constructor
    def __init__(self, db: Session) -> None:
        self.db = db

    # Payment yaratish
    def create(self, payment: Payment) -> Payment:

        self.db.add(payment)

        # DB ga flush qilamiz
        self.db.flush()

        # Payment objectni refresh qilamiz
        self.db.refresh(payment)

        return payment

    # Paymentni ID orqali olish
    def get_by_id(self, payment_id: UUID) -> Payment | None:

        return (
            self.db.query(Payment)
            .filter(Payment.id == payment_id)
            .first()
        )

    # Paymentni trip ID orqali olish
    def get_by_trip_id(self, trip_id: UUID) -> Payment | None:

        return (
            self.db.query(Payment)
            .filter(Payment.trip_id == trip_id)
            .first()
        )

    # Barcha paymentlarni olish
    def get_all(self) -> list[Payment]:

        return (
            self.db.query(Payment)
            .order_by(Payment.created_at.desc())
            .all()
        )

    # User triplariga tegishli paymentlarni olish
    def get_by_user_trips(self, user_id: UUID, role: str) -> list[Payment]:

        # Payment va Trip join qilamiz
        query = self.db.query(Payment).join(
            Trip,
            Trip.id == Payment.trip_id,
        )

        # Passenger paymentlari
        if role == "passenger":
            query = query.filter(Trip.passenger_id == user_id)

        # Driver paymentlari
        if role == "driver":
            query = query.filter(Trip.driver_id == user_id)

        return query.order_by(Payment.created_at.desc()).all()

    # Success paymentlar summary olish
    def success_summary(self, date_from: datetime, date_to: datetime) -> tuple:

        return (
            self.db.query(
                # Jami summa
                func.coalesce(func.sum(Payment.amount), 0),

                # Paymentlar soni
                func.count(Payment.id),
            )

            # Faqat success paymentlar
            .filter(Payment.status == PaymentStatus.success)

            # Sana filterlari
            .filter(Payment.created_at >= date_from)
            .filter(Payment.created_at <= date_to)

            .one()
        )

    # Paymentni o'chirish
    def delete(self, payment: Payment) -> None:

        self.db.delete(payment)