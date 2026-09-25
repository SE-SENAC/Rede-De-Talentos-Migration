from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    value: str

    @classmethod
    def create(cls, raw: str | None) -> "Email":
        if not raw:
            return cls("")
        cleaned = str(raw).strip().lower()
        return cls(cleaned)

    @property
    def is_valid_format(self) -> bool:
        return "@" in self.value and "." in self.value.split("@")[-1]

    def __str__(self) -> str:
        return self.value

