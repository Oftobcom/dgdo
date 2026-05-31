import enum


# Wallet transaction type enum
class WalletTransactionType(str, enum.Enum):

    # Wallet balance to'ldirish
    top_up = "top_up"

    # Payment transaction
    payment = "payment"

    # Refund transaction
    refund = "refund"

    # Driver earning transaction
    driver_earning = "driver_earning"

    # Pul yechib olish transaction
    withdrawal = "withdrawal"

    # Manual balance adjustment
    adjustment = "adjustment"