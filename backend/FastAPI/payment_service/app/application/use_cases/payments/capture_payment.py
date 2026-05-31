from datetime import datetime

from fastapi import HTTPException

from app.application.services.wallet_service import WalletService
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.wallet_transaction_type import WalletTransactionType


# Payment capture use case
class CapturePaymentUseCase:

    # Constructor
    def __init__(
        self,
        payment_repository,
        trip_repository,
        wallet_repository,
        gateway,
        db,
    ) -> None:

        # Payment repository
        self.payment_repository = payment_repository

        # Trip repository
        self.trip_repository = trip_repository

        # Wallet repository
        self.wallet_repository = wallet_repository

        # Payment gateway
        self.gateway = gateway

        # Database session
        self.db = db

        # Wallet service
        self.wallet_service = WalletService()

    # Payment capture qilish
    def execute(self, payment_id):

        # Paymentni olamiz
        payment = self.payment_repository.get_by_id(payment_id)

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        # Faqat pending payment capture bo'ladi
        if payment.status != PaymentStatus.pending:
            raise HTTPException(
                status_code=400,
                detail="Only pending payment can be captured",
            )

        # Tripni olamiz
        trip = self.trip_repository.get_by_id(payment.trip_id)

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found",
            )

        # Passenger walletini olamiz
        passenger_wallet = self.wallet_repository.get_by_user_id(
            trip.passenger_id
        )

        if not passenger_wallet:
            raise HTTPException(
                status_code=404,
                detail="Passenger wallet not found",
            )

        # Gateway capture request
        gateway_result = self.gateway.capture(str(payment.id))

        # Gateway capture error bo'lsa
        if not gateway_result["ok"]:
            raise HTTPException(
                status_code=502,
                detail="Gateway capture failed",
            )

        # Passenger debit transaction yaratamiz
        passenger_transaction = (
            self.wallet_service.create_debit_transaction(
                wallet=passenger_wallet,
                trip_id=trip.id,
                amount=payment.amount,
                description="Passenger trip payment",
            )
        )

        # Transactionni save qilamiz
        self.wallet_repository.create_transaction(
            passenger_transaction
        )

        # Driver mavjud bo'lsa
        if trip.driver_id:

            # Driver walletini olamiz
            driver_wallet = self.wallet_repository.get_by_user_id(
                trip.driver_id
            )

            if driver_wallet:

                # Driver earning transaction
                driver_transaction = (
                    self.wallet_service.create_credit_transaction(
                        wallet=driver_wallet,
                        trip_id=trip.id,
                        amount=payment.amount,
                        transaction_type=WalletTransactionType.driver_earning,
                        description="Driver earning for trip",
                    )
                )

                # Transactionni save qilamiz
                self.wallet_repository.create_transaction(
                    driver_transaction
                )

        # Paymentga transaction ID yozamiz
        payment.wallet_transaction_id = passenger_transaction.id

        # Payment status update
        payment.status = PaymentStatus.success

        # Trip status update
        trip.status = TripStatus.completed

        # Trip completed vaqti
        trip.completed_at = datetime.utcnow()

        # Transaction commit qilamiz
        self.db.commit()

        # Payment objectni refresh qilamiz
        self.db.refresh(payment)

        return payment