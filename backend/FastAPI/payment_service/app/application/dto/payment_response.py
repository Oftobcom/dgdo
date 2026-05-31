from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


# Payment response DTO
class PaymentResponse(BaseModel):

    # Payment ID
    id: UUID

    # Trip ID
    trip_id: UUID

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
    model_config = {
        "from_attributes": True,
    }