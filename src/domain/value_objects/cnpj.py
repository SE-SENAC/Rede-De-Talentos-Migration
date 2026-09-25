import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CNPJ:
    value: str

    @classmethod
    def create(cls, raw: str | None) -> "CNPJ":
        if not raw:
            return cls("")
        digits = re.sub(r"\D", "", str(raw))
        if len(digits) > 14:
            digits = digits[:14]
        elif len(digits) < 14 and digits:
            digits = digits.zfill(14)
        return cls(digits)

    @property
    def is_valid_format(self) -> bool:
        return len(self.value) == 14 and not (self.value == self.value[0] * 14)

    def __str__(self) -> str:
        return self.value

