import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CPF:
    value: str

    @classmethod
    def create(cls, raw: str | None) -> "CPF":
        if not raw:
            return cls("")
        digits = re.sub(r"\D", "", str(raw))
        if len(digits) > 11:
            digits = digits[:11]
        elif len(digits) < 11 and digits:
            digits = digits.zfill(11)
        return cls(digits)

    @property
    def is_valid_format(self) -> bool:
        return len(self.value) == 11 and not (self.value == self.value[0] * 11)

    def __str__(self) -> str:
        return self.value

