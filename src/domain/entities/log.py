from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class LogEntity:
    """
    Entidade unificada de auditoria (tabela log no novo schema).
    Recebe eventos migrados de LogAdmin, LogJob e LogUser.
    """
    id: UUID
    type_name: str
    created_at: datetime
    user_id: str | None = None
    user_name: str | None = None
    type_action: str | None = None
    description: str | None = None
    reason: str | None = None
    message: str | None = None
    ip_address: str | None = None
    updated_at: datetime | None = None

