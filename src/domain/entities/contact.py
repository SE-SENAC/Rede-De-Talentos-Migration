from dataclasses import dataclass
from uuid import UUID
from src.domain.value_objects.email import Email


@dataclass(frozen=True)
class ContactEntity:
    id: UUID
    email: Email
    show_email: bool = True
    show_phone: bool = True

