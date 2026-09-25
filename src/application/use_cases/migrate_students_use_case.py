import time
from typing import Dict, Any, List

from src.application.dtos.legacy_dtos import LegacyStudentDTO
from src.application.factories.entity_factory import EntityFactory
from src.domain.entities.student import StudentEntity
from src.domain.ports.inbound.step_migration_port import StepMigrationPort
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class MigrateStudentsUseCase(StepMigrationPort):
    """
    Caso de Uso: Migração de Estudantes para a tabela student.
    Aplica sanitização de CPF, mapeamento com a conta de usuário e normalização de escolaridade/PCD.
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
        self.reporter.log_step_start("Estudantes -> [student]")

        extracted_count = 0
        migrated_count = 0
        skipped_count = 0
        errors_count = 0

        students: List[StudentEntity] = []
        seen_cpfs = set()

        def flush_students_batch():
            if not dry_run and students:
                try:
                    self.target_db.save_students(students)
                finally:
                    students.clear()

        for row in self.source_db.get_students():
            extracted_count += 1
            student_legacy_id = row.get("StudentId") or row.get("Id") or row.get("AlunoId") or row.get("_pk")
            try:
                dto = LegacyStudentDTO(
                    id=student_legacy_id,
                    nome=row.get("Nome"),
                    cpf=row.get("CPF"),
                    usuario_id=row.get("UsuarioId"),
                    pcd=row.get("PCD"),
                    tipo_pcd=row.get("TipoPCD"),
                    escolaridade=row.get("Escolaridade"),
                    aluno_id_sig=row.get("AlunoIdSIG"),
                    data_criacao=row.get("DataCriacao"),
                    data_atualizacao=row.get("DataAtualizacao"),
                    linkedin_url=row.get("LinkedInURL"),
                    portfolio=row.get("Portfolio"),
                )

                # Busca avatar do cache de usuário
                avatar = self.id_mapper.get_mapping("user_avatar", dto.usuario_id)

                _, student_entity = EntityFactory.create_student_bundle(
                    dto, self.id_mapper, avatar_url=str(avatar) if avatar else None
                )

                cpf_str = str(student_entity.cpf)
                if cpf_str in seen_cpfs:
                    self.reporter.log_warning(f"CPF duplicado ignorado na migração: {cpf_str}")
                    skipped_count += 1
                    continue

                seen_cpfs.add(cpf_str)
                students.append(student_entity)
                migrated_count += 1

                if len(students) >= self.batch_size:
                    flush_students_batch()

            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar estudante legado {student_legacy_id}: {e}", e)

        flush_students_batch()

        duration = time.time() - start_time
        self.reporter.log_step_completed("Estudantes", extracted_count, migrated_count, skipped_count)

        return {
            "step": "students",
            "extracted": extracted_count,
            "migrated": migrated_count,
            "skipped": skipped_count,
            "errors": errors_count,
            "duration_seconds": duration,
        }
