from typing import Generator, Dict, Any, List
from unittest.mock import MagicMock

from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.infrastructure.id_mapping.in_memory_id_mapper import InMemoryIdMapper
from src.application.use_cases.migrate_users_use_case import MigrateUsersUseCase
from src.application.use_cases.migrate_jobs_use_case import MigrateJobsUseCase
from src.application.use_cases.run_full_migration_use_case import RunFullMigrationUseCase


class MockSourceDatabase(SourceDatabasePort):
    def test_connection(self) -> bool:
        return True

    def get_row_counts(self) -> Dict[str, int]:
        return {"Usuario": 2, "Admin": 1, "Vaga": 1, "Recruiter": 1}

    def get_usuarios(self) -> Generator[Dict[str, Any], None, None]:
        yield {
            "Id": 1,
            "Nome": "Aluno Um",
            "Email": "aluno1@senac.br",
            "Senha": "hash",
            "TipoUsuario": "STUDENT",
            "Status": 1,
        }
        # Recrutador
        yield {
            "Id": 2,
            "Nome": "Recrutador Empresa",
            "Email": "recrutador@empresa.com",
            "Senha": "hash",
            "TipoUsuario": "RECRUITER",
            "Status": 1,
        }

    def get_admins(self) -> Generator[Dict[str, Any], None, None]:
        yield {
            "Id": 10,
            "Login": "admin_master",
            "Senha": "hash",
            "Email": "admin@senac.br",
            "TipoAdmin": "ADMIN",
            "Status": 1,
        }

    def get_empresas(self) -> Generator[Dict[str, Any], None, None]:
        yield from []

    def get_recruiters(self) -> Generator[Dict[str, Any], None, None]:
        yield {"Id": 2, "UsuarioId": 2, "EmpresaId": 100}

    def get_students(self) -> Generator[Dict[str, Any], None, None]:
        yield from []

    def get_vagas(self) -> Generator[Dict[str, Any], None, None]:
        yield {
            "Id": 50,
            "EmpresaId": 100,
            "Titulo": "Vaga Desenvolvedor",
            "Descricao": "Vaga Dev",
            "RecrutadorId": 2,
            "Status": "ABERTO",
            "Modalidade": "PRESENCIAL",
            "Tipo": "CLT",
            "QuantidadeVagas": 1,
        }

    def get_experiencias(self) -> Generator[Dict[str, Any], None, None]:
        yield from []

    def get_idiomas(self) -> Generator[Dict[str, Any], None, None]:
        yield from []

    def get_qualificacoes(self) -> Generator[Dict[str, Any], None, None]:
        yield from []

    def get_inscricoes(self) -> Generator[Dict[str, Any], None, None]:
        yield from []

    def get_notifications(self) -> Generator[Dict[str, Any], None, None]:
        yield from []

    def get_logs_admin(self) -> Generator[Dict[str, Any], None, None]:
        yield from []

    def get_logs_job(self) -> Generator[Dict[str, Any], None, None]:
        yield from []

    def get_logs_user(self) -> Generator[Dict[str, Any], None, None]:
        yield from []


class MockTargetDatabase(TargetDatabasePort):
    def __init__(self):
        self.saved_users = []
        self.saved_jobs = []

    def test_connection(self) -> bool:
        return True

    def get_row_counts(self) -> Dict[str, int]:
        return {}

    def save_users(self, users: List[Any]) -> int:
        self.saved_users.extend(users)
        return len(users)

    def save_addresses(self, addresses: List[Any]) -> int:
        return len(addresses)

    def save_contacts(self, contacts: List[Any]) -> int:
        return len(contacts)

    def save_phones(self, phones: List[Any]) -> int:
        return len(phones)

    def save_companies(self, companies: List[Any]) -> int:
        return len(companies)

    def save_students(self, students: List[Any]) -> int:
        return len(students)

    def save_jobs(self, jobs: List[Any]) -> int:
        self.saved_jobs.extend(jobs)
        return len(jobs)

    def save_experiences(self, experiences: List[Any]) -> int:
        return len(experiences)

    def save_languages(self, languages: List[Any]) -> int:
        return len(languages)

    def save_qualifications(self, qualifications: List[Any]) -> int:
        return len(qualifications)

    def save_applications(self, applications: List[Any]) -> int:
        return len(applications)

    def save_notifications(self, notifications: List[Any]) -> int:
        return len(notifications)

    def save_logs(self, logs: List[Any]) -> int:
        return len(logs)

    def clean_target_tables(self) -> None:
        self.saved_users.clear()
        self.saved_jobs.clear()


def test_migrate_users_use_case_skips_recruiter():
    source = MockSourceDatabase()
    target = MockTargetDatabase()
    id_mapper = InMemoryIdMapper()
    reporter = MagicMock()

    use_case = MigrateUsersUseCase(
        source_db=source,
        target_db=target,
        id_mapper=id_mapper,
        reporter=reporter,
        omit_recruiters=True,
    )

    result = use_case.execute(dry_run=False)
    assert result["extracted"] == 3  # 2 usuarios + 1 admin
    assert result["migrated"] == 2   # 1 aluno + 1 admin
    assert result["recruiters_skipped"] == 1
    assert len(target.saved_users) == 2


def test_migrate_jobs_use_case():
    source = MockSourceDatabase()
    target = MockTargetDatabase()
    id_mapper = InMemoryIdMapper()
    reporter = MagicMock()

    from src.application.factories.uuid_factory import UUIDFactory
    company_uuid = UUIDFactory.create_deterministic("company", 100)
    id_mapper.set_mapping("company", 100, company_uuid)

    use_case = MigrateJobsUseCase(
        source_db=source,
        target_db=target,
        id_mapper=id_mapper,
        reporter=reporter,
    )

    result = use_case.execute(dry_run=False)
    assert result["extracted"] == 1
    assert result["migrated"] == 1
    assert len(target.saved_jobs) == 1
    assert not hasattr(target.saved_jobs[0], "recrutador_id")


def test_full_orchestration_dry_run():
    source = MockSourceDatabase()
    target = MockTargetDatabase()
    id_mapper = InMemoryIdMapper()
    reporter = MagicMock()

    users_uc = MigrateUsersUseCase(source, target, id_mapper, reporter)
    jobs_uc = MigrateJobsUseCase(source, target, id_mapper, reporter)

    orchestrator = RunFullMigrationUseCase(
        migrate_users=users_uc,
        migrate_companies=MagicMock(execute=lambda dry_run: {"extracted": 0, "migrated": 0, "skipped": 0, "errors": 0}),
        migrate_students=MagicMock(execute=lambda dry_run: {"extracted": 0, "migrated": 0, "skipped": 0, "errors": 0}),
        migrate_jobs=jobs_uc,
        migrate_curriculum=MagicMock(execute=lambda dry_run: {"extracted": 0, "migrated": 0, "skipped": 0, "errors": 0}),
        migrate_applications=MagicMock(execute=lambda dry_run: {"extracted": 0, "migrated": 0, "skipped": 0, "errors": 0}),
        migrate_notifications=MagicMock(execute=lambda dry_run: {"extracted": 0, "migrated": 0, "skipped": 0, "errors": 0}),
        migrate_logs=MagicMock(execute=lambda dry_run: {"extracted": 0, "migrated": 0, "skipped": 0, "errors": 0}),
        reporter=reporter,
    )

    summary = orchestrator.execute(dry_run=True)
    assert summary["dry_run"] is True
    assert summary["total_extracted"] >= 3
    assert len(target.saved_users) == 0  # Em dry-run não salva nada


def test_seed_credentials_use_case():
    from src.application.use_cases.seed_credentials_use_case import SeedCredentialsUseCase
    target = MockTargetDatabase()
    id_mapper = InMemoryIdMapper()
    reporter = MagicMock()

    use_case = SeedCredentialsUseCase(
        target_db=target,
        id_mapper=id_mapper,
        reporter=reporter,
    )

    result = use_case.execute(dry_run=False)
    assert result["extracted"] == 4
    assert result["migrated"] == 4
    assert result["errors"] == 0
    assert len(target.saved_users) == 4

    roles = {u.role for u in target.saved_users}
    assert "ADMIN" in roles
    assert "SUPER_ADMIN" in roles
    assert "COMPANY" in roles
    assert "STUDENT" in roles
