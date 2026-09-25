from dataclasses import dataclass
from datetime import datetime, date
from typing import Any


@dataclass(frozen=True)
class LegacyUserDTO:
    id: Any
    nome: str
    email: str
    senha: str
    tipo_usuario: str
    avatar_url: str | None = None
    data_criacao: datetime | None = None
    data_atualizacao: datetime | None = None
    status: Any = None


@dataclass(frozen=True)
class LegacyAdminDTO:
    id: Any
    login: str
    senha: str
    email: str
    tipo_admin: str
    status: Any = None
    data_criacao: datetime | None = None
    data_atualizacao: datetime | None = None
    ferias_inicio: datetime | None = None
    ferias_fim: datetime | None = None
    arquivado: bool | None = None


@dataclass(frozen=True)
class LegacyCompanyDTO:
    id: Any
    nome_fantasia: str | None
    razao_social: str | None
    cnpj: str
    telefone: str | None
    logradouro: str | None
    numero: Any | None
    complemento: str | None
    bairro: str | None
    cidade: str | None
    estado: str | None
    cep: str | None
    parceira_senac: bool | None
    logo_url: str | None
    website_url: str | None
    usuario_id: Any
    descricao: str | None
    status_aprovacao: str | None
    data_criacao: datetime | None
    data_atualizacao: datetime | None
    email_contato: str | None
    mostrar_email_contato: bool | None
    mostrar_telefone_contato: bool | None


@dataclass(frozen=True)
class LegacyRecruiterDTO:
    id: Any
    usuario_id: Any
    nome: str
    email: str
    telefone: str | None
    cpf: str | None
    empresa_id: Any
    status: Any = None
    data_criacao: datetime | None = None
    data_atualizacao: datetime | None = None


@dataclass(frozen=True)
class LegacyStudentDTO:
    id: Any
    nome: str
    cpf: str
    usuario_id: Any
    pcd: bool | None
    tipo_pcd: str | None
    escolaridade: str | None
    aluno_id_sig: str | None
    data_criacao: datetime | None
    data_atualizacao: datetime | None
    linkedin_url: str | None
    portfolio: str | None


@dataclass(frozen=True)
class LegacyVagaDTO:
    id: Any
    empresa_id: Any
    titulo: str
    descricao: str | None
    data_publicacao: datetime | None
    data_atualizacao: datetime | None
    data_encerramento: datetime | None
    segmento: str | None
    modalidade: str | None
    tipo: str | None
    pcd: bool | None
    escolaridade_minima: str | None
    idade_minima: int | None
    status: str | None
    salario: float | None
    salario_maximo: float | None
    beneficios: str | None
    recrutador_id: Any | None
    mostrar_email_contato: bool | None
    mostrar_salario: bool | None
    mostrar_telefone_contato: bool | None
    quantidade_vagas: int | None


@dataclass(frozen=True)
class LegacyExperienceDTO:
    id: Any
    aluno_id: Any
    cargo: str | None
    empresa: str | None
    data_inicio: date | None
    data_fim: date | None
    atual: bool | None
    descricao: str | None
    data_criacao: datetime | None
    data_atualizacao: datetime | None


@dataclass(frozen=True)
class LegacyLanguageDTO:
    id: Any
    aluno_id: Any
    idioma: str
    fluencia: str | None
    data_criacao: datetime | None
    data_atualizacao: datetime | None


@dataclass(frozen=True)
class LegacyQualificationDTO:
    id: Any
    aluno_id: Any
    curso: str
    instituicao: str
    data_inicio: date | None
    data_fim: date | None
    atual: bool | None
    descricao: str | None
    data_criacao: datetime | None
    data_atualizacao: datetime | None


@dataclass(frozen=True)
class LegacyInscricaoDTO:
    id: Any
    vaga_id: Any
    aluno_id: Any
    data_inscricao: datetime | None
    data_atualizacao: datetime | None
    status: str | None


@dataclass(frozen=True)
class LegacyNotificationDTO:
    id: Any
    usuario_id: Any
    titulo: str
    conteudo: str
    tipo: str | None
    is_read: bool | None
    status: str | None
    data_criacao: datetime | None
    updated_at: datetime | None
    metadata: str | None = None


@dataclass(frozen=True)
class LegacyLogAdminDTO:
    id: Any
    admin_id: Any
    nome_de_usuario: str | None
    tipo_acao: str | None
    descricao: str | None
    ipv4: str | None
    user_agent: str | None
    data_criacao: datetime | None


@dataclass(frozen=True)
class LegacyLogJobDTO:
    id: Any
    job_id: Any
    acao: str | None
    motivo: str | None
    data_criacao: datetime | None
    tipo_usuario: str | None
    usuario_id: Any
    admin_id: Any


@dataclass(frozen=True)
class LegacyLogUserDTO:
    id: Any
    usuario_id: Any
    email: str | None
    tipo_acao: str | None
    descricao: str | None
    ipv4: str | None
    user_agent: str | None
    data_criacao: datetime | None

