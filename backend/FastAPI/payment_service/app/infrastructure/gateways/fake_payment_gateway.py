# Fake payment gateway classi
class FakePaymentGateway:

    # Payment authorize qilish
    def authorize(self, amount, currency, payment_method) -> dict:

        # Fake gateway response
        return {
            "ok": True,
            "gateway_status": "authorized",
        }

    # Payment capture qilish
    def capture(self, payment_id: str) -> dict:

        # Fake gateway response
        return {
            "ok": True,
            "gateway_status": "captured",
        }

    # Payment refund qilish
    def refund(self, payment_id: str) -> dict:

        # Fake gateway response
        return {
            "ok": True,
            "gateway_status": "refunded",
        }

    # Gateway statusni olish
    def fetch_status(self, local_status: str) -> dict:

        # Local status -> gateway status mapping
        mapping = {
            "pending": "authorized",
            "success": "captured",
            "failed": "refunded_or_failed",
        }

        # Fake gateway response
        return {
            "ok": True,
            "gateway_status": mapping.get(local_status, "unknown"),
        }