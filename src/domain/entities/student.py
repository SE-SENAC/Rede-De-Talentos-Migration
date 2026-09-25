from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from src.domain.enums.student_enums import StudentTypePCD, StudentEducation
from src.domain.value_objects.cpf import CPF


@dataclass(frozen=True)
class StudentEntity:
    id: UUID
    user_id: UUID
    cpf: CPF
    pcd: bool
    student_id_siga: str
    created_at: datetime
    updated_at: datetime
    contact_id: UUID | None = None
    avatar_url: str | None = None
    type_pcd: StudentTypePCD | None = None
    education: StudentEducation | None = None
    linkedin_url: str | None = None
    portfolio: str | None = None

