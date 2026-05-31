from fastapi import HTTPException


# Payment authorize use case
class AuthorizePaymentUseCase:

    # Constructor
    def __init__(self, gateway, create_payment_use_case) -> None:

        # Payment gateway
        self.gateway = gateway

        # Create payment use case
        self.create_payment_use_case = create_payment_use_case

    # Payment authorize qilish
    def execute(self, request, current_user):

        # Gateway authorize request
        gateway_result = self.gateway.authorize(
            amount=request.amount,
            currency=request.currency,
            payment_method=request.payment_method,
        )

        # Gateway authorize muvaffaqiyatsiz bo'lsa
        if not gateway_result["ok"]:
            raise HTTPException(
                status_code=502,
                detail="Gateway authorization failed",
            )

        # Payment yaratamiz
        return self.create_payment_use_case.execute(
            request,
            current_user,
        )