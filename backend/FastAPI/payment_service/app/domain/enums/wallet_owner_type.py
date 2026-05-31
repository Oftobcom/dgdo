import enum


# Wallet owner type enum
class WalletOwnerType(str, enum.Enum):

    # Passenger wallet
    passenger = "passenger"

    # Driver wallet
    driver = "driver"