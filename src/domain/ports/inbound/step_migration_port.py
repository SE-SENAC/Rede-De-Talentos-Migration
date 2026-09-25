from abc import ABC, abstractmethod
from typing import Any, Dict


class StepMigrationPort(ABC):
    """
    Porta de entrada para casos de uso que executam etapas de migração.
    """

    @abstractmethod
    def execute(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Executa a etapa de migração.
        Retorna dicionário com métricas: {'extracted': int, 'migrated': int, 'skipped': int}.
        """
        pass

