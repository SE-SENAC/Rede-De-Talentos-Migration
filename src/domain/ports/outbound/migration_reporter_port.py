from abc import ABC, abstractmethod
from typing import Dict, Any


class MigrationReporterPort(ABC):
    """
    Porta de saída para emissão de logs, relatórios e progresso da migração.
    """

    @abstractmethod
    def log_info(self, message: str) -> None:
        pass

    @abstractmethod
    def log_warning(self, message: str) -> None:
        pass

    @abstractmethod
    def log_error(self, message: str, error: Exception | None = None) -> None:
        pass

    @abstractmethod
    def log_step_start(self, step_name: str) -> None:
        pass

    @abstractmethod
    def log_step_completed(self, step_name: str, extracted: int, inserted: int, skipped: int) -> None:
        pass

    @abstractmethod
    def log_summary(self, summary_data: Dict[str, Any]) -> None:
        pass

