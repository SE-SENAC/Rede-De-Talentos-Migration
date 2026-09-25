from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.domain.value_objects.email import Email


@dataclass(frozen=True)
class UserEntity:
    """
    Entidade pura de Usuário conforme nova especificação RBAC.
    """
    id: UUID
    name: str
    email: Email
    password: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    actived_at: datetime | None = None
    re_actived_at: datetime | None = None
    deactived_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    @property
    def is_admin(self) -> bool:
        return self.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)

