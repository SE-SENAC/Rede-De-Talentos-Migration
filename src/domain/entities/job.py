from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from src.domain.enums.job_enums import JobWorkMode, JobType, JobStatus, JobEducation


@dataclass(frozen=True)
class JobEntity:
    """
    Entidade pura de Vaga (job).
    IMPORTANTE: Recruiter foi descontinuado no novo schema.
    A vaga vincula-se diretamente à organização através de company_id.
    """
    id: UUID
    company_id: UUID
    title: str
    description: str | None = None
    segment: str | None = None
    work_mode: JobWorkMode = JobWorkMode.PRESENTIAL
    type: JobType = JobType.CLT
    pcd: bool = False
    minimum_education: JobEducation = JobEducation.UNKNOWN
    minimum_age: int | None = None
    status: JobStatus = JobStatus.OPEN
    salary: float | None = None
    maximum_salary: float | None = None
    number_of_openings: int = 1
    show_contact_email: bool = True
    show_contact_phone: bool = True
    show_salary: bool = True
    benefits: str | None = None
    skills: str | None = None
    closing_date: datetime | None = None
    published_at: datetime | None = None
    updated_at: datetime | None = None
