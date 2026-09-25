from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from src.domain.enums.application_enums import ApplicationStatus


@dataclass(frozen=True)
class ApplicationEntity:
    id: UUID
    job_id: UUID
    student_id: UUID
    applied_at: datetime
    status: ApplicationStatus = ApplicationStatus.APPLIED
    status_changed_at: datetime | None = None

