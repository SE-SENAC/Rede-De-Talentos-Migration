from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class NotificationEntity:
    id: UUID
    user_id: UUID
    title: str
    content: str
    is_read: bool
    created_at: datetime
    type: str | None = None
    status: str | None = None
    updated_at: datetime | None = None

