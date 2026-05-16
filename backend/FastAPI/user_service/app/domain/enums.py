import enum


# User role enum
class UserRole(str, enum.Enum):

    # Oddiy passenger user
    passenger = "passenger"

    # Driver user
    driver = "driver"

    # Admin user
    admin = "admin"


# Wallet owner type enum
class WalletOwnerType(str, enum.Enum):

    # Passenger wallet
    passenger = "passenger"

    # Driver wallet
    driver = "driver"

class WalletTransactionType(str, enum.Enum):
    top_up = "top_up"
    payment = "payment"
    refund = "refund"
    driver_earning = "driver_earning"
    withdrawal = "withdrawal"
    adjustment = "adjustment"


class WalletTransactionStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"