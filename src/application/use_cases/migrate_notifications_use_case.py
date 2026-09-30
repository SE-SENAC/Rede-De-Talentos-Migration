import time
from typing import Dict, Any, List

from src.application.dtos.legacy_dtos import LegacyNotificationDTO
from src.application.factories.entity_factory import EntityFactory
from src.domain.entities.notification import NotificationEntity
from src.domain.ports.inbound.step_migration_port import StepMigrationPort
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class MigrateNotificationsUseCase(StepMigrationPort):
    """
    Caso de Uso: Migração de Notificações para a tabela notification.
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
        self.reporter.log_step_start("Notificações -> [notification]")

        extracted_count = 0
        migrated_count = 0
        skipped_count = 0
        errors_count = 0

        notifications: List[NotificationEntity] = []

        def flush_notifications_batch():
            nonlocal migrated_count, errors_count
            if dry_run or not notifications:
                return
            record_count = len(notifications)
            try:
                saved = self.target_db.save_notifications(notifications)
                migrated_count += saved
                errors_count += record_count - saved
                if saved < record_count:
                    self.reporter.log_error(
                        f"{record_count - saved} notificacoes nao puderam ser persistidas."
                    )
            except Exception as e:
                errors_count += record_count
                self.reporter.log_error(f"Erro ao persistir notificacoes: {e}", e)
            finally:
                notifications.clear()

        for row in self.source_db.get_notifications():
            extracted_count += 1
            notif_legacy_id = (
                row.get("NotificaoId")
                or row.get("NotificaoId")
                or row.get("NotificacaoId")
                or row.get("NotificationId")
                or row.get("Id")
                or row.get("_pk")
            )
            try:
                dto = LegacyNotificationDTO(
                    id=notif_legacy_id,
                    usuario_id=row.get("UsuarioId"),
                    titulo=row.get("Titulo"),
                    conteudo=row.get("Conteudo"),
                    tipo=row.get("Tipo"),
                    is_read=row.get("isRead"),
                    status=row.get("status"),
                    data_criacao=row.get("DataCriacao"),
                    updated_at=row.get("updatedAt"),
                    metadata=row.get("metadata"),
                )

                notif_entity = EntityFactory.create_notification_from_legacy(dto, self.id_mapper)
                if not notif_entity:
                    skipped_count += 1
                    continue

                notifications.append(notif_entity)
                if dry_run:
                    migrated_count += 1

                if len(notifications) >= self.batch_size:
                    flush_notifications_batch()

            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar notificação {notif_legacy_id}: {e}", e)

        flush_notifications_batch()

        duration = time.time() - start_time
        self.reporter.log_step_completed("Notificações", extracted_count, migrated_count, skipped_count)

        return {
            "step": "notifications",
            "extracted": extracted_count,
            "migrated": migrated_count,
            "skipped": skipped_count,
            "errors": errors_count,
            "duration_seconds": duration,
        }
