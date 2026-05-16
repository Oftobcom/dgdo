from fastapi import HTTPException

from app.application.services.wallet_service import WalletService
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.wallet_transaction_type import WalletTransactionType


# Payment refund use case
class RefundPaymentUseCase:

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

    # Payment refund qilish
    def execute(self, payment_id, reason: str | None = None):

        # Paymentni olamiz
        payment = self.payment_repository.get_by_id(payment_id)

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        # Faqat success payment refund bo'ladi
        if payment.status != PaymentStatus.success:
            raise HTTPException(
                status_code=400,
                detail="Only success payment can be refunded",
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

        # Gateway refund request
        gateway_result = self.gateway.refund(str(payment.id))

        # Gateway refund error bo'lsa
        if not gateway_result["ok"]:
            raise HTTPException(
                status_code=502,
                detail="Gateway refund failed",
            )

        # Refund transaction yaratamiz
        refund_transaction = (
            self.wallet_service.create_credit_transaction(
                wallet=passenger_wallet,
                trip_id=trip.id,
                amount=payment.amount,

                # Transaction turi
                transaction_type=WalletTransactionType.refund,

                # Refund description
                description=reason or "Payment refund",
            )
        )

        # Transactionni save qilamiz
        self.wallet_repository.create_transaction(
            refund_transaction
        )

        # Payment status update
        payment.status = PaymentStatus.failed

        # Transaction commit qilamiz
        self.db.commit()

        # Payment objectni refresh qilamiz
        self.db.refresh(payment)

        return payment