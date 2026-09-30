from src.infrastructure.config.settings import MigrationSettings
from src.infrastructure.database.source_sql_server_repository import SourceSqlServerRepository
from src.infrastructure.database.target_sql_server_repository import TargetSqlServerRepository
from src.infrastructure.id_mapping.in_memory_id_mapper import InMemoryIdMapper
from src.infrastructure.logging.console_reporter import ConsoleMigrationReporter

from src.application.use_cases.migrate_users_use_case import MigrateUsersUseCase
from src.application.use_cases.migrate_companies_use_case import MigrateCompaniesUseCase
from src.application.use_cases.migrate_students_use_case import MigrateStudentsUseCase
from src.application.use_cases.migrate_jobs_use_case import MigrateJobsUseCase
from src.application.use_cases.migrate_curriculum_use_case import MigrateCurriculumUseCase
from src.application.use_cases.migrate_applications_use_case import MigrateApplicationsUseCase
from src.application.use_cases.migrate_notifications_use_case import MigrateNotificationsUseCase
from src.application.use_cases.migrate_logs_use_case import MigrateLogsUseCase
from src.application.use_cases.run_full_migration_use_case import RunFullMigrationUseCase

from src.domain.ports.inbound.run_full_migration_port import RunFullMigrationPort
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class Container:
    """
    Container de Injeção de Dependências (IoC).
    Resolve interfaces para suas respectivas implementações de infraestrutura e aplicação,
    mantendo desacoplamento total conforme os princípios SOLID.
    """

    def __init__(self, settings: MigrationSettings | None = None):
        self.settings = settings or MigrationSettings.load_from_env()

        # Outbound Adapters
        self.reporter: MigrationReporterPort = ConsoleMigrationReporter()
        self.id_mapper: IdMappingPort = InMemoryIdMapper()
        self.source_db: SourceDatabasePort = SourceSqlServerRepository(self.settings.source_db)
        self.target_db: TargetDatabasePort = TargetSqlServerRepository(self.settings.target_db)

        # Inbound Use Cases
        self.migrate_users_use_case = MigrateUsersUseCase(
            source_db=self.source_db,
            target_db=self.target_db,
            id_mapper=self.id_mapper,
            reporter=self.reporter,
            omit_recruiters=self.settings.omit_recruiters,
            batch_size=self.settings.batch_size,
        )

        self.migrate_companies_use_case = MigrateCompaniesUseCase(
            source_db=self.source_db,
            target_db=self.target_db,
            id_mapper=self.id_mapper,
            reporter=self.reporter,
            batch_size=self.settings.batch_size,
        )

        self.migrate_students_use_case = MigrateStudentsUseCase(
            source_db=self.source_db,
            target_db=self.target_db,
            id_mapper=self.id_mapper,
            reporter=self.reporter,
            batch_size=self.settings.batch_size,
        )

        self.migrate_jobs_use_case = MigrateJobsUseCase(
            source_db=self.source_db,
            target_db=self.target_db,
            id_mapper=self.id_mapper,
            reporter=self.reporter,
            batch_size=self.settings.batch_size,
        )

        self.migrate_curriculum_use_case = MigrateCurriculumUseCase(
            source_db=self.source_db,
            target_db=self.target_db,
            id_mapper=self.id_mapper,
            reporter=self.reporter,
            batch_size=self.settings.batch_size,
        )

        self.migrate_applications_use_case = MigrateApplicationsUseCase(
            source_db=self.source_db,
            target_db=self.target_db,
            id_mapper=self.id_mapper,
            reporter=self.reporter,
            batch_size=self.settings.batch_size,
        )

        self.migrate_notifications_use_case = MigrateNotificationsUseCase(
            source_db=self.source_db,
            target_db=self.target_db,
            id_mapper=self.id_mapper,
            reporter=self.reporter,
            batch_size=self.settings.batch_size,
        )

        self.migrate_logs_use_case = MigrateLogsUseCase(
            source_db=self.source_db,
            target_db=self.target_db,
            id_mapper=self.id_mapper,
            reporter=self.reporter,
            batch_size=self.settings.batch_size,
        )

        self.migration_orchestrator: RunFullMigrationPort = RunFullMigrationUseCase(
            migrate_users=self.migrate_users_use_case,
            migrate_companies=self.migrate_companies_use_case,
            migrate_students=self.migrate_students_use_case,
            migrate_jobs=self.migrate_jobs_use_case,
            migrate_curriculum=self.migrate_curriculum_use_case,
            migrate_applications=self.migrate_applications_use_case,
            migrate_notifications=self.migrate_notifications_use_case,
            migrate_logs=self.migrate_logs_use_case,
            reporter=self.reporter,
        )

    def get_orchestrator(self) -> RunFullMigrationPort:
        return self.migration_orchestrator

    def get_source_db(self) -> SourceDatabasePort:
        return self.source_db

    def get_target_db(self) -> TargetDatabasePort:
        return self.target_db

    def get_reporter(self) -> MigrationReporterPort:
        return self.reporter
