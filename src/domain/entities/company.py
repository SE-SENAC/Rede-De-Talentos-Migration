from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from src.domain.enums.approval_status import ApprovalStatus
from src.domain.value_objects.cnpj import CNPJ


@dataclass(frozen=True)
class CompanyEntity:
    id: UUID
    user_id: UUID
    cnpj: CNPJ
    legal_name: str
    description: str
    is_senac_partner: bool
    approval_status: ApprovalStatus
    address_id: UUID | None = None
    contact_id: UUID | None = None
    sector: str | None = None
    state_registration: str | None = None
    municipal_registration: str | None = None
    websiteurl: str | None = None
    logourl: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

