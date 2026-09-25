from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class StepResultDTO:
    step_name: str
    extracted: int = 0
    migrated: int = 0
    skipped: int = 0
    errors: int = 0
    duration_seconds: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MigrationSummaryDTO:
    started_at: datetime
    finished_at: datetime | None = None
    dry_run: bool = False
    total_extracted: int = 0
    total_migrated: int = 0
    total_skipped: int = 0
    total_errors: int = 0
    steps: Dict[str, StepResultDTO] = field(default_factory=dict)

    @property
    def total_duration_seconds(self) -> float:
        if not self.finished_at:
            return 0.0
        return (self.finished_at - self.started_at).total_seconds()

