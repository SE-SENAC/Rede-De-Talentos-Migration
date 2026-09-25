from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

    @classmethod
    def from_legacy(cls, legacy_status: any) -> "UserStatus":
        if legacy_status is None:
            return cls.ACTIVE

        if isinstance(legacy_status, bool):
            return cls.ACTIVE if legacy_status else cls.INACTIVE

        cleaned = str(legacy_status).strip().upper()
        if cleaned in ("1", "TRUE", "ACTIVE", "ATIVO", "A"):
            return cls.ACTIVE
        return cls.INACTIVE

