from enum import StrEnum


class ConvStatus(StrEnum):
    active = "ACTIVE"
    waiting_confirmation = "WAITING_CONFIRMATION"
    escalated = "ESCALATED"  # Devredildi
    resolved = "RESOLVED"  # Çözüldü


class Priority(StrEnum):
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    urgent = "URGENT"  # Acil


class TicketStatus(StrEnum):
    open = "OPEN"
    in_progress = "IN_PROGRESS"
    resolved = "RESOLVED"  # Çözüldü
