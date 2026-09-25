import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneNumber:
    ddi: str
    ddd: str
    number: str

    @classmethod
    def create(cls, raw: str | None, default_ddd: str = "79", default_ddi: str = "+55") -> "PhoneNumber":
        if not raw:
            return cls(ddi=default_ddi, ddd=default_ddd, number="000000000")

        digits = re.sub(r"\D", "", str(raw))
        if not digits:
            return cls(ddi=default_ddi, ddd=default_ddd, number="000000000")

        ddi = default_ddi
        if digits.startswith("55") and len(digits) in (12, 13):
            ddi = "+55"
            digits = digits[2:]

        if len(digits) >= 10:
            ddd = digits[:2]
            number = digits[2:]
        elif len(digits) in (8, 9):
            ddd = default_ddd
            number = digits
        else:
            ddd = default_ddd
            number = digits

        return cls(ddi=ddi, ddd=ddd, number=number[:20])

