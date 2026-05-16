from fastapi import HTTPException

from app.domain.enums.user_role import UserRole


# Bitta paymentni olish use case
class GetPaymentUseCase:

    # Constructor
    def __init__(self, payment_repository, trip_repository) -> None:

        # Payment repository
        self.payment_repository = payment_repository

        # Trip repository
        self.trip_repository = trip_repository

    # Paymentni olish
    def execute(self, payment_id, current_user):

        # Paymentni olamiz
        payment = self.payment_repository.get_by_id(payment_id)

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        # Admin barcha paymentlarni ko'ra oladi
        if current_user.role == UserRole.admin:
            return payment

        # Paymentga bog'langan tripni olamiz
        trip = self.trip_repository.get_by_id(payment.trip_id)

        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found",
            )

        # Passenger o'z paymentini ko'ra oladi
        if (
            current_user.role == UserRole.passenger
            and trip.passenger_id == current_user.id
        ):
            return payment

        # Driver o'z paymentini ko'ra oladi
        if (
            current_user.role == UserRole.driver
            and trip.driver_id == current_user.id
        ):
            return payment

        # Access taqiqlangan
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )