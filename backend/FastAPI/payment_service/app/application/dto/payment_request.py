from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


# Payment yaratish request DTO
class CreatePaymentRequest(BaseModel):

    # Trip ID
    trip_id: UUID

    # Payment summasi
    amount: Decimal = Field(gt=0)

    # Payment currency
    currency: str

    # Payment method
    payment_method: str