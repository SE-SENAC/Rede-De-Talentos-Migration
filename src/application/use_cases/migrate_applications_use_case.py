import time
from typing import Dict, Any, List

from src.application.dtos.legacy_dtos import LegacyInscricaoDTO
from src.application.factories.entity_factory import EntityFactory
from src.domain.entities.application import ApplicationEntity
from src.domain.ports.inbound.step_migration_port import StepMigrationPort
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class MigrateApplicationsUseCase(StepMigrationPort):
    """
    Caso de Uso: Migração de Inscrições para a tabela applications (funil seletivo).
    Vincula o egresso (student_id) à vaga corporativa (job_id).
    """

    def __init__(
        self,
        source_db: SourceDatabasePort,
        target_db: TargetDatabasePort,
        id_mapper: IdMappingPort,
        reporter: MigrationReporterPort,
        batch_size: int = 250
    ):
        self.source_db = source_db
        self.target_db = target_db
        self.id_mapper = id_mapper
        self.reporter = reporter
        self.batch_size = batch_size

    def execute(self, dry_run: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        self.reporter.log_step_start("Inscrições -> [applications]")

        extracted_count = 0
        migrated_count = 0
        skipped_count = 0
        errors_count = 0

        applications: List[ApplicationEntity] = []
        seen_pairs = set()

        def flush_applications_batch():
            nonlocal migrated_count, errors_count
            if not dry_run and applications:
                try:
                    saved = self.target_db.save_applications(applications)
                    migrated_count += saved
                    if saved < len(applications):
                        diff = len(applications) - saved
                        errors_count += diff
                        self.reporter.log_error(f"{diff} inscrições não puderam ser persistidas no banco de destino.")
                except Exception as e:
                    errors_count += len(applications)
                    self.reporter.log_error(f"Erro ao salvar lote de inscrições: {e}", e)
                finally:
                    applications.clear()
            elif dry_run and applications:
                migrated_count += len(applications)
                applications.clear()

        for row in self.source_db.get_inscricoes():
            extracted_count += 1
            inscricao_legacy_id = (
                row.get("InscricaoId")
                or row.get("Id")
                or row.get("_pk")
                or f"{row.get('VagaId')}_{row.get('AlunoId')}"
            )
            try:
                dto = LegacyInscricaoDTO(
                    id=inscricao_legacy_id,
                    vaga_id=row.get("VagaId"),
                    aluno_id=row.get("AlunoId"),
                    data_inscricao=row.get("DataInscricao"),
                    data_atualizacao=row.get("DataAtualizacao"),
                    status=row.get("Status"),
                )

                app_entity = EntityFactory.create_application_from_legacy(dto, self.id_mapper)
                if not app_entity:
                    skipped_count += 1
                    continue

                pair = (str(app_entity.job_id), str(app_entity.student_id))
                if pair in seen_pairs:
                    skipped_count += 1
                    continue

                seen_pairs.add(pair)
                applications.append(app_entity)

                if len(applications) >= self.batch_size:
                    flush_applications_batch()

            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar inscrição {inscricao_legacy_id}: {e}", e)

        flush_applications_batch()

        duration = time.time() - start_time
        self.reporter.log_step_completed("Candidaturas e Inscrições", extracted_count, migrated_count, skipped_count)

        return {
            "step": "applications",
            "extracted": extracted_count,
            "migrated": migrated_count,
            "skipped": skipped_count,
            "errors": errors_count,
            "duration_seconds": duration,
        }
