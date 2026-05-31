# Barcha paymentlarni olish use case
class GetAllPaymentsUseCase:

    # Constructor
    def __init__(self, payment_repository) -> None:

        # Payment repository
        self.payment_repository = payment_repository

    # Barcha paymentlarni olish
    def execute(self):

        return self.payment_repository.get_all()