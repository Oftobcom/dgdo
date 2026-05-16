from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import AdminEntity, DriverEntity, PassengerEntity, UserEntity, WalletEntity

from app.domain.entities import AdminEntity, DriverEntity, PassengerEntity, UserEntity
from app.domain.enums import UserRole, WalletOwnerType


# UserRepository abstract interface
class UserRepository(ABC):

    # Userni ID orqali olish
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> UserEntity | None:
        pass

    # Userni telefon orqali olish
    @abstractmethod
    def get_by_phone(self, phone: str) -> UserEntity | None:
        pass

    # Userni email orqali olish
    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None:
        pass

    # Barcha userlarni olish
    @abstractmethod
    def list_users(self) -> list[UserEntity]:
        pass

    # Oddiy user yaratish
    @abstractmethod
    def create_user(self, user: UserEntity) -> None:
        pass

    # Passenger yaratish
    @abstractmethod
    def create_passenger(self, passenger: PassengerEntity) -> None:
        pass

    # Driver yaratish
    @abstractmethod
    def create_driver(self, driver: DriverEntity) -> None:
        pass

    # Admin yaratish
    @abstractmethod
    def create_admin(self, admin: AdminEntity) -> None:
        pass

    # Wallet yaratish
    @abstractmethod
    def create_wallet(self, user_id: UUID, owner_type: WalletOwnerType) -> None:
        pass

    # Passengerni olish
    @abstractmethod
    def get_passenger(self, user_id: UUID) -> PassengerEntity | None:
        pass

    # Driverni olish
    @abstractmethod
    def get_driver(self, user_id: UUID) -> DriverEntity | None:
        pass

    # Adminni olish
    @abstractmethod
    def get_admin(self, user_id: UUID) -> AdminEntity | None:
        pass

    # Walletni user ID orqali olish
    @abstractmethod
    def get_wallet_by_user_id(self, user_id: UUID) -> WalletEntity | None:
        pass

    # User ma'lumotlarini update qilish
    @abstractmethod
    def update_user(
        self,
        user_id: UUID,
        phone: str | None = None,
        email: str | None = None,
        is_active: bool | None = None,
    ) -> None:
        pass

    # Passenger full name update qilish
    @abstractmethod
    def update_passenger_full_name(self, user_id: UUID, full_name: str | None) -> None:
        pass

    # Driver full name update qilish
    @abstractmethod
    def update_driver_full_name(self, user_id: UUID, full_name: str | None) -> None:
        pass

    # Admin full name update qilish
    @abstractmethod
    def update_admin_full_name(self, user_id: UUID, full_name: str | None) -> None:
        pass

    # Transaction commit qilish
    @abstractmethod
    def commit(self) -> None:
        pass