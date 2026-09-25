from dataclasses import dataclass
from uuid import UUID
from src.domain.value_objects.phone_number import PhoneNumber


@dataclass(frozen=True)
class PhoneEntity:
    id: UUID
    contact_id: UUID
    phone: PhoneNumber

