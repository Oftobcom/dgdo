from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

# Payment DTO classlar
from app.application.dto.payment_dto import (
    PaymentAuthorizeRequest,
    PaymentCaptureRequest,
    PaymentCreateRequest,
    PaymentReconcileRequest,
    PaymentRefundRequest,
    PaymentResponse,
    PaymentSuccessSummaryResponse,
    PaymentUpdateRequest,
    ReconciliationResponse,
)

# Payment use case classlar
from app.application.use_cases.payments.authorize_payment import AuthorizePaymentUseCase
from app.application.use_cases.payments.capture_payment import CapturePaymentUseCase
from app.application.use_cases.payments.create_payment import CreatePaymentUseCase
from app.application.use_cases.payments.delete_payment import DeletePaymentUseCase
from app.application.use_cases.payments.get_all_payments import GetAllPaymentsUseCase
from app.application.use_cases.payments.get_my_payments import GetMyPaymentsUseCase
from app.application.use_cases.payments.get_payment import GetPaymentUseCase
from app.application.use_cases.payments.get_success_summary import GetSuccessSummaryUseCase
from app.application.use_cases.payments.reconcile_payment import ReconcilePaymentUseCase
from app.application.use_cases.payments.refund_payment import RefundPaymentUseCase
from app.application.use_cases.payments.update_payment import UpdatePaymentUseCase

# Database dependency
from app.core.database import get_db

# Fake payment gateway
from app.infrastructure.gateways.fake_payment_gateway import FakePaymentGateway

# Repository classlar
from app.infrastructure.repositories.sqlalchemy_payment_repository import SqlAlchemyPaymentRepository
from app.infrastructure.repositories.sqlalchemy_trip_repository import SqlAlchemyTripRepository
from app.infrastructure.repositories.sqlalchemy_wallet_repository import SqlAlchemyWalletRepository

# Auth dependency
from app.presentation.dependencies.auth_dependency import get_current_user, require_admin


# Payments router
router = APIRouter(prefix="/payments", tags=["Payments"])


# Repository objectlarini yaratish
def get_repositories(db: Session):
    return {
        "payment": SqlAlchemyPaymentRepository(db),
        "trip": SqlAlchemyTripRepository(db),
        "wallet": SqlAlchemyWalletRepository(db),
        "gateway": FakePaymentGateway(),
    }


# Success paymentlar summary endpointi
@router.get("/success/summary", response_model=PaymentSuccessSummaryResponse)
def get_success_payments_summary(

    # Boshlanish sanasi
    date_from: str = Query(..., description="Start date in YYYY-MM-DD format"),

    # Tugash sanasi
    date_to: str = Query(..., description="End date in YYYY-MM-DD format"),

    # Faqat admin access
    _: object = Depends(require_admin),

    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Use case yaratamiz
    use_case = GetSuccessSummaryUseCase(
        payment_repository=repos["payment"],
    )

    return use_case.execute(date_from, date_to)


# Payment authorize endpointi
@router.post("/authorize", response_model=PaymentResponse)
def authorize_payment(
    request: PaymentAuthorizeRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Payment create use case
    create_payment_use_case = CreatePaymentUseCase(
        payment_repository=repos["payment"],
        trip_repository=repos["trip"],
        db=db,
    )

    # Authorize use case
    use_case = AuthorizePaymentUseCase(
        gateway=repos["gateway"],
        create_payment_use_case=create_payment_use_case,
    )

    return use_case.execute(request, current_user)


# Payment capture endpointi
@router.post("/capture", response_model=PaymentResponse)
def capture_payment(
    request: PaymentCaptureRequest,

    # Faqat admin access
    _: object = Depends(require_admin),

    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Capture use case
    use_case = CapturePaymentUseCase(
        payment_repository=repos["payment"],
        trip_repository=repos["trip"],
        wallet_repository=repos["wallet"],
        gateway=repos["gateway"],
        db=db,
    )

    return use_case.execute(request.payment_id)


# Payment refund endpointi
@router.post("/refund", response_model=PaymentResponse)
def refund_payment(
    request: PaymentRefundRequest,

    # Faqat admin access
    _: object = Depends(require_admin),

    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Refund use case
    use_case = RefundPaymentUseCase(
        payment_repository=repos["payment"],
        trip_repository=repos["trip"],
        wallet_repository=repos["wallet"],
        gateway=repos["gateway"],
        db=db,
    )

    return use_case.execute(request.payment_id, request.reason)


# Payment reconciliation endpointi
@router.post("/reconcile", response_model=ReconciliationResponse)
def reconcile_payment(
    request: PaymentReconcileRequest,

    # Faqat admin access
    _: object = Depends(require_admin),

    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Reconciliation use case
    use_case = ReconcilePaymentUseCase(
        payment_repository=repos["payment"],
        gateway=repos["gateway"],
    )

    return use_case.execute(request.payment_id)


# Payment yaratish endpointi
@router.post("", response_model=PaymentResponse)
def create_payment(
    request: PaymentCreateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Create payment use case
    use_case = CreatePaymentUseCase(
        payment_repository=repos["payment"],
        trip_repository=repos["trip"],
        db=db,
    )

    return use_case.execute(request, current_user)


# Barcha paymentlarni olish endpointi
@router.get("", response_model=list[PaymentResponse])
def get_all_payments(

    # Faqat admin access
    _: object = Depends(require_admin),

    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Get all payments use case
    use_case = GetAllPaymentsUseCase(
        payment_repository=repos["payment"],
    )

    return use_case.execute()


# Current user paymentlarini olish endpointi
@router.get("/my", response_model=list[PaymentResponse])
def get_my_payments(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # My payments use case
    use_case = GetMyPaymentsUseCase(
        payment_repository=repos["payment"],
    )

    return use_case.execute(current_user)


# Bitta paymentni olish endpointi
@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Get payment use case
    use_case = GetPaymentUseCase(
        payment_repository=repos["payment"],
        trip_repository=repos["trip"],
    )

    return use_case.execute(payment_id, current_user)


# Payment update endpointi
@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: UUID,
    request: PaymentUpdateRequest,

    # Faqat admin access
    _: object = Depends(require_admin),

    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Update payment use case
    use_case = UpdatePaymentUseCase(
        payment_repository=repos["payment"],
        db=db,
    )

    return use_case.execute(payment_id, request)


# Payment delete endpointi
@router.delete("/{payment_id}")
def delete_payment(
    payment_id: UUID,

    # Faqat admin access
    _: object = Depends(require_admin),

    db: Session = Depends(get_db),
):
    repos = get_repositories(db)

    # Delete payment use case
    use_case = DeletePaymentUseCase(
        payment_repository=repos["payment"],
        db=db,
    )

    return use_case.execute(payment_id)