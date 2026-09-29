import time
from typing import Dict, Any, List

from src.application.dtos.legacy_dtos import LegacyCompanyDTO
from src.application.factories.entity_factory import EntityFactory
from src.domain.entities.address import AddressEntity
from src.domain.entities.contact import ContactEntity
from src.domain.entities.phone import PhoneEntity
from src.domain.entities.company import CompanyEntity
from src.domain.ports.inbound.step_migration_port import StepMigrationPort
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class MigrateCompaniesUseCase(StepMigrationPort):
    """
    Caso de Uso: Migração de Empresas para Company, Address, Contact e Phone.
    Aplica normalização em 3FN para desacoplamento de localização e contatos corporativos.
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
        self.reporter.log_step_start("Empresas -> [company, address, contact, phone]")

        extracted_count = 0
        migrated_count = 0
        skipped_count = 0
        errors_count = 0

        addresses: List[AddressEntity] = []
        contacts: List[ContactEntity] = []
        phones: List[PhoneEntity] = []
        companies: List[CompanyEntity] = []

        seen_cnpjs = set()

        def flush_companies_batch():
            nonlocal migrated_count, errors_count
            if not dry_run and companies:
                try:
                    self.target_db.save_addresses(addresses)
                    self.target_db.save_contacts(contacts)
                    self.target_db.save_phones(phones)
                    saved = self.target_db.save_companies(companies)
                    migrated_count += saved
                    if saved < len(companies):
                        diff = len(companies) - saved
                        errors_count += diff
                        self.reporter.log_error(f"{diff} empresas não puderam ser persistidas no banco de destino.")
                except Exception as e:
                    errors_count += len(companies)
                    self.reporter.log_error(f"Erro ao salvar lote de empresas: {e}", e)
                finally:
                    addresses.clear()
                    contacts.clear()
                    phones.clear()
                    companies.clear()
            elif dry_run and companies:
                migrated_count += len(companies)
                addresses.clear()
                contacts.clear()
                phones.clear()
                companies.clear()

        for row in self.source_db.get_empresas():
            extracted_count += 1
            empresa_legacy_id = row.get("EmpresaId") or row.get("Id") or row.get("_pk")
            try:
                dto = LegacyCompanyDTO(
                    id=empresa_legacy_id,
                    nome_fantasia=row.get("NomeFantasia"),
                    razao_social=row.get("RazaoSocial"),
                    cnpj=row.get("CNPJ"),
                    telefone=row.get("Telefone"),
                    logradouro=row.get("Logradouro"),
                    numero=row.get("Numero"),
                    complemento=row.get("Complemento"),
                    bairro=row.get("Bairro"),
                    cidade=row.get("Cidade"),
                    estado=row.get("Estado"),
                    cep=row.get("CEP"),
                    parceira_senac=row.get("ParceiraSenac"),
                    logo_url=row.get("LogoURL"),
                    website_url=row.get("WebsiteURL"),
                    usuario_id=row.get("UsuarioId"),
                    descricao=row.get("Descricao"),
                    status_aprovacao=row.get("StatusAprovacao"),
                    data_criacao=row.get("DataCriacao"),
                    data_atualizacao=row.get("DataAtualizacao"),
                    email_contato=row.get("EmailContato"),
                    mostrar_email_contato=row.get("MostrarEmailContato"),
                    mostrar_telefone_contato=row.get("MostrarTelefoneContato"),
                )

                addr, cont, phone, comp = EntityFactory.create_company_bundle(dto, self.id_mapper)
                cnpj_str = str(comp.cnpj)

                if cnpj_str in seen_cnpjs:
                    self.reporter.log_warning(f"CNPJ duplicado ignorado na migração: {cnpj_str}")
                    skipped_count += 1
                    continue

                seen_cnpjs.add(cnpj_str)
                addresses.append(addr)
                contacts.append(cont)
                phones.append(phone)
                companies.append(comp)

                if len(companies) >= self.batch_size:
                    flush_companies_batch()

            except Exception as e:
                errors_count += 1
                self.reporter.log_error(f"Erro ao processar empresa legada {empresa_legacy_id}: {e}", e)

        flush_companies_batch()

        duration = time.time() - start_time
        self.reporter.log_step_completed("Empresas e Estruturas Auxiliares", extracted_count, migrated_count, skipped_count)

        return {
            "step": "companies",
            "extracted": extracted_count,
            "migrated": migrated_count,
            "skipped": skipped_count,
            "errors": errors_count,
            "duration_seconds": duration,
        }
