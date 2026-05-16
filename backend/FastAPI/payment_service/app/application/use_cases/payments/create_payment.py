import uuid
from datetime import datetime

from fastapi import HTTPException

from app.domain.entities.payment import Payment
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.user_role import UserRole


# Payment create use case
class CreatePaymentUseCase:

    # Constructor
    def __init__(self, payment_repository, trip_repository, db) -> None:

        # Payment repository
        self.payment_repository = payment_repository

        # Trip repository
        self.trip_repository = trip_repository

        # Database session
        self.db = db

    # Payment yaratish
    def execute(self, request, current_user):

        # Tripni olamiz
        trip = self.trip_repository.get_by_id(request.trip_id)

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found",
            )

        # Driver payment yarata olmaydi
        if current_user.role == UserRole.driver:
            raise HTTPException(
                status_code=403,
                detail="Driver cannot create payment",
            )

        # Passenger faqat o'z tripi uchun payment yaratadi
        if (
            current_user.role == UserRole.passenger
            and trip.passenger_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can create payment only for your own trip",
            )

        # Shu trip uchun payment mavjudligini tekshiramiz
        existing_payment = self.payment_repository.get_by_trip_id(
            request.trip_id
        )

        if existing_payment:
            raise HTTPException(
                status_code=409,
                detail="Payment for this trip already exists",
            )

        # Payment object yaratamiz
        payment = Payment(
            id=uuid.uuid4(),
            trip_id=request.trip_id,

            # Wallet transaction hali mavjud emas
            wallet_transaction_id=None,

            amount=request.amount,
            currency=request.currency,
            payment_method=request.payment_method,

            # Payment statusi
            status=PaymentStatus.pending,

            created_at=datetime.utcnow(),
        )

        # Paymentni save qilamiz
        payment = self.payment_repository.create(payment)

        # Transaction commit qilamiz
        self.db.commit()

        # Payment objectni refresh qilamiz
        self.db.refresh(payment)

        return payment