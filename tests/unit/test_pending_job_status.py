from dataclasses import fields
from datetime import datetime, timedelta

import pytest

from src.application.dtos.legacy_dtos import LegacyVagaDTO
from src.application.factories.entity_factory import EntityFactory
from src.application.factories.uuid_factory import UUIDFactory
from src.domain.enums.job_enums import JobStatus
from src.infrastructure.id_mapping.in_memory_id_mapper import InMemoryIdMapper


@pytest.mark.parametrize(
    "legacy_status, expected",
    [
        ("analise", JobStatus.UNDER_REVIEW),
        (" análise ", JobStatus.UNDER_REVIEW),
        ("Em Análise", JobStatus.UNDER_REVIEW),
        ("EM_ANALISE", JobStatus.UNDER_REVIEW),
        ("PENDING_APPROVAL", JobStatus.UNDER_REVIEW),
        ("aguardando aprovação", JobStatus.UNDER_REVIEW),
        ("UNDER_REVIEW", JobStatus.UNDER_REVIEW),
        ("aprovada", JobStatus.OPEN),
        ("finalizada", JobStatus.CLOSED),
    ],
)
def test_legacy_job_status(legacy_status, expected):
    assert JobStatus.from_legacy(legacy_status) == expected


@pytest.mark.parametrize("closing_date", [datetime(2020, 1, 1), "2020-01-01", None])
def test_pending_job_keeps_approval_status_even_with_expired_deadline(closing_date):
    mapper = InMemoryIdMapper()
    mapper.set_mapping("company", 10, UUIDFactory.create_deterministic("company", 10))
    values = {field.name: None for field in fields(LegacyVagaDTO)}
    values.update(
        id=99,
        empresa_id=10,
        titulo="Vaga em análise",
        descricao="Vaga aguardando aprovação da instituição",
        status="analise",
        data_publicacao=datetime.now() - timedelta(days=30),
        data_encerramento=closing_date,
    )

    job = EntityFactory.create_job_from_legacy(LegacyVagaDTO(**values), mapper)

    assert job is not None
    assert job.status == JobStatus.UNDER_REVIEW
