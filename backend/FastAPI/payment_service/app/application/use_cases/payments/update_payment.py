from fastapi import HTTPException

from app.domain.enums.payment_status import PaymentStatus


# Payment update use case
class UpdatePaymentUseCase:

    # Constructor
    def __init__(self, payment_repository, db) -> None:

        # Payment repository
        self.payment_repository = payment_repository

        # Database session
        self.db = db

    # Paymentni update qilish
    def execute(self, payment_id, request):

        # Paymentni olamiz
        payment = self.payment_repository.get_by_id(payment_id)

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        # Amount update
        if request.amount is not None:
            payment.amount = request.amount

        # Currency update
        if request.currency is not None:
            payment.currency = request.currency

        # Payment method update
        if request.payment_method is not None:
            payment.payment_method = request.payment_method

        # Status update
        if request.status is not None:
            try:
                payment.status = PaymentStatus(request.status)

            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid status. Allowed: pending, success, failed",
                )

        # Transaction commit qilamiz
        self.db.commit()

        # Payment objectni refresh qilamiz
        self.db.refresh(payment)

        return payment