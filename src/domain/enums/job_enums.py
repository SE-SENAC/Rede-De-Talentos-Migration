from enum import Enum


class JobWorkMode(str, Enum):
    PRESENTIAL = "PRESENTIAL"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"

    @classmethod
    def from_legacy(cls, mode: any) -> "JobWorkMode":
        if not mode:
            return cls.PRESENTIAL
        cleaned = str(mode).strip().upper()
        if "REMOTO" in cleaned or "REMOTE" in cleaned or "HOME" in cleaned:
            return cls.REMOTE
        if "HIBRIDO" in cleaned or "HÍBRIDO" in cleaned or "HYBRID" in cleaned:
            return cls.HYBRID
        return cls.PRESENTIAL


class JobType(str, Enum):
    CLT = "CLT"
    APPRENTICE = "APPRENTICE"
    INTERNSHIP = "INTERNSHIP"
    PJ = "PJ"
    TEMPORARY = "TEMPORARY"
    VOLUNTEER = "VOLUNTEER"

    @classmethod
    def from_legacy(cls, job_type: any) -> "JobType":
        if not job_type:
            return cls.CLT
        cleaned = str(job_type).strip().upper()
        if "ESTAGIO" in cleaned or "ESTÁGIO" in cleaned or "INTERN" in cleaned:
            return cls.INTERNSHIP
        if "APRENDIZ" in cleaned or "APPRENTICE" in cleaned:
            return cls.APPRENTICE
        if "PJ" in cleaned or "PESSOA JURIDICA" in cleaned:
            return cls.PJ
        if "TEMPORARIO" in cleaned or "TEMPORÁRIO" in cleaned or "TEMPORARY" in cleaned:
            return cls.TEMPORARY
        if "VOLUNT" in cleaned:
            return cls.VOLUNTEER
        return cls.CLT


class JobStatus(str, Enum):
    UNDER_REVIEW = "UNDER_REVIEW"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"

    @classmethod
    def from_legacy(cls, status: any) -> "JobStatus":
        if not status:
            return cls.OPEN
        cleaned = str(status).strip().upper()
        if cleaned in ("ABERTA", "ABERTO", "OPEN", "ATIVA", "ATIVO", "1"):
            return cls.OPEN
        if cleaned in ("ENCERRADA", "ENCERRADO", "FECHADA", "FECHADO", "CLOSED", "0"):
            return cls.CLOSED
        if cleaned in ("PREENCHIDA", "FILLED"):
            return cls.FILLED
        if cleaned in ("CANCELADA", "CANCELADO", "CANCELLED"):
            return cls.CANCELLED
        if cleaned in ("EM_ANALISE", "EM ANÁLISE", "UNDER_REVIEW", "PENDENTE"):
            return cls.UNDER_REVIEW
        return cls.OPEN


class JobEducation(str, Enum):
    INCOMPLETE_BASIC_EDUCATION = "INCOMPLETE_BASIC_EDUCATION"
    COMPLETE_BASIC_EDUCATION = "COMPLETE_BASIC_EDUCATION"
    INCOMPLETE_HIGH_SCHOOL = "INCOMPLETE_HIGH_SCHOOL"
    COMPLETE_HIGH_SCHOOL = "COMPLETE_HIGH_SCHOOL"
    INCOMPLETE_TECHNICAL_EDUCATION = "INCOMPLETE_TECHNICAL_EDUCATION"
    COMPLETE_TECHNICAL_EDUCATION = "COMPLETE_TECHNICAL_EDUCATION"
    INCOMPLETE_HIGHER_EDUCATION = "INCOMPLETE_HIGHER_EDUCATION"
    COMPLETE_HIGHER_EDUCATION = "COMPLETE_HIGHER_EDUCATION"
    POSTGRADUATE_DEGREE = "POSTGRADUATE_DEGREE"
    MASTER_DEGREE = "MASTER_DEGREE"
    DOCTORATE_DEGREE = "DOCTORATE_DEGREE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_legacy(cls, education: any) -> "JobEducation":
        if not education:
            return cls.UNKNOWN
        cleaned = str(education).strip().upper()
        mapping = {
            "FUNDAMENTAL_INCOMPLETO": cls.INCOMPLETE_BASIC_EDUCATION,
            "FUNDAMENTAL_COMPLETO": cls.COMPLETE_BASIC_EDUCATION,
            "MEDIO_INCOMPLETO": cls.INCOMPLETE_HIGH_SCHOOL,
            "MÉDIO_INCOMPLETO": cls.INCOMPLETE_HIGH_SCHOOL,
            "MEDIO_COMPLETO": cls.COMPLETE_HIGH_SCHOOL,
            "MÉDIO_COMPLETO": cls.COMPLETE_HIGH_SCHOOL,
            "TECNICO_INCOMPLETO": cls.INCOMPLETE_TECHNICAL_EDUCATION,
            "TÉCNICO_INCOMPLETO": cls.INCOMPLETE_TECHNICAL_EDUCATION,
            "TECNICO_COMPLETO": cls.COMPLETE_TECHNICAL_EDUCATION,
            "TÉCNICO_COMPLETO": cls.COMPLETE_TECHNICAL_EDUCATION,
            "SUPERIOR_INCOMPLETO": cls.INCOMPLETE_HIGHER_EDUCATION,
            "SUPERIOR_COMPLETO": cls.COMPLETE_HIGHER_EDUCATION,
            "POS_GRADUACAO": cls.POSTGRADUATE_DEGREE,
            "PÓS_GRADUAÇÃO": cls.POSTGRADUATE_DEGREE,
            "MESTRADO": cls.MASTER_DEGREE,
            "DOUTORADO": cls.DOCTORATE_DEGREE,
        }
        for k, v in mapping.items():
            if k in cleaned.replace(" ", "_"):
                return v
        try:
            return cls(cleaned)
        except ValueError:
            return cls.UNKNOWN

