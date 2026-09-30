from datetime import datetime
from typing import Dict, Any

from src.application.dtos.migration_dtos import MigrationSummaryDTO, StepResultDTO
from src.application.use_cases.migrate_users_use_case import MigrateUsersUseCase
from src.application.use_cases.migrate_companies_use_case import MigrateCompaniesUseCase
from src.application.use_cases.migrate_students_use_case import MigrateStudentsUseCase
from src.application.use_cases.migrate_jobs_use_case import MigrateJobsUseCase
from src.application.use_cases.migrate_curriculum_use_case import MigrateCurriculumUseCase
from src.application.use_cases.migrate_applications_use_case import MigrateApplicationsUseCase
from src.application.use_cases.migrate_notifications_use_case import MigrateNotificationsUseCase
from src.application.use_cases.migrate_logs_use_case import MigrateLogsUseCase
from src.domain.ports.inbound.run_full_migration_port import RunFullMigrationPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class RunFullMigrationUseCase(RunFullMigrationPort):
    """
    Orquestrador mestre da migração de dados.
    Coordena as etapas em estrita ordem de integridade referencial:
    1. Users (Usuários e Administradores)
    2. Companies (Empresas, Endereços, Contatos e Telefones)
    3. Students (Egressos Senac)
    4. Jobs (Vagas desvinculadas de Recruiter)
    5. Curriculum (Experiências, Idiomas e Qualificações)
    6. Applications (Inscrições)
    7. Notifications (Notificações)
    8. Logs (Trilha de auditoria consolidada)
    """

    def __init__(
        self,
        migrate_users: MigrateUsersUseCase,
        migrate_companies: MigrateCompaniesUseCase,
        migrate_students: MigrateStudentsUseCase,
        migrate_jobs: MigrateJobsUseCase,
        migrate_curriculum: MigrateCurriculumUseCase,
        migrate_applications: MigrateApplicationsUseCase,
        migrate_notifications: MigrateNotificationsUseCase,
        migrate_logs: MigrateLogsUseCase,
        reporter: MigrationReporterPort,
    ):
        self.steps_map = {
            "users": migrate_users,
            "companies": migrate_companies,
            "students": migrate_students,
            "jobs": migrate_jobs,
            "curriculum": migrate_curriculum,
            "applications": migrate_applications,
            "notifications": migrate_notifications,
            "logs": migrate_logs,
        }
        self.reporter = reporter

    def execute(self, dry_run: bool = False, specific_step: str | None = None) -> Dict[str, Any]:
        started_at = datetime.now()
        summary = MigrationSummaryDTO(
            started_at=started_at,
            dry_run=dry_run
        )

        steps_to_run = (
            [specific_step]
            if specific_step and specific_step in self.steps_map
            else list(self.steps_map.keys())
        )

        self.reporter.log_info(
            f"Iniciando processo de migração (Modo: {'DRY-RUN (Simulação)' if dry_run else 'PRODUÇÃO (Persistência real)'}) | "
            f"Etapas selecionadas: {', '.join(steps_to_run)}"
        )

        for step_name in steps_to_run:
            use_case = self.steps_map[step_name]
            result_dict = use_case.execute(dry_run=dry_run)

            step_dto = StepResultDTO(
                step_name=step_name,
                extracted=result_dict.get("extracted", 0),
                migrated=result_dict.get("migrated", 0),
                skipped=result_dict.get("skipped", 0),
                errors=result_dict.get("errors", 0),
                duration_seconds=result_dict.get("duration_seconds", 0.0),
                details=result_dict,
            )

            summary.steps[step_name] = step_dto
            summary.total_extracted += step_dto.extracted
            summary.total_migrated += step_dto.migrated
            summary.total_skipped += step_dto.skipped
            summary.total_errors += step_dto.errors

        summary.finished_at = datetime.now()

        summary_payload = {
            "dry_run": summary.dry_run,
            "started_at": summary.started_at.isoformat(),
            "finished_at": summary.finished_at.isoformat(),
            "duration_seconds": round(summary.total_duration_seconds, 2),
            "total_extracted": summary.total_extracted,
            "total_migrated": summary.total_migrated,
            "total_skipped": summary.total_skipped,
            "total_errors": summary.total_errors,
            "steps": {k: v.__dict__ for k, v in summary.steps.items()},
        }

        self.reporter.log_summary(summary_payload)
        return summary_payload
