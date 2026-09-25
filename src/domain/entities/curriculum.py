from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class ExperienceEntity:
    id: UUID
    user_id: UUID
    empresa: str | None
    cargo: str | None
    descricao: str | None
    data_inicio: date | None
    data_fim: date | None
    atual: bool
    criado_em: datetime
    atualizado_em: datetime


@dataclass(frozen=True)
class LanguageEntity:
    id: UUID
    user_id: UUID
    idioma: str
    nivel: str
    criado_em: datetime
    atualizado_em: datetime


@dataclass(frozen=True)
class QualificationEntity:
    id: UUID
    user_id: UUID
    titulo: str | None
    curso: str
    instituicao: str
    descricao: str | None
    data_inicio: date | None
    data_fim: date | None
    em_andamento: bool
    criado_em: datetime
    atualizado_em: datetime

