from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# Payment yaratish request DTO
class PaymentCreateRequest(BaseModel):

    # Trip ID
    trip_id: UUID

    # Payment summasi
    amount: Decimal = Field(gt=0)

    # Payment currency
    currency: str = Field(min_length=1, max_length=8)

    # Payment method
    payment_method: str = Field(min_length=1, max_length=32)


# Payment authorize request DTO
class PaymentAuthorizeRequest(PaymentCreateRequest):
    pass


# Payment update request DTO
class PaymentUpdateRequest(BaseModel):

    # Yangi payment summasi
    amount: Decimal | None = Field(default=None, gt=0)

    # Yangi currency
    currency: str | None = Field(default=None, min_length=1, max_length=8)

    # Yangi payment method
    payment_method: str | None = Field(default=None, min_length=1, max_length=32)

    # Yangi payment status
    status: str | None = None


# Payment capture request DTO
class PaymentCaptureRequest(BaseModel):

    # Payment ID
    payment_id: UUID


# Payment refund request DTO
class PaymentRefundRequest(BaseModel):

    # Payment ID
    payment_id: UUID

    # Refund sababi
    reason: str | None = Field(default=None, max_length=500)


# Payment reconciliation request DTO
class PaymentReconcileRequest(BaseModel):

    # Payment ID
    payment_id: UUID


# Payment response DTO
class PaymentResponse(BaseModel):

    # Payment ID
    id: UUID

    # Trip ID
    trip_id: UUID

    # Wallet transaction ID
    wallet_transaction_id: UUID | None

    # Payment summasi
    amount: Decimal

    # Payment currency
    currency: str

    # Payment method
    payment_method: str

    # Payment statusi
    status: str

    # Payment yaratilgan vaqt
    created_at: datetime

    # SQLAlchemy object support
    model_config = {"from_attributes": True}


# Reconciliation response DTO
class ReconciliationResponse(BaseModel):

    # Payment ID
    payment_id: UUID

    # Local payment status
    local_status: str

    # Gateway payment status
    gateway_status: str

    # Statuslar bir xilmi
    is_matched: bool

    # Reconciliation message
    message: str


# Success paymentlar summary response DTO
class PaymentSuccessSummaryResponse(BaseModel):

    # Boshlanish sanasi
    date_from: str

    # Tugash sanasi
    date_to: str

    # Umumiy summa
    total_amount: Decimal

    # Paymentlar soni
    payments_count: int