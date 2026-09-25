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
    def from_legacy(cls, education: any) -> "StudentEducation":
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

