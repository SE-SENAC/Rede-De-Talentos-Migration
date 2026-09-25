from typing import Dict, Any, Callable
from uuid import UUID
from src.domain.ports.outbound.id_mapping_port import IdMappingPort


class InMemoryIdMapper(IdMappingPort):
    """
    Implementação em memória do mapeador de IDs legados para novos UUIDs.
    Pode ser estendido para persistência de checkpoint se necessário.
    """

    def __init__(self):
        self._registry: Dict[str, Dict[Any, UUID]] = {}

    def set_mapping(self, entity_type: str, legacy_id: Any, new_id: UUID) -> None:
        etype = entity_type.lower()
        if etype not in self._registry:
            self._registry[etype] = {}
        self._registry[etype][legacy_id] = new_id

    def get_mapping(self, entity_type: str, legacy_id: Any) -> UUID | None:
        etype = entity_type.lower()
        if etype not in self._registry:
            return None
        return self._registry[etype].get(legacy_id)

    def get_or_create(self, entity_type: str, legacy_id: Any, generator_func: Callable[[], UUID]) -> UUID:
        existing = self.get_mapping(entity_type, legacy_id)
        if existing:
            return existing

        new_uuid = generator_func()
        self.set_mapping(entity_type, legacy_id, new_uuid)
        return new_uuid

    def has_mapping(self, entity_type: str, legacy_id: Any) -> bool:
        etype = entity_type.lower()
        return etype in self._registry and legacy_id in self._registry[etype]

