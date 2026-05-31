from fastapi import HTTPException


# Payment delete use case
class DeletePaymentUseCase:

    # Constructor
    def __init__(self, payment_repository, db) -> None:

        # Payment repository
        self.payment_repository = payment_repository

        # Database session
        self.db = db

    # Paymentni o'chirish
    def execute(self, payment_id):

        # Paymentni olamiz
        payment = self.payment_repository.get_by_id(payment_id)

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        # Paymentni delete qilamiz
        self.payment_repository.delete(payment)

        # Transaction commit qilamiz
        self.db.commit()

        return {
            "message": "Payment deleted successfully",
        }