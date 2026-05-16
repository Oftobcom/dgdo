from uuid import UUID

from fastapi import APIRouter, Depends
from app.application.dto.user_dto import AdminWalletAdjustRequest, AdminWalletAdjustResponse

# DTO classlarni import qilamiz
from app.application.dto.user_dto import (
    AdminResponse,
    AdminUpdateUserRequest,
    CreateAdminRequest,
    DriverResponse,
    LoginRequest,
    RegisterDriverRequest,
    RegisterPassengerRequest,
    TokenResponse,
    UpdateMeRequest,
    UserResponse,
)

# UserService ni import qilamiz
from app.application.services.user_service import UserService

# UserEntity modelini import qilamiz
from app.domain.entities import UserEntity

# Dependency functionlarni import qilamiz
from app.presentation.dependencies import (
    get_current_user,
    get_user_service,
    require_admin,
)



# Users uchun router yaratamiz
router = APIRouter(
    prefix="/users",   # Base endpoint
    tags=["Users"],    # Swagger tag
)


# Passenger register endpoint
@router.post("/passengers/register", response_model=UserResponse)
def register_passenger(
    request: RegisterPassengerRequest,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.register_passenger(request)


# Driver register endpoint
@router.post("/drivers/register", response_model=DriverResponse)
def register_driver(
    request: RegisterDriverRequest,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.register_driver(request)


# Login endpoint
@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    token = user_service.login(request)

    # Access token qaytaramiz
    return TokenResponse(access_token=token)


# Current user ma'lumotini olish endpointi
@router.get("/me", response_model=UserResponse | DriverResponse | AdminResponse)
def get_me(
    current_user: UserEntity = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return user_service.get_me(current_user.id)


# Current user ma'lumotini update qilish endpointi
@router.put("/me", response_model=UserResponse | DriverResponse | AdminResponse)
def update_me(
    request: UpdateMeRequest,
    current_user: UserEntity = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return user_service.update_me(current_user.id, request)


# Admin yaratish endpointi
@router.post("/admins", response_model=AdminResponse)
def create_admin(
    request: CreateAdminRequest,

    # Faqat admin access oladi
    _: UserEntity = Depends(require_admin),

    user_service: UserService = Depends(get_user_service),
):
    return user_service.create_admin(request)


# Barcha userlarni olish endpointi
@router.get("", response_model=list[UserResponse])
def get_all_users(
    _: UserEntity = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    return user_service.get_all_users()


# Admin userni update qilishi uchun endpoint
@router.put("/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: UUID,
    request: AdminUpdateUserRequest,
    _: UserEntity = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    return user_service.admin_update_user(user_id, request)


# Userni deactivate qilish endpointi
@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: UUID,
    _: UserEntity = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    return user_service.deactivate_user(user_id)


# Userni activate qilish endpointi
@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: UUID,
    _: UserEntity = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    return user_service.activate_user(user_id)

# Admin user wallet balanceini adjustment qiladi
@router.patch("/{user_id}/wallet/adjust", response_model=AdminWalletAdjustResponse)
def admin_adjust_wallet(
    user_id: UUID,
    request: AdminWalletAdjustRequest,
    _: UserEntity = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    return user_service.admin_adjust_wallet(user_id, request)