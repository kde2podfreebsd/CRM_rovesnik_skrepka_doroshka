from enum import Enum

class ReservationStatus(str, Enum):
    RESERVED = "reserved"
    RESERVED_AND_NOTIFIED = "reserved_and_notified"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
