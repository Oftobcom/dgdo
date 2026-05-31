import enum


# Trip status enum
class TripStatus(str, enum.Enum):

    # Trip request yuborilgan
    requested = "requested"

    # Driver topilgan
    matched = "matched"

    # Driver tripni accept qilgan
    accepted = "accepted"

    # Trip tugallangan
    completed = "completed"

    # Trip bekor qilingan
    cancelled = "cancelled"