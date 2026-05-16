import enum


# Payment status enum
class PaymentStatus(str, enum.Enum):

    # Payment hali tugallanmagan
    pending = "pending"

    # Payment muvaffaqiyatli o'tgan
    success = "success"

    # Payment muvaffaqiyatsiz bo'lgan
    failed = "failed"