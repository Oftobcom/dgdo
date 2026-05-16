import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

# Repository interface
from app.application.interfaces.user_repository import UserRepository

# Entity classlar
from app.domain.entities import AdminEntity, DriverEntity, PassengerEntity, UserEntity

# Enum class
from app.domain.enums import WalletOwnerType

# SQLAlchemy modellari
from app.infrastructure.models.user_models import (
    AdminModel,
    DriverModel,
    PassengerModel,
    UserModel,
    WalletModel,
)

from app.domain.entities import WalletEntity
from app.infrastructure.models.user_models import WalletModel


# SQLAlchemy repository implementatsiyasi
class SqlAlchemyUserRepository(UserRepository):

    # Constructor
    def __init__(self, db: Session) -> None:
        self.db = db

    # UserModel -> UserEntity convert qilish
    def _to_user_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            role=model.role,
            phone=model.phone,
            email=model.email,
            password_hash=model.password_hash,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # Userni ID orqali olish
    def get_by_id(self, user_id: UUID) -> UserEntity | None:

        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()

        return self._to_user_entity(user) if user else None

    # Userni telefon orqali olish
    def get_by_phone(self, phone: str) -> UserEntity | None:

        user = self.db.query(UserModel).filter(UserModel.phone == phone).first()

        return self._to_user_entity(user) if user else None

    # Userni email orqali olish
    def get_by_email(self, email: str) -> UserEntity | None:

        user = self.db.query(UserModel).filter(UserModel.email == email).first()

        return self._to_user_entity(user) if user else None

    # Barcha userlarni olish
    def list_users(self) -> list[UserEntity]:

        users = self.db.query(UserModel).order_by(UserModel.created_at.desc()).all()

        return [self._to_user_entity(user) for user in users]

    # User yaratish
    def create_user(self, user: UserEntity) -> None:

        model = UserModel(
            id=user.id,
            role=user.role,
            phone=user.phone,
            email=user.email,
            password_hash=user.password_hash,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        self.db.add(model)

    # Passenger yaratish
    def create_passenger(self, passenger: PassengerEntity) -> None:

        model = PassengerModel(
            user_id=passenger.user_id,
            full_name=passenger.full_name,
            rating=passenger.rating,
            created_at=passenger.created_at,
        )

        self.db.add(model)

    # Driver yaratish
    def create_driver(self, driver: DriverEntity) -> None:

        model = DriverModel(
            user_id=driver.user_id,
            full_name=driver.full_name,
            license_number=driver.license_number,
            is_verified=driver.is_verified,
            rating=driver.rating,
            created_at=driver.created_at,
        )

        self.db.add(model)

    # Admin yaratish
    def create_admin(self, admin: AdminEntity) -> None:

        model = AdminModel(
            user_id=admin.user_id,
            full_name=admin.full_name,
            admin_level=admin.admin_level,
            created_at=admin.created_at,
        )

        self.db.add(model)

    # Wallet yaratish
    def create_wallet(self, user_id: UUID, owner_type: WalletOwnerType) -> None:

        model = WalletModel(
            id=uuid.uuid4(),
            user_id=user_id,
            owner_type=owner_type,
            balance=0,
            currency="TJS",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=None,
        )

        self.db.add(model)

    # Passengerni olish
    def get_passenger(self, user_id: UUID) -> PassengerEntity | None:

        passenger = (
            self.db.query(PassengerModel)
            .filter(PassengerModel.user_id == user_id)
            .first()
        )

        if not passenger:
            return None

        return PassengerEntity(
            user_id=passenger.user_id,
            full_name=passenger.full_name,
            rating=float(passenger.rating) if passenger.rating is not None else None,
            created_at=passenger.created_at,
        )

    # Driverni olish
    def get_driver(self, user_id: UUID) -> DriverEntity | None:

        driver = (
            self.db.query(DriverModel)
            .filter(DriverModel.user_id == user_id)
            .first()
        )

        if not driver:
            return None

        return DriverEntity(
            user_id=driver.user_id,
            full_name=driver.full_name,
            license_number=driver.license_number,
            is_verified=driver.is_verified,
            rating=float(driver.rating) if driver.rating is not None else None,
            created_at=driver.created_at,
        )

    # Adminni olish
    def get_admin(self, user_id: UUID) -> AdminEntity | None:

        admin = (
            self.db.query(AdminModel)
            .filter(AdminModel.user_id == user_id)
            .first()
        )

        if not admin:
            return None

        return AdminEntity(
            user_id=admin.user_id,
            full_name=admin.full_name,
            admin_level=admin.admin_level,
            created_at=admin.created_at,
        )

    # User update qilish
    def update_user(
        self,
        user_id: UUID,
        phone: str | None = None,
        email: str | None = None,
        is_active: bool | None = None,
    ) -> None:

        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()

        if not user:
            return

        # Telefon update
        if phone is not None:
            user.phone = phone

        # Email update
        if email is not None:
            user.email = email

        # Active status update
        if is_active is not None:
            user.is_active = is_active

        # Update vaqtini yozamiz
        user.updated_at = datetime.utcnow()

    # Passenger full name update
    def update_passenger_full_name(self, user_id: UUID, full_name: str | None) -> None:

        passenger = (
            self.db.query(PassengerModel)
            .filter(PassengerModel.user_id == user_id)
            .first()
        )

        if passenger:
            passenger.full_name = full_name

    # Driver full name update
    def update_driver_full_name(self, user_id: UUID, full_name: str | None) -> None:

        driver = (
            self.db.query(DriverModel)
            .filter(DriverModel.user_id == user_id)
            .first()
        )

        if driver:
            driver.full_name = full_name

    # Admin full name update
    def update_admin_full_name(self, user_id: UUID, full_name: str | None) -> None:

        admin = (
            self.db.query(AdminModel)
            .filter(AdminModel.user_id == user_id)
            .first()
        )

        if admin:
            admin.full_name = full_name

    # Transaction commit qilish
    def commit(self) -> None:
        self.db.commit()
    
        # Walletni user ID orqali olish
    def get_wallet_by_user_id(self, user_id: UUID) -> WalletEntity | None:
        wallet = (
            self.db.query(WalletModel)
            .filter(WalletModel.user_id == user_id)
            .first()
        )

        if not wallet:
            return None

        return WalletEntity(
            id=wallet.id,
            user_id=wallet.user_id,
            owner_type=wallet.owner_type.value,
            balance=wallet.balance,
            currency=wallet.currency,
            is_active=wallet.is_active,
            created_at=wallet.created_at,
            updated_at=wallet.updated_at,
        )