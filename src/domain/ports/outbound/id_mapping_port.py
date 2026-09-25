from abc import ABC, abstractmethod
from uuid import UUID


class IdMappingPort(ABC):
    """
    Porta de saída responsável por gerenciar e manter o mapeamento
    entre IDs legados (int/string) e novos UUIDs v4/v5 gerados.
    """

    @abstractmethod
    def set_mapping(self, entity_type: str, legacy_id: any, new_id: UUID) -> None:
        """Registra mapeamento para um tipo de entidade."""
        pass

    @abstractmethod
    def get_mapping(self, entity_type: str, legacy_id: any) -> UUID | None:
        """Recupera o UUID associado ao ID legado."""
        pass

    @abstractmethod
    def get_or_create(self, entity_type: str, legacy_id: any, generator_func) -> UUID:
        """Recupera ou gera de forma atômica um UUID determinístico."""
        pass

    @abstractmethod
    def has_mapping(self, entity_type: str, legacy_id: any) -> bool:
        """Verifica se existe mapeamento."""
        pass

