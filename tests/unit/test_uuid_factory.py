import uuid
from src.application.factories.uuid_factory import UUIDFactory


def test_uuid_factory_deterministic():
    uuid1 = UUIDFactory.create_deterministic("user", 42)
    uuid2 = UUIDFactory.create_deterministic("user", 42)
    assert uuid1 == uuid2

    # Entidade diferente deve produzir UUID diferente
    uuid_company = UUIDFactory.create_deterministic("company", 42)
    assert uuid1 != uuid_company

    # ID diferente deve produzir UUID diferente
    uuid3 = UUIDFactory.create_deterministic("user", 43)
    assert uuid1 != uuid3


def test_uuid_factory_preserves_valid_uuid():
    original = uuid.uuid4()
    preserved = UUIDFactory.create_deterministic("user", str(original))
    assert preserved == original

