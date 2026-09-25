from enum import Enum


class ApprovalStatus(str, Enum):
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REPROVED = "REPROVED"

    @classmethod
    def from_legacy(cls, status: any) -> "ApprovalStatus":
        if status is None:
            return cls.UNDER_REVIEW

        cleaned = str(status).strip().upper()
        if cleaned in ("APPROVED", "APROVADO", "APROVADA", "1", "TRUE"):
            return cls.APPROVED
        if cleaned in ("REPROVED", "REPROVADO", "REJEITADO", "RECUSADO", "2"):
            return cls.REPROVED
        return cls.UNDER_REVIEW

