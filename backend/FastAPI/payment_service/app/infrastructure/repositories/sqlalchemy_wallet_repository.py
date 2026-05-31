from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.wallet import Wallet
from app.domain.entities.wallet_transaction import WalletTransaction
from app.domain.repositories.wallet_repository import WalletRepository


# SQLAlchemy wallet repository implementatsiyasi
class SqlAlchemyWalletRepository(WalletRepository):

    # Constructor
    def __init__(self, db: Session) -> None:
        self.db = db

    # User ID orqali walletni olish
    def get_by_user_id(self, user_id: UUID) -> Wallet | None:

        return (
            self.db.query(Wallet)

            # User ID filter
            .filter(Wallet.user_id == user_id)

            # Row lock qo'yiladi
            .with_for_update()

            .first()
        )

    # Wallet transaction yaratish
    def create_transaction(self, transaction: WalletTransaction) -> WalletTransaction:

        self.db.add(transaction)

        # DB ga flush qilamiz
        self.db.flush()

        # Transaction objectni refresh qilamiz
        self.db.refresh(transaction)

        return transaction