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
    FUNDAMENTAL_INCOMPLETO = "FUNDAMENTAL_INCOMPLETO"
    FUNDAMENTAL_COMPLETO = "FUNDAMENTAL_COMPLETO"
    MEDIO_INCOMPLETO = "MEDIO_INCOMPLETO"
    MEDIO_COMPLETO = "MEDIO_COMPLETO"
    TECNICO_INCOMPLETO = "TECNICO_INCOMPLETO"
    TECNICO_COMPLETO = "TECNICO_COMPLETO"
    SUPERIOR_INCOMPLETO = "SUPERIOR_INCOMPLETO"
    SUPERIOR_COMPLETO = "SUPERIOR_COMPLETO"
    POS_GRADUACAO = "POS_GRADUACAO"
    MESTRADO = "MESTRADO"
    DOUTORADO = "DOUTORADO"
    NAO_INFORMADO = "NAO_INFORMADO"

    # Aliases em inglês para retrocompatibilidade
    INCOMPLETE_BASIC_EDUCATION = "FUNDAMENTAL_INCOMPLETO"
    COMPLETE_BASIC_EDUCATION = "FUNDAMENTAL_COMPLETO"
    INCOMPLETE_HIGH_SCHOOL = "MEDIO_INCOMPLETO"
    COMPLETE_HIGH_SCHOOL = "MEDIO_COMPLETO"
    INCOMPLETE_TECHNICAL_EDUCATION = "TECNICO_INCOMPLETO"
    COMPLETE_TECHNICAL_EDUCATION = "TECNICO_COMPLETO"
    INCOMPLETE_HIGHER_EDUCATION = "SUPERIOR_INCOMPLETO"
    COMPLETE_HIGHER_EDUCATION = "SUPERIOR_COMPLETO"
    POSTGRADUATE_DEGREE = "POS_GRADUACAO"
    MASTER_DEGREE = "MESTRADO"
    DOUTORADO_DEGREE = "DOUTORADO"
    DOCTORATE_DEGREE = "DOUTORADO"
    UNKNOWN = "NAO_INFORMADO"

    @classmethod
    def from_legacy(cls, education: any) -> "JobEducation":
        if not education:
            return cls.NAO_INFORMADO
        cleaned = str(education).strip().upper().replace(" ", "_")
        mapping = {
            "FUNDAMENTAL_INCOMPLETO": cls.FUNDAMENTAL_INCOMPLETO,
            "FUNDAMENTAL_COMPLETO": cls.FUNDAMENTAL_COMPLETO,
            "MEDIO_INCOMPLETO": cls.MEDIO_INCOMPLETO,
            "MÉDIO_INCOMPLETO": cls.MEDIO_INCOMPLETO,
            "MEDIO_COMPLETO": cls.MEDIO_COMPLETO,
            "MÉDIO_COMPLETO": cls.MEDIO_COMPLETO,
            "TECNICO_INCOMPLETO": cls.TECNICO_INCOMPLETO,
            "TÉCNICO_INCOMPLETO": cls.TECNICO_INCOMPLETO,
            "TECNICO_COMPLETO": cls.TECNICO_COMPLETO,
            "TÉCNICO_COMPLETO": cls.TECNICO_COMPLETO,
            "SUPERIOR_INCOMPLETO": cls.SUPERIOR_INCOMPLETO,
            "SUPERIOR_COMPLETO": cls.SUPERIOR_COMPLETO,
            "POS_GRADUACAO": cls.POS_GRADUACAO,
            "PÓS_GRADUAÇÃO": cls.POS_GRADUACAO,
            "MESTRADO": cls.MESTRADO,
            "DOUTORADO": cls.DOUTORADO,
            "NAO_INFORMADO": cls.NAO_INFORMADO,
            "NÃO_INFORMADO": cls.NAO_INFORMADO,
            "INCOMPLETE_BASIC_EDUCATION": cls.FUNDAMENTAL_INCOMPLETO,
            "COMPLETE_BASIC_EDUCATION": cls.FUNDAMENTAL_COMPLETO,
            "INCOMPLETE_HIGH_SCHOOL": cls.MEDIO_INCOMPLETO,
            "COMPLETE_HIGH_SCHOOL": cls.MEDIO_COMPLETO,
            "INCOMPLETE_TECHNICAL_EDUCATION": cls.TECNICO_INCOMPLETO,
            "COMPLETE_TECHNICAL_EDUCATION": cls.TECNICO_COMPLETO,
            "INCOMPLETE_HIGHER_EDUCATION": cls.SUPERIOR_INCOMPLETO,
            "COMPLETE_HIGHER_EDUCATION": cls.SUPERIOR_COMPLETO,
            "POSTGRADUATE_DEGREE": cls.POS_GRADUACAO,
            "MASTER_DEGREE": cls.MESTRADO,
            "DOCTORATE_DEGREE": cls.DOUTORADO,
            "UNKNOWN": cls.NAO_INFORMADO,
        }
        for k, v in mapping.items():
            if k in cleaned:
                return v
        try:
            return cls(cleaned)
        except ValueError:
            return cls.NAO_INFORMADO

