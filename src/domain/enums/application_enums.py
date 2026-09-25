from enum import Enum


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    IN_REVIEW = "IN_REVIEW"
    INTERVIEW = "INTERVIEW"
    HIRED = "HIRED"
    REJECTED = "REJECTED"
    ON_HOLD = "ON_HOLD"

    @classmethod
    def from_legacy(cls, status: any) -> "ApplicationStatus":
        if not status:
            return cls.APPLIED
        cleaned = str(status).strip().upper()
        if "HIRED" in cleaned or "CONTRATAD" in cleaned or "APROVAD" in cleaned:
            return cls.HIRED
        if "REJECT" in cleaned or "RECUSAD" in cleaned or "REPROVAD" in cleaned:
            return cls.REJECTED
        if "INTERVIEW" in cleaned or "ENTREVISTA" in cleaned:
            return cls.INTERVIEW
        if "REVIEW" in cleaned or "ANALISE" in cleaned or "ANÁLISE" in cleaned or "TRIAGEM" in cleaned:
            return cls.IN_REVIEW
        if "HOLD" in cleaned or "ESPERA" in cleaned:
            return cls.ON_HOLD
        return cls.APPLIED

