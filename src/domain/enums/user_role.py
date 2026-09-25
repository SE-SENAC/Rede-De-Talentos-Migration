from enum import Enum


class UserRole(str, Enum):
    """
    Papéis de usuário permitidos no modelo RBAC do novo schema.
    Nota: RECRUITER foi descontinuado no novo schema.
    """
    STUDENT = "STUDENT"
    COMPANY = "COMPANY"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    INACTIVE = "INACTIVE"

    @classmethod
    def from_legacy(cls, legacy_role: str | None) -> "UserRole":
        if not legacy_role:
            return cls.INACTIVE

        cleaned = str(legacy_role).strip().upper()
        mapping = {
            "STUDENT": cls.STUDENT,
            "ALUNO": cls.STUDENT,
            "ESTUDANTE": cls.STUDENT,
            "COMPANY": cls.COMPANY,
            "EMPRESA": cls.COMPANY,
            "ADMIN": cls.ADMIN,
            "ADMINISTRADOR": cls.ADMIN,
            "SUPER_ADMIN": cls.SUPER_ADMIN,
            "SUPERADMIN": cls.SUPER_ADMIN,
            "RECRUITER": cls.INACTIVE,  # Recruiter descontinuado
            "RECRUTADOR": cls.INACTIVE,
            "INACTIVE": cls.INACTIVE,
            "INATIVO": cls.INACTIVE,
        }
        return mapping.get(cleaned, cls.INACTIVE)

