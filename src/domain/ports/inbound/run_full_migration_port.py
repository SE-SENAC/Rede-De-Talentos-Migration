from abc import ABC, abstractmethod
from typing import Any, Dict


class RunFullMigrationPort(ABC):
    """
    Porta de entrada para execução da orquestração global da migração.
    """

    @abstractmethod
    def execute(self, dry_run: bool = False, specific_step: str | None = None) -> Dict[str, Any]:
        """
        Executa todas as etapas ou uma etapa específica.
        """
        pass

