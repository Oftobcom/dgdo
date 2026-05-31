from datetime import datetime, time
from decimal import Decimal

from fastapi import HTTPException

from app.application.dto.payment_dto import PaymentSuccessSummaryResponse


# Success paymentlar summary use case
class GetSuccessSummaryUseCase:

    # Constructor
    def __init__(self, payment_repository) -> None:

        # Payment repository
        self.payment_repository = payment_repository

    # Success paymentlar summary olish
    def execute(
        self,
        date_from: str,
        date_to: str,
    ) -> PaymentSuccessSummaryResponse:

        try:
            # String sanani datetime ga aylantiramiz
            from_dt = datetime.strptime(
                date_from,
                "%Y-%m-%d",
            )

            to_dt = datetime.strptime(
                date_to,
                "%Y-%m-%d",
            )

        except ValueError:

            # Sana formati noto'g'ri bo'lsa
            raise HTTPException(
                status_code=400,
                detail="Date format must be YYYY-MM-DD",
            )

        # date_from katta bo'lmasligi kerak
        if from_dt > to_dt:
            raise HTTPException(
                status_code=400,
                detail="date_from cannot be greater than date_to",
            )

        # Kun boshidagi vaqt
        start_datetime = datetime.combine(
            from_dt.date(),
            time.min,
        )

        # Kun oxiridagi vaqt
        end_datetime = datetime.combine(
            to_dt.date(),
            time.max,
        )

        # Success paymentlar summary olamiz
        total_amount, payments_count = (
            self.payment_repository.success_summary(
                start_datetime,
                end_datetime,
            )
        )

        # Response qaytaramiz
        return PaymentSuccessSummaryResponse(
            date_from=date_from,
            date_to=date_to,

            # Umumiy summa
            total_amount=Decimal(total_amount),

            # Paymentlar soni
            payments_count=payments_count,
        )