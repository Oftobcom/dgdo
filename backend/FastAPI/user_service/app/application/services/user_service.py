import uuid
from datetime import datetime
from uuid import UUID

from app.application.dto.user_dto import WalletResponse
from fastapi import HTTPException, status

# DTO classlarni import qilamiz
from app.application.dto.user_dto import (
    AdminResponse,
    AdminUpdateUserRequest,
    CreateAdminRequest,
    DriverResponse,
    LoginRequest,
    RegisterDriverRequest,
    RegisterPassengerRequest,
    UpdateMeRequest,
    UserResponse,
)

# Repository interface ni import qilamiz
from app.application.interfaces.user_repository import UserRepository

# Security helper functionlar
from app.core.security import create_access_token, hash_password, verify_password

# Entity classlarni import qilamiz
from app.domain.entities import AdminEntity, DriverEntity, PassengerEntity, UserEntity

# Enum classlarni import qilamiz
from app.domain.enums import UserRole, WalletOwnerType


# UserService business logic classi
class UserService:

    # Constructor
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    # Passenger register qilish
    def register_passenger(self, request: RegisterPassengerRequest) -> UserResponse:

        # Telefon unique ekanligini tekshiramiz
        self._ensure_phone_is_unique(request.phone)

        # Email unique ekanligini tekshiramiz
        self._ensure_email_is_unique(request.email)

        now = datetime.utcnow()
        user_id = uuid.uuid4()

        # User entity yaratamiz
        user = UserEntity(
            id=user_id,
            role=UserRole.passenger,
            phone=request.phone,
            email=request.email,

            # Password hash qilinadi
            password_hash=hash_password(request.password),

            is_active=True,
            created_at=now,
            updated_at=None,
        )

        # Passenger entity yaratamiz
        passenger = PassengerEntity(
            user_id=user_id,
            full_name=request.full_name,
            rating=5.0,
            created_at=now,
        )

        # DB ga save qilamiz
        self.user_repository.create_user(user)
        self.user_repository.create_passenger(passenger)

        # Passenger wallet yaratamiz
        self.user_repository.create_wallet(user_id, WalletOwnerType.passenger)

        self.user_repository.commit()

        return self._build_user_response(user)

    # Driver register qilish
    def register_driver(self, request: RegisterDriverRequest) -> DriverResponse:

        self._ensure_phone_is_unique(request.phone)
        self._ensure_email_is_unique(request.email)

        now = datetime.utcnow()
        user_id = uuid.uuid4()

        # Driver uchun user entity
        user = UserEntity(
            id=user_id,
            role=UserRole.driver,
            phone=request.phone,
            email=request.email,
            password_hash=hash_password(request.password),
            is_active=True,
            created_at=now,
            updated_at=None,
        )

        # Driver entity yaratamiz
        driver = DriverEntity(
            user_id=user_id,
            full_name=request.full_name,
            license_number=request.license_number,
            is_verified=False,
            rating=5.0,
            created_at=now,
        )

        # DB ga save qilamiz
        self.user_repository.create_user(user)
        self.user_repository.create_driver(driver)

        # Driver wallet yaratamiz
        self.user_repository.create_wallet(user_id, WalletOwnerType.driver)

        self.user_repository.commit()

        return self._build_driver_response(user, driver)

    # Admin yaratish
    def create_admin(self, request: CreateAdminRequest) -> AdminResponse:

        self._ensure_phone_is_unique(request.phone)
        self._ensure_email_is_unique(request.email)

        now = datetime.utcnow()
        user_id = uuid.uuid4()

        # Admin user entity
        user = UserEntity(
            id=user_id,
            role=UserRole.admin,
            phone=request.phone,
            email=request.email,
            password_hash=hash_password(request.password),
            is_active=True,
            created_at=now,
            updated_at=None,
        )

        # Admin entity
        admin = AdminEntity(
            user_id=user_id,
            full_name=request.full_name,
            admin_level=request.admin_level,
            created_at=now,
        )

        # DB ga save qilamiz
        self.user_repository.create_user(user)
        self.user_repository.create_admin(admin)

        self.user_repository.commit()

        return self._build_admin_response(user, admin)

    # Login qilish
    def login(self, request: LoginRequest) -> str:

        # Userni telefon orqali topamiz
        user = self.user_repository.get_by_phone(request.phone)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone or password",
            )

        # Password verify qilamiz
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone or password",
            )

        # User inactive bo'lsa
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        # JWT token yaratamiz
        return create_access_token(str(user.id))

    # Current user ma'lumotini olish
    def get_me(self, user_id: UUID) -> UserResponse | DriverResponse | AdminResponse:

        user = self._get_user_or_404(user_id)

        # Passenger response
        if user.role == UserRole.passenger:
            return self._build_user_response(user)

        # Driver response
        if user.role == UserRole.driver:

            driver = self.user_repository.get_driver(user.id)

            if not driver:
                raise HTTPException(status_code=404, detail="Driver profile not found")

            return self._build_driver_response(user, driver)

        # Admin response
        if user.role == UserRole.admin:

            admin = self.user_repository.get_admin(user.id)

            if not admin:
                raise HTTPException(status_code=404, detail="Admin profile not found")

            return self._build_admin_response(user, admin)

        raise HTTPException(status_code=400, detail="Unsupported user role")
    
        # Wallet response yasash
    def _build_wallet_response(self, user_id: UUID) -> WalletResponse | None:
        wallet = self.user_repository.get_wallet_by_user_id(user_id)

        if not wallet:
            return None

        return WalletResponse(
            balance=wallet.balance,
            currency=wallet.currency,
        )

    # Current userni update qilish
    def update_me(self, user_id: UUID, request: UpdateMeRequest) -> UserResponse | DriverResponse | AdminResponse:

        user = self._get_user_or_404(user_id)

        # Email unique ekanligini tekshiramiz
        if request.email is not None and request.email != user.email:
            self._ensure_email_is_unique(request.email)

        # User update
        self.user_repository.update_user(
            user_id=user.id,
            email=request.email,
        )

        # Passenger full name update
        if user.role == UserRole.passenger:
            self.user_repository.update_passenger_full_name(user.id, request.full_name)

        # Driver full name update
        if user.role == UserRole.driver:
            self.user_repository.update_driver_full_name(user.id, request.full_name)

        # Admin full name update
        if user.role == UserRole.admin:
            self.user_repository.update_admin_full_name(user.id, request.full_name)

        self.user_repository.commit()

        return self.get_me(user.id)

    # Barcha userlarni olish
    def get_all_users(self) -> list[UserResponse]:

        users = self.user_repository.list_users()

        return [self._build_user_response(user) for user in users]

    # Admin user update qilish
    def admin_update_user(self, user_id: UUID, request: AdminUpdateUserRequest) -> UserResponse:

        user = self._get_user_or_404(user_id)

        # Telefon unique tekshiruvi
        if request.phone is not None and request.phone != user.phone:
            self._ensure_phone_is_unique(request.phone)

        # Email unique tekshiruvi
        if request.email is not None and request.email != user.email:
            self._ensure_email_is_unique(request.email)

        # User update
        self.user_repository.update_user(
            user_id=user.id,
            phone=request.phone,
            email=request.email,
            is_active=request.is_active,
        )

        # Full name update
        if request.full_name is not None:

            if user.role == UserRole.passenger:
                self.user_repository.update_passenger_full_name(user.id, request.full_name)

            if user.role == UserRole.driver:
                self.user_repository.update_driver_full_name(user.id, request.full_name)

            if user.role == UserRole.admin:
                self.user_repository.update_admin_full_name(user.id, request.full_name)

        self.user_repository.commit()

        updated_user = self._get_user_or_404(user.id)

        return self._build_user_response(updated_user)

    # Userni deactivate qilish
    def deactivate_user(self, user_id: UUID) -> UserResponse:

        user = self._get_user_or_404(user_id)

        self.user_repository.update_user(
            user_id=user.id,
            is_active=False,
        )

        self.user_repository.commit()

        updated_user = self._get_user_or_404(user.id)

        return self._build_user_response(updated_user)

    # Userni activate qilish
    def activate_user(self, user_id: UUID) -> UserResponse:

        user = self._get_user_or_404(user_id)

        self.user_repository.update_user(
            user_id=user.id,
            is_active=True,
        )

        self.user_repository.commit()

        updated_user = self._get_user_or_404(user.id)

        return self._build_user_response(updated_user)

    # Telefon unique ekanligini tekshirish
    def _ensure_phone_is_unique(self, phone: str) -> None:

        existing_user = self.user_repository.get_by_phone(phone)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone already exists",
            )

    # Email unique ekanligini tekshirish
    def _ensure_email_is_unique(self, email: str | None) -> None:

        if email is None:
            return

        existing_user = self.user_repository.get_by_email(email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

    # Userni topish yoki 404 qaytarish
    def _get_user_or_404(self, user_id: UUID) -> UserEntity:

        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    # Oddiy user response build qilish
    def _build_user_response(self, user: UserEntity) -> UserResponse:

        full_name = None

        # Passenger full name
        if user.role == UserRole.passenger:
            passenger = self.user_repository.get_passenger(user.id)
            full_name = passenger.full_name if passenger else None

        # Driver full name
        if user.role == UserRole.driver:
            driver = self.user_repository.get_driver(user.id)
            full_name = driver.full_name if driver else None

        # Admin full name
        if user.role == UserRole.admin:
            admin = self.user_repository.get_admin(user.id)
            full_name = admin.full_name if admin else None

        return UserResponse(
            id=user.id,
            role=user.role.value,
            phone=user.phone,
            email=user.email,
            full_name=full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            wallet=self._build_wallet_response(user.id),
        )

    # Driver response build qilish
    def _build_driver_response(self, user: UserEntity, driver: DriverEntity) -> DriverResponse:

        return DriverResponse(
            id=user.id,
            role=user.role.value,
            phone=user.phone,
            email=user.email,
            full_name=driver.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            license_number=driver.license_number,
            is_verified=driver.is_verified,
            wallet=self._build_wallet_response(user.id),
        )

    # Admin response build qilish
    def _build_admin_response(self, user: UserEntity, admin: AdminEntity) -> AdminResponse:

        return AdminResponse(
            id=user.id,
            role=user.role.value,
            phone=user.phone,
            email=user.email,
            full_name=admin.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            admin_level=admin.admin_level,
            wallet=self._build_wallet_response(user.id),
        )