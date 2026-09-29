from enum import Enum


class StudentTypePCD(str, Enum):
    VISUAL = "VISUAL"
    AUDITVE = "AUDITVE"
    PHYSICAL = "PHYSICAL"
    INTELLECTUAL = "INTELLECTUAL"
    MENTAL = "MENTAL"
    MULTIPLE = "MULTIPLE"
    DEAFNESS = "DEAFNESS"
    AUTISM_ESPECTRUM_DISORDER = "AUTISM_ESPECTRUM_DISORDER"
    NON = "NON"
    OTHER = "OTHER"

    @classmethod
    def from_legacy(cls, val: any) -> "StudentTypePCD":
        if not val:
            return cls.NON
        cleaned = str(val).strip().upper()
        if "VISUAL" in cleaned:
            return cls.VISUAL
        if "AUDITIV" in cleaned or "AUDITVE" in cleaned:
            return cls.AUDITVE
        if "FISIC" in cleaned or "FÍSIC" in cleaned or "PHYSICAL" in cleaned:
            return cls.PHYSICAL
        if "INTELECTUAL" in cleaned or "INTELLECTUAL" in cleaned:
            return cls.INTELLECTUAL
        if "MENTAL" in cleaned:
            return cls.MENTAL
        if "MULTIP" in cleaned or "MÚLTIP" in cleaned:
            return cls.MULTIPLE
        if "SURD" in cleaned or "DEAF" in cleaned:
            return cls.DEAFNESS
        if "AUTIS" in cleaned or "TEA" in cleaned:
            return cls.AUTISM_ESPECTRUM_DISORDER
        if "NAO" in cleaned or "NÃO" in cleaned or "NENHUM" in cleaned:
            return cls.NON
        return cls.OTHER


class StudentEducation(str, Enum):
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
    DOCTORATE_DEGREE = "DOUTORADO"
    UNKNOWN = "NAO_INFORMADO"

    @classmethod
    def from_legacy(cls, education: any) -> "StudentEducation":
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

