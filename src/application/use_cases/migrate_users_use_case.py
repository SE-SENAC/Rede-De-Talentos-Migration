import time
from typing import Dict, Any, List

from src.application.dtos.legacy_dtos import LegacyUserDTO, LegacyAdminDTO
from src.application.factories.entity_factory import EntityFactory
from src.domain.entities.user import UserEntity
from src.domain.ports.inbound.step_migration_port import StepMigrationPort
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class MigrateUsersUseCase(StepMigrationPort):
    """
    Caso de Uso: Migração de Usuários e Administradores para a tabela [user].
    Implementa:
    1. Unificação de [Usuario] e [Admin].
    2. Eliminação/tratamento seguro de contas legadas de Recruiter.
    3. Higienização e desduplicação de e-mails institucionais.
    """

    def __init__(
        self,
        source_db: SourceDatabasePort,
        target_db: TargetDatabasePort,
        id_mapper: IdMappingPort,
        reporter: MigrationReporterPort,
        omit_recruiters: bool = True,
        batch_size: int = 250
    ):
        self.source_db = source_db
        self.target_db = target_db
        self.id_mapper = id_mapper
        self.reporter = reporter
        self.omit_recruiters = omit_recruiters
        self.batch_size = batch_size

    def execute(self, dry_run: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        self.reporter.log_step_start("Usuários e Administradores -> [user]")

        extracted_count = 0
        migrated_count = 0
        skipped_count = 0
        recruiters_skipped = 0
        errors_count = 0

        users_batch: List[UserEntity] = []
        seen_emails = set()

        def flush_users_batch():
            nonlocal migrated_count, errors_count
            if not dry_run and users_batch:
                try:
                    saved = self.target_db.save_users(users_batch)
                    migrated_count += saved
                    if saved < len(users_batch):
                        diff = len(users_batch) - saved
                        errors_count += diff
                        self.reporter.log_error(f"{diff} usuários não puderam ser persistidos no banco de destino.")
                except Exception as e:
                    errors_count += len(users_batch)
                    self.reporter.log_error(f"Erro ao salvar lote de usuários: {e}", e)
                finally:
                    users_batch.clear()
            elif dry_run and users_batch:
                migrated_count += len(users_batch)
                users_batch.clear()

        # 1. Processar Usuários Legados
        for row in self.source_db.get_usuarios():
            extracted_count += 1
            user_legacy_id = row.get("UsuarioId") or row.get("Id") or row.get("_pk")
            try:
                dto = LegacyUserDTO(
                    id=user_legacy_id,
                    nome=row.get("Nome"),
                    email=row.get("Email"),
                    senha=row.get("Senha"),
                    tipo_usuario=row.get("TipoUsuario"),
                    avatar_url=row.get("AvatarUrl"),
                    data_criacao=row.get("DataCriacao"),
                    data_atualizacao=row.get("DataAtualizacao"),
                    status=row.get("Status"),
                )

                # Salva avatar no cache se for aluno
                if dto.avatar_url:
                    self.id_mapper.set_mapping("user_avatar", dto.id, dto.avatar_url)

                entity = EntityFactory.create_user_from_legacy(
                    dto, self.id_mapper, omit_recruiters=self.omit_recruiters
                )

                if entity is None:
                    skipped_count += 1
                    recruiters_skipped += 1
                    continue

                email_str = str(entity.email)
                if email_str in seen_emails:
                    self.reporter.log_warning(f"E-mail duplicado ignorado na migração: {email_str}")
                    skipped_count += 1
                    continue

                seen_emails.add(email_str)
                users_batch.append(entity)

                if len(users_batch) >= self.batch_size:
                    flush_users_batch()

            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar usuário legado {user_legacy_id}: {e}", e)

        # 2. Processar Administradores Legados
        for row in self.source_db.get_admins():
            extracted_count += 1
            admin_legacy_id = row.get("AdminId") or row.get("Id") or row.get("_pk")
            try:
                dto = LegacyAdminDTO(
                    id=admin_legacy_id,
                    login=row.get("Login"),
                    senha=row.get("Senha"),
                    email=row.get("Email"),
                    tipo_admin=row.get("TipoAdmin"),
                    status=row.get("Status"),
                    data_criacao=row.get("DataCriacao"),
                    data_atualizacao=row.get("DataAtualizacao"),
                    ferias_inicio=row.get("FeriasInicio"),
                    ferias_fim=row.get("FeriasFim"),
                    arquivado=row.get("Arquivado"),
                )

                entity = EntityFactory.create_user_from_admin(dto, self.id_mapper)
                email_str = str(entity.email)

                if email_str in seen_emails:
                    self.reporter.log_warning(f"Administrador com e-mail já existente: {email_str}. Mapeado para reutilização.")
                    continue

                seen_emails.add(email_str)
                users_batch.append(entity)

                if len(users_batch) >= self.batch_size:
                    flush_users_batch()

            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar admin legado {admin_legacy_id}: {e}", e)

        # Salvar lote remanescente
        flush_users_batch()

        duration = time.time() - start_time
        if recruiters_skipped > 0:
            self.reporter.log_info(f"Regra de Recruiter: {recruiters_skipped} perfis de recrutadores legados não foram criados como [user] ativo.")

        self.reporter.log_step_completed("Usuários e Administradores", extracted_count, migrated_count, skipped_count)

        return {
            "step": "users",
            "extracted": extracted_count,
            "migrated": migrated_count,
            "skipped": skipped_count,
            "errors": errors_count,
            "recruiters_skipped": recruiters_skipped,
            "duration_seconds": duration,
        }

