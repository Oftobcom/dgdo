import uuid
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException

from app.domain.entities.wallet import Wallet
from app.domain.entities.wallet_transaction import WalletTransaction
from app.domain.enums.wallet_transaction_status import WalletTransactionStatus
from app.domain.enums.wallet_transaction_type import WalletTransactionType


# Wallet service classi
class WalletService:

    # Debit transaction yaratish
    def create_debit_transaction(
        self,
        wallet: Wallet,
        trip_id: UUID,
        amount: Decimal,
        description: str,
    ) -> WalletTransaction:

        # Wallet active ekanligini tekshiramiz
        if not wallet.is_active:
            raise HTTPException(
                status_code=400,
                detail="Wallet is inactive",
            )

        # Balance yetarliligini tekshiramiz
        if wallet.balance < amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance",
            )

        # Oldingi balance
        balance_before = wallet.balance

        # Yangi balance
        balance_after = balance_before - amount

        # Wallet balance update
        wallet.balance = balance_after

        # Wallet update vaqtini yozamiz
        wallet.updated_at = datetime.utcnow()

        # Wallet transaction object yaratamiz
        return WalletTransaction(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            trip_id=trip_id,

            # Transaction turi
            type=WalletTransactionType.payment,

            # Transaction statusi
            status=WalletTransactionStatus.success,

            amount=amount,
            currency=wallet.currency,

            # Balance history
            balance_before=balance_before,
            balance_after=balance_after,

            description=description,
            created_at=datetime.utcnow(),
        )

    # Credit transaction yaratish
    def create_credit_transaction(
        self,
        wallet: Wallet,
        trip_id: UUID,
        amount: Decimal,
        transaction_type: WalletTransactionType,
        description: str,
    ) -> WalletTransaction:

        # Wallet active ekanligini tekshiramiz
        if not wallet.is_active:
            raise HTTPException(
                status_code=400,
                detail="Wallet is inactive",
            )

        # Oldingi balance
        balance_before = wallet.balance

        # Yangi balance
        balance_after = balance_before + amount

        # Wallet balance update
        wallet.balance = balance_after

        # Wallet update vaqtini yozamiz
        wallet.updated_at = datetime.utcnow()

        # Wallet transaction object yaratamiz
        return WalletTransaction(
            id=uuid.uuid4(),
            wallet_id=wallet.id,
            trip_id=trip_id,

            # Transaction turi
            type=transaction_type,

            # Transaction statusi
            status=WalletTransactionStatus.success,

            amount=amount,
            currency=wallet.currency,

            # Balance history
            balance_before=balance_before,
            balance_after=balance_after,

            description=description,
            created_at=datetime.utcnow(),
        )