from datetime import datetime

from fastapi import HTTPException

from app.domain.entities.payment import Payment
from app.domain.entities.wallet import Wallet
from app.domain.entities.wallet_transaction import WalletTransaction

from app.domain.enums.payment_enum import PaymentStatus

from app.domain.enums.wallet_enum import WalletTransactionStatus
from app.domain.enums.wallet_enum import WalletTransactionType

from app.infrastructure.gateway.fake_payment_gateway import FakePaymentGateway


# Payment service classi
class PaymentService:

    # Constructor
    def __init__(self, db):

        # Database session
        self.db = db

        # Fake payment gateway
        self.gateway = FakePaymentGateway()

    # Payment yaratish
    def create_payment(
        self,
        request,
        current_user,
    ):

        # User walletini olamiz
        wallet = (
            self.db.query(Wallet)
            .filter(Wallet.user_id == current_user.id)
            .first()
        )

        if not wallet:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found",
            )

        # Balance yetarliligini tekshiramiz
        if wallet.balance < request.amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance",
            )

        # Gateway payment request
        gateway_result = self.gateway.pay(
            request.amount,
            request.currency,
        )

        # Gateway error bo'lsa
        if not gateway_result["success"]:
            raise HTTPException(
                status_code=502,
                detail="Gateway failed",
            )

        # Oldingi balance
        balance_before = wallet.balance

        # Yangi balance
        balance_after = balance_before - request.amount

        # Wallet balance update
        wallet.balance = balance_after

        # Wallet transaction yaratamiz
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            trip_id=request.trip_id,

            # Transaction turi
            type=WalletTransactionType.payment,

            # Transaction statusi
            status=WalletTransactionStatus.success,

            amount=request.amount,
            currency=request.currency,

            # Balance history
            balance_before=balance_before,
            balance_after=balance_after,

            description="Trip payment",
        )

        self.db.add(transaction)

        # Transaction ID olish uchun flush qilamiz
        self.db.flush()

        # Payment yaratamiz
        payment = Payment(
            trip_id=request.trip_id,

            # Wallet transaction ID
            wallet_transaction_id=transaction.id,

            amount=request.amount,
            currency=request.currency,
            payment_method=request.payment_method,

            # Payment statusi
            status=PaymentStatus.success,

            created_at=datetime.utcnow(),
        )

        self.db.add(payment)

        # Transaction commit qilamiz
        self.db.commit()

        # Payment objectni refresh qilamiz
        self.db.refresh(payment)

        return payment