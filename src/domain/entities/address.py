from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AddressEntity:
    id: UUID
    street: str
    number: int
    neighborhood: str
    city: str
    state: str
    zipcode: str
    complement: str | None = None
    latitude: float | None = None
    longitude: float | None = None

