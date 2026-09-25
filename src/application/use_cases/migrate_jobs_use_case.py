import time
from typing import Dict, Any, List

from src.application.dtos.legacy_dtos import LegacyVagaDTO
from src.application.factories.entity_factory import EntityFactory
from src.domain.entities.job import JobEntity
from src.domain.ports.inbound.step_migration_port import StepMigrationPort
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class MigrateJobsUseCase(StepMigrationPort):
    """
    Caso de Uso: Migração de Vagas para a tabela job.
    ATENÇÃO: A tabela Recruiter foi descontinuada no novo schema.
    Este caso de uso elimina o campo RecrutadorId e vincula a oportunidade
    diretamente à organização conveniada (company_id).
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
        self.reporter.log_step_start("Vagas -> [job] (Desacoplamento de Recruiter)")

        # 1. Carregar mapa auxiliar de Recrutador -> Empresa para fallback
        recruiter_empresa_map: Dict[Any, Any] = {}
        for rec in self.source_db.get_recruiters():
            rec_id = rec.get("id") or rec.get("Id") or rec.get("UsuarioId")
            emp_id = rec.get("EmpresaId")
            if rec_id and emp_id:
                recruiter_empresa_map[rec_id] = emp_id

        extracted_count = 0
        migrated_count = 0
        skipped_count = 0
        errors_count = 0

        jobs: List[JobEntity] = []

        def flush_jobs_batch():
            if not dry_run and jobs:
                try:
                    self.target_db.save_jobs(jobs)
                finally:
                    jobs.clear()

        for row in self.source_db.get_vagas():
            extracted_count += 1
            vaga_legacy_id = row.get("VagaId") or row.get("Id") or row.get("_pk")
            try:
                dto = LegacyVagaDTO(
                    id=vaga_legacy_id,
                    empresa_id=row.get("EmpresaId"),
                    titulo=row.get("Titulo"),
                    descricao=row.get("Descricao"),
                    data_publicacao=row.get("DataPublicacao"),
                    data_atualizacao=row.get("DataAtualizacao"),
                    data_encerramento=row.get("DataEncerramento"),
                    segmento=row.get("Segmento"),
                    modalidade=row.get("Modalidade"),
                    tipo=row.get("Tipo"),
                    pcd=row.get("PCD"),
                    escolaridade_minima=row.get("EscolaridadeMinima"),
                    idade_minima=row.get("IdadeMinima"),
                    status=row.get("Status"),
                    salario=row.get("Salario"),
                    salario_maximo=row.get("SalarioMaximo"),
                    beneficios=row.get("Beneficios"),
                    recrutador_id=row.get("RecrutadorId"),
                    mostrar_email_contato=row.get("MostrarEmailContato"),
                    mostrar_salario=row.get("MostrarSalario"),
                    mostrar_telefone_contato=row.get("MostrarTelefoneContato"),
                    quantidade_vagas=row.get("QuantidadeVagas"),
                )

                job_entity = EntityFactory.create_job_from_legacy(
                    dto, self.id_mapper, recruiter_empresa_map=recruiter_empresa_map
                )

                if job_entity is None:
                    self.reporter.log_warning(
                        f"Vaga {dto.id} ('{dto.titulo}') ignorada: empresa correspondente não localizada."
                    )
                    skipped_count += 1
                    continue

                jobs.append(job_entity)
                migrated_count += 1

                if len(jobs) >= self.batch_size:
                    flush_jobs_batch()

            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar vaga legada {vaga_legacy_id}: {e}", e)

        flush_jobs_batch()

        duration = time.time() - start_time
        self.reporter.log_info("Regra de Recruiter: Todas as vagas foram vinculadas diretamente às empresas contratantes.")
        self.reporter.log_step_completed("Vagas de Emprego", extracted_count, migrated_count, skipped_count)

        return {
            "step": "jobs",
            "extracted": extracted_count,
            "migrated": migrated_count,
            "skipped": skipped_count,
            "errors": errors_count,
            "duration_seconds": duration,
        }
