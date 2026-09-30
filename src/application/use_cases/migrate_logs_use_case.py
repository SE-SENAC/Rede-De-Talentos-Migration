import time
from typing import Dict, Any, List

from src.application.dtos.legacy_dtos import (
    LegacyLogAdminDTO,
    LegacyLogJobDTO,
    LegacyLogUserDTO,
)
from src.application.factories.entity_factory import EntityFactory
from src.domain.entities.log import LogEntity
from src.domain.ports.inbound.step_migration_port import StepMigrationPort
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class MigrateLogsUseCase(StepMigrationPort):
    """
    Caso de Uso: Unificação e Migração de Logs de Auditoria (LogAdmin, LogJob, LogUser -> log).
    Consolida as três trilhas legadas na estrutura padrão do Apache Kafka / Trilha do novo schema.
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
        self.reporter.log_step_start("Logs de Auditoria -> [log] (Unificação)")

        extracted_count = 0
        migrated_count = 0
        skipped_count = 0
        errors_count = 0

        logs: List[LogEntity] = []

        def flush_logs_batch():
            nonlocal migrated_count, errors_count
            if dry_run or not logs:
                return
            record_count = len(logs)
            try:
                saved = self.target_db.save_logs(logs)
                migrated_count += saved
                errors_count += record_count - saved
                if saved < record_count:
                    self.reporter.log_error(f"{record_count - saved} logs nao puderam ser persistidos.")
            except Exception as e:
                errors_count += record_count
                self.reporter.log_error(f"Erro ao persistir lote de logs: {e}", e)
            finally:
                logs.clear()

        # 1. Logs de Administrador
        for row in self.source_db.get_logs_admin():
            extracted_count += 1
            log_id = row.get("LogAdminId") or row.get("Id") or row.get("_pk") or f"admin_{extracted_count}"
            try:
                dto = LegacyLogAdminDTO(
                    id=log_id,
                    admin_id=row.get("AdminId"),
                    nome_de_usuario=row.get("NomeDeUsuario"),
                    tipo_acao=row.get("TipoAcao"),
                    descricao=row.get("Descricao"),
                    ipv4=row.get("IPV4"),
                    user_agent=row.get("UserAgent"),
                    data_criacao=row.get("DataCriacao"),
                )
                entity = EntityFactory.create_log_from_admin(dto, self.id_mapper)
                logs.append(entity)
                if dry_run:
                    migrated_count += 1

                if len(logs) >= self.batch_size:
                    flush_logs_batch()
            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar log admin {log_id}: {e}", e)

        flush_logs_batch()

        # 2. Logs de Vaga (Job)
        for row in self.source_db.get_logs_job():
            extracted_count += 1
            log_id = row.get("JobActionLogId") or row.get("Id") or row.get("_pk") or f"job_{extracted_count}"
            try:
                dto = LegacyLogJobDTO(
                    id=log_id,
                    job_id=row.get("JobId"),
                    acao=row.get("Acao"),
                    motivo=row.get("Motivo"),
                    data_criacao=row.get("DataCriacao"),
                    tipo_usuario=row.get("TipoUsuario"),
                    usuario_id=row.get("UsuarioId"),
                    admin_id=row.get("AdminId"),
                )
                entity = EntityFactory.create_log_from_job(dto, self.id_mapper)
                logs.append(entity)
                if dry_run:
                    migrated_count += 1

                if len(logs) >= self.batch_size:
                    flush_logs_batch()
            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar log job {log_id}: {e}", e)

        flush_logs_batch()

        # 3. Logs de Usuário
        for row in self.source_db.get_logs_user():
            extracted_count += 1
            log_id = row.get("LogUserId") or row.get("Id") or row.get("_pk") or f"user_{extracted_count}"
            try:
                dto = LegacyLogUserDTO(
                    id=log_id,
                    usuario_id=row.get("UsuarioId"),
                    email=row.get("Email"),
                    tipo_acao=row.get("TipoAcao"),
                    descricao=row.get("Descricao"),
                    ipv4=row.get("IPV4"),
                    user_agent=row.get("UserAgent"),
                    data_criacao=row.get("DataCriacao"),
                )
                entity = EntityFactory.create_log_from_user(dto, self.id_mapper)
                logs.append(entity)
                if dry_run:
                    migrated_count += 1

                if len(logs) >= self.batch_size:
                    flush_logs_batch()
            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar log user {log_id}: {e}", e)

        flush_logs_batch()

        duration = time.time() - start_time
        self.reporter.log_step_completed("Logs de Auditoria Unificados", extracted_count, migrated_count, skipped_count)

        return {
            "step": "logs",
            "extracted": extracted_count,
            "migrated": migrated_count,
            "skipped": skipped_count,
            "errors": errors_count,
            "duration_seconds": duration,
        }
