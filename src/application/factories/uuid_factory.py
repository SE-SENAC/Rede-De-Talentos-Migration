import uuid
from uuid import UUID


class UUIDFactory:
    """
    Fábrica de UUIDs determinísticos baseados no padrão UUIDv5 (SHA-1)
    ou UUIDv4 aleatório. Garante reprodutibilidade exata nas migrações.
    """
    NAMESPACE_SENAC = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # UUIDv5 DNS base

    @classmethod
    def create_deterministic(cls, entity_type: str, legacy_id: any) -> UUID:
        """
        Gera um UUIDv5 determinístico a partir do tipo da entidade e do ID legado.
        Se legacy_id já for um UUID válido, preserva o UUID original.
        """
        if legacy_id is None:
            return uuid.uuid4()

        raw_str = str(legacy_id).strip()

        # Se já é um UUID válido, reutiliza
        try:
            return UUID(raw_str)
        except (ValueError, AttributeError):
            pass

        key = f"senac-migration:{entity_type.lower()}:{raw_str}"
        return uuid.uuid5(cls.NAMESPACE_SENAC, key)

    @classmethod
    def create_random(cls) -> UUID:
        """Gera um novo UUIDv4."""
        return uuid.uuid4()

