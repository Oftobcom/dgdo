import enum


# Wallet transaction status enum
class WalletTransactionStatus(str, enum.Enum):

    # Transaction hali tugallanmagan
    pending = "pending"

    # Transaction muvaffaqiyatli o'tgan
    success = "success"

    # Transaction muvaffaqiyatsiz bo'lgan
    failed = "failed"

    # Transaction bekor qilingan
    cancelled = "cancelled"