import time
from typing import Dict, Any, List

from src.application.dtos.legacy_dtos import (
    LegacyExperienceDTO,
    LegacyLanguageDTO,
    LegacyQualificationDTO,
)
from src.application.factories.entity_factory import EntityFactory
from src.domain.entities.curriculum import (
    ExperienceEntity,
    LanguageEntity,
    QualificationEntity,
)
from src.domain.ports.inbound.step_migration_port import StepMigrationPort
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class MigrateCurriculumUseCase(StepMigrationPort):
    """
    Caso de Uso: Migração do Histórico Curricular (Experiências, Idiomas e Qualificações).
    Mapeia os registros de AlunoId legado diretamente para o user_id do egresso no novo schema.
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
        self.reporter.log_step_start("Currículo -> [experience, language, qualification]")

        extracted_count = 0
        migrated_count = 0
        skipped_count = 0
        errors_count = 0

        experiences: List[ExperienceEntity] = []
        languages: List[LanguageEntity] = []
        qualifications: List[QualificationEntity] = []

        def flush_exp_batch():
            if not dry_run and experiences:
                try:
                    self.target_db.save_experiences(experiences)
                finally:
                    experiences.clear()

        def flush_lang_batch():
            if not dry_run and languages:
                try:
                    self.target_db.save_languages(languages)
                finally:
                    languages.clear()

        def flush_qual_batch():
            if not dry_run and qualifications:
                try:
                    self.target_db.save_qualifications(qualifications)
                finally:
                    qualifications.clear()

        # 1. Experiências
        for row in self.source_db.get_experiencias():
            extracted_count += 1
            exp_id = row.get("ExperienciaId") or row.get("Id") or row.get("_pk")
            try:
                dto = LegacyExperienceDTO(
                    id=exp_id,
                    aluno_id=row.get("AlunoId"),
                    cargo=row.get("Cargo"),
                    empresa=row.get("Empresa"),
                    data_inicio=row.get("DataInicio"),
                    data_fim=row.get("DataFim"),
                    atual=row.get("Atual"),
                    descricao=row.get("Descricao"),
                    data_criacao=row.get("DataCriacao"),
                    data_atualizacao=row.get("DataAtualizacao"),
                )
                entity = EntityFactory.create_experience_from_legacy(dto, self.id_mapper)
                if not entity:
                    skipped_count += 1
                    continue
                experiences.append(entity)
                migrated_count += 1

                if len(experiences) >= self.batch_size:
                    flush_exp_batch()
            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar experiência {exp_id}: {e}", e)

        flush_exp_batch()

        # 2. Idiomas
        for row in self.source_db.get_idiomas():
            extracted_count += 1
            idioma_id = row.get("IdiomaId") or row.get("Id") or row.get("_pk")
            try:
                dto = LegacyLanguageDTO(
                    id=idioma_id,
                    aluno_id=row.get("AlunoId"),
                    idioma=row.get("Idioma"),
                    fluencia=row.get("Fluencia"),
                    data_criacao=row.get("DataCriacao"),
                    data_atualizacao=row.get("DataAtualizacao"),
                )
                entity = EntityFactory.create_language_from_legacy(dto, self.id_mapper)
                if not entity:
                    skipped_count += 1
                    continue
                languages.append(entity)
                migrated_count += 1

                if len(languages) >= self.batch_size:
                    flush_lang_batch()
            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar idioma {idioma_id}: {e}", e)

        flush_lang_batch()

        # 3. Qualificações
        for row in self.source_db.get_qualificacoes():
            extracted_count += 1
            qual_id = row.get("QualificacaoId") or row.get("Id") or row.get("_pk")
            try:
                dto = LegacyQualificationDTO(
                    id=qual_id,
                    aluno_id=row.get("AlunoId"),
                    curso=row.get("Curso"),
                    instituicao=row.get("Instituicao"),
                    data_inicio=row.get("DataInicio"),
                    data_fim=row.get("DataFim"),
                    atual=row.get("Atual"),
                    descricao=row.get("Descricao"),
                    data_criacao=row.get("DataCriacao"),
                    data_atualizacao=row.get("DataAtualizacao"),
                )
                entity = EntityFactory.create_qualification_from_legacy(dto, self.id_mapper)
                if not entity:
                    skipped_count += 1
                    continue
                qualifications.append(entity)
                migrated_count += 1

                if len(qualifications) >= self.batch_size:
                    flush_qual_batch()
            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar qualificação {qual_id}: {e}", e)

        flush_qual_batch()

        duration = time.time() - start_time
        self.reporter.log_step_completed("Currículo Profissional", extracted_count, migrated_count, skipped_count)

        return {
            "step": "curriculum",
            "extracted": extracted_count,
            "migrated": migrated_count,
            "skipped": skipped_count,
            "errors": errors_count,
            "duration_seconds": duration,
        }
