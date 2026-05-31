from fastapi import HTTPException

from app.domain.enums.user_role import UserRole


# Current user paymentlarini olish use case
class GetMyPaymentsUseCase:

    # Constructor
    def __init__(self, payment_repository) -> None:

        # Payment repository
        self.payment_repository = payment_repository

    # Current user paymentlarini olish
    def execute(self, current_user):

        # Admin barcha paymentlarni ko'ra oladi
        if current_user.role == UserRole.admin:
            return self.payment_repository.get_all()

        # Passenger va driver faqat o'z paymentlarini ko'radi
        if current_user.role in [
            UserRole.passenger,
            UserRole.driver,
        ]:
            return self.payment_repository.get_by_user_trips(
                user_id=current_user.id,
                role=current_user.role.value,
            )

        # Access taqiqlangan
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )