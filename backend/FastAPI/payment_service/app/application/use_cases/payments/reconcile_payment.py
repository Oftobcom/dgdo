from fastapi import HTTPException

from app.application.dto.payment_dto import ReconciliationResponse


# Payment reconciliation use case
class ReconcilePaymentUseCase:

    # Constructor
    def __init__(self, payment_repository, gateway) -> None:

        # Payment repository
        self.payment_repository = payment_repository

        # Payment gateway
        self.gateway = gateway

    # Payment reconciliation qilish
    def execute(self, payment_id) -> ReconciliationResponse:

        # Paymentni olamiz
        payment = self.payment_repository.get_by_id(payment_id)

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        # Gateway statusni olamiz
        gateway_result = self.gateway.fetch_status(
            payment.status.value
        )

        # Gateway error bo'lsa
        if not gateway_result["ok"]:
            raise HTTPException(
                status_code=502,
                detail="Gateway reconciliation failed",
            )

        # Local status -> gateway status mapping
        expected = {
            "pending": "authorized",
            "success": "captured",
            "failed": "refunded_or_failed",
        }

        # Gateway status
        gateway_status = gateway_result["gateway_status"]

        # Kutilayotgan gateway status
        expected_gateway_status = expected[
            payment.status.value
        ]

        # Reconciliation response qaytaramiz
        return ReconciliationResponse(
            payment_id=payment.id,

            # Local payment status
            local_status=payment.status.value,

            # Gateway payment status
            gateway_status=gateway_status,

            # Statuslar mosligini tekshiramiz
            is_matched=(
                gateway_status == expected_gateway_status
            ),

            message="Payment reconciliation completed",
        )