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