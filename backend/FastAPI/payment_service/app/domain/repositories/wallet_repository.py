from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.wallet import Wallet
from app.domain.entities.wallet_transaction import WalletTransaction


# WalletRepository abstract interface
class WalletRepository(ABC):

    # User ID orqali walletni olish
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Wallet | None:
        pass

    # Wallet transaction yaratish
    @abstractmethod
    def create_transaction(self, transaction: WalletTransaction) -> WalletTransaction:
        pass