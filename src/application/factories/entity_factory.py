import re
from datetime import datetime
from typing import Tuple, Dict, Any
from uuid import UUID

from src.application.dtos.legacy_dtos import (
    LegacyUserDTO,
    LegacyAdminDTO,
    LegacyCompanyDTO,
    LegacyStudentDTO,
    LegacyVagaDTO,
    LegacyExperienceDTO,
    LegacyLanguageDTO,
    LegacyQualificationDTO,
    LegacyInscricaoDTO,
    LegacyNotificationDTO,
    LegacyLogAdminDTO,
    LegacyLogJobDTO,
    LegacyLogUserDTO,
)
from src.application.factories.uuid_factory import UUIDFactory
from src.domain.entities.user import UserEntity
from src.domain.entities.address import AddressEntity
from src.domain.entities.contact import ContactEntity
from src.domain.entities.phone import PhoneEntity
from src.domain.entities.company import CompanyEntity
from src.domain.entities.student import StudentEntity
from src.domain.entities.job import JobEntity
from src.domain.entities.application import ApplicationEntity
from src.domain.entities.curriculum import ExperienceEntity, LanguageEntity, QualificationEntity
from src.domain.entities.notification import NotificationEntity
from src.domain.entities.log import LogEntity
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.domain.enums.approval_status import ApprovalStatus
from src.domain.enums.job_enums import JobWorkMode, JobType, JobStatus, JobEducation
from src.domain.enums.student_enums import StudentTypePCD, StudentEducation
from src.domain.enums.application_enums import ApplicationStatus
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.value_objects.cpf import CPF
from src.domain.value_objects.cnpj import CNPJ
from src.domain.value_objects.email import Email
from src.domain.value_objects.phone_number import PhoneNumber


class EntityFactory:
    """
    Fábrica responsável por orquestrar a conversão entre DTOs legados
    e as Entidades puras do Domínio, aplicando higienização, defaults
    e regras de transição de schema (ex: eliminação de Recruiter).
    """

    @staticmethod
    def _truncate_to_bytes(text: str | None, max_bytes: int) -> str | None:
        if not text:
            return text
        encoded = text.encode("utf-8")
        if len(encoded) <= max_bytes:
            return text
        return encoded[:max_bytes].decode("utf-8", errors="ignore")

    @staticmethod
    def _parse_int_safe(val: Any, default: int = 0) -> int:
        if val is None:
            return default
        digits = re.sub(r"\D", "", str(val))
        return int(digits) if digits else default

    @staticmethod
    def create_user_from_legacy(
        dto: LegacyUserDTO,
        id_mapper: IdMappingPort,
        omit_recruiters: bool = True
    ) -> UserEntity | None:
        raw_role = str(dto.tipo_usuario or "").strip().upper()
        if raw_role in ("RECRUITER", "RECRUTADOR") and omit_recruiters:
            # Recrutadores não existem no novo schema e são descartados ou inativados
            return None

        user_id = id_mapper.get_or_create(
            "user", dto.id, lambda: UUIDFactory.create_deterministic("user", dto.id)
        )
        now = datetime.now()
        created_at = dto.data_criacao or now
        updated_at = dto.data_atualizacao or created_at

        return UserEntity(
            id=user_id,
            name=dto.nome.strip() if dto.nome else "Usuário Sem Nome",
            email=Email.create(dto.email),
            password=dto.senha or "SENHA_NAO_DEFINIDA",
            role=UserRole.from_legacy(dto.tipo_usuario),
            status=UserStatus.from_legacy(dto.status),
            created_at=created_at,
            updated_at=updated_at,
        )

    @staticmethod
    def create_user_from_admin(
        dto: LegacyAdminDTO,
        id_mapper: IdMappingPort
    ) -> UserEntity:
        user_id = id_mapper.get_or_create(
            "user", f"admin_{dto.id}", lambda: UUIDFactory.create_deterministic("user", f"admin_{dto.id}")
        )
        raw_type = str(dto.tipo_admin or "").upper()
        role = UserRole.SUPER_ADMIN if "SUPER" in raw_type else UserRole.ADMIN

        now = datetime.now()
        created_at = dto.data_criacao or now
        updated_at = dto.data_atualizacao or created_at

        name = dto.login.strip() if dto.login else "Administrador"

        return UserEntity(
            id=user_id,
            name=name,
            email=Email.create(dto.email),
            password=dto.senha or "SENHA_NAO_DEFINIDA",
            role=role,
            status=UserStatus.from_legacy(dto.status),
            created_at=created_at,
            updated_at=updated_at,
        )

    @classmethod
    def create_company_bundle(
        cls,
        dto: LegacyCompanyDTO,
        id_mapper: IdMappingPort
    ) -> Tuple[AddressEntity, ContactEntity, PhoneEntity, CompanyEntity]:
        company_id = id_mapper.get_or_create(
            "company", dto.id, lambda: UUIDFactory.create_deterministic("company", dto.id)
        )

        # Resolução do Usuário gestor da empresa
        user_id = id_mapper.get_mapping("user", dto.usuario_id)
        if not user_id:
            user_id = UUIDFactory.create_deterministic("user", dto.usuario_id)
            id_mapper.set_mapping("user", dto.usuario_id, user_id)

        # 1. Address
        address_id = UUIDFactory.create_deterministic("address", dto.id)
        raw_street = dto.logradouro.strip() if dto.logradouro else "Não informado"
        raw_bairro = dto.bairro.strip() if dto.bairro else "Centro"
        raw_cidade = dto.cidade.strip() if dto.cidade else "Aracaju"
        raw_comp = dto.complemento.strip() if dto.complemento else None

        address = AddressEntity(
            id=address_id,
            street=cls._truncate_to_bytes(raw_street, 50) or "Não informado",
            number=cls._parse_int_safe(dto.numero, default=0),
            neighborhood=cls._truncate_to_bytes(raw_bairro, 50) or "Centro",
            city=cls._truncate_to_bytes(raw_cidade, 50) or "Aracaju",
            state=(dto.estado.strip()[:2].upper() if dto.estado else "SE"),
            zipcode=re.sub(r"\D", "", str(dto.cep or "49000000"))[:10],
            complement=cls._truncate_to_bytes(raw_comp, 50) if raw_comp else None,
        )

        # 2. Contact
        contact_id = UUIDFactory.create_deterministic("contact", dto.id)
        contact_email = dto.email_contato or f"contato_{company_id}@empresa.local"
        contact = ContactEntity(
            id=contact_id,
            email=Email.create(contact_email),
            show_email=bool(dto.mostrar_email_contato if dto.mostrar_email_contato is not None else True),
            show_phone=bool(dto.mostrar_telefone_contato if dto.mostrar_telefone_contato is not None else True),
        )

        # 3. Phone
        phone_id = UUIDFactory.create_deterministic("phone", dto.id)
        phone_vo = PhoneNumber.create(dto.telefone)
        phone = PhoneEntity(
            id=phone_id,
            contact_id=contact_id,
            phone=phone_vo,
        )

        # 4. Company
        now = datetime.now()
        legal_name = dto.razao_social or dto.nome_fantasia or "Empresa Sem Razão Social"
        description = dto.descricao or f"Perfil institucional da empresa {legal_name}"

        company = CompanyEntity(
            id=company_id,
            user_id=user_id,
            cnpj=CNPJ.create(dto.cnpj),
            legal_name=legal_name[:50],
            description=description[:500],
            is_senac_partner=bool(dto.parceira_senac or False),
            approval_status=ApprovalStatus.from_legacy(dto.status_aprovacao),
            address_id=address_id,
            contact_id=contact_id,
            websiteurl=dto.website_url[:255] if dto.website_url else None,
            logourl=dto.logo_url[:255] if dto.logo_url else None,
            created_at=dto.data_criacao or now,
            updated_at=dto.data_atualizacao or now,
        )

        return address, contact, phone, company

    @classmethod
    def create_student_bundle(
        cls,
        dto: LegacyStudentDTO,
        id_mapper: IdMappingPort,
        avatar_url: str | None = None
    ) -> Tuple[ContactEntity | None, StudentEntity]:
        student_id = id_mapper.get_or_create(
            "student", dto.id, lambda: UUIDFactory.create_deterministic("student", dto.id)
        )

        user_id = id_mapper.get_mapping("user", dto.usuario_id)
        if not user_id:
            user_id = UUIDFactory.create_deterministic("user", dto.usuario_id)
            id_mapper.set_mapping("user", dto.usuario_id, user_id)

        # Registra também o mapeamento do aluno para seu user_id (usado no currículo)
        id_mapper.set_mapping("student_to_user", dto.id, user_id)

        now = datetime.now()
        siga_id = dto.aluno_id_sig or f"SIG-{student_id.hex[:8].upper()}"

        student = StudentEntity(
            id=student_id,
            user_id=user_id,
            cpf=CPF.create(dto.cpf),
            pcd=bool(dto.pcd or False),
            student_id_siga=str(siga_id)[:50],
            created_at=dto.data_criacao or now,
            updated_at=dto.data_atualizacao or now,
            contact_id=None,
            avatar_url=avatar_url or None,
            type_pcd=StudentTypePCD.from_legacy(dto.tipo_pcd) if dto.pcd else StudentTypePCD.NON,
            education=StudentEducation.from_legacy(dto.escolaridade),
            linkedin_url=dto.linkedin_url[:255] if dto.linkedin_url else None,
            portfolio=dto.portfolio[:255] if dto.portfolio else None,
        )

        return None, student

    @classmethod
    def create_job_from_legacy(
        cls,
        dto: LegacyVagaDTO,
        id_mapper: IdMappingPort,
        recruiter_empresa_map: Dict[Any, Any] | None = None
    ) -> JobEntity | None:
        """
        Mapeia Vaga para job no novo schema.
        REGRA PRINCIPAL: A tabela Recruiter foi descontinuada.
        O campo RecrutadorId da vaga antiga é eliminado e a vaga é associada
        diretamente a company_id.
        """
        job_id = id_mapper.get_or_create(
            "job", dto.id, lambda: UUIDFactory.create_deterministic("job", dto.id)
        )

        company_id = None
        # 1. Tenta obter company_id diretamente de empresa_id
        if dto.empresa_id is not None:
            company_id = id_mapper.get_mapping("company", dto.empresa_id)

        # 2. Se não encontrou, tenta fallback via recrutador_id usando o mapa legado de recrutadores
        if not company_id and dto.recrutador_id is not None and recruiter_empresa_map:
            empresa_legada = recruiter_empresa_map.get(dto.recrutador_id)
            if empresa_legada:
                company_id = id_mapper.get_mapping("company", empresa_legada)

        if not company_id:
            # Não é possível vincular uma vaga sem uma empresa válida no novo schema
            return None

        now = datetime.now()
        published_at = dto.data_publicacao or now
        updated_at = dto.data_atualizacao or published_at

        # Regra de negócio de cálculo de status por data:
        # Se a data de encerramento já passou, a vaga é migrada como CLOSED (fechada/encerrada).
        job_status = JobStatus.from_legacy(dto.status)
        if dto.data_encerramento:
            try:
                closing_dt = dto.data_encerramento
                if hasattr(closing_dt, "date"):
                    if closing_dt.date() < now.date() or (
                        closing_dt.date() == now.date()
                        and (closing_dt.hour != 0 or closing_dt.minute != 0)
                        and closing_dt < now
                    ):
                        job_status = JobStatus.CLOSED
                elif isinstance(closing_dt, str):
                    from datetime import datetime as dt
                    parsed_dt = dt.fromisoformat(closing_dt.replace("Z", "+00:00"))
                    if parsed_dt.date() < now.date():
                        job_status = JobStatus.CLOSED
            except Exception:
                pass

        # Title normalization: >= 4 chars, <= 255 bytes
        raw_title = (dto.titulo or "").strip()
        if len(raw_title) < 4:
            raw_title = f"Vaga {raw_title}".strip() if raw_title else "Oportunidade de Trabalho"
            if len(raw_title) < 4:
                raw_title = raw_title.ljust(4, ".")
        title = cls._truncate_to_bytes(raw_title, 255)

        # Description normalization: >= 10 chars, <= 500 bytes
        raw_desc = (dto.descricao or "").strip()
        if len(raw_desc) < 10:
            if raw_desc:
                raw_desc = f"Nesta vaga vai ser realizado atividades de: {raw_desc}".strip()
            else:
                raw_desc = f"Nesta vaga vai ser realizado atividades de: {raw_title}".strip()
        description = cls._truncate_to_bytes(raw_desc, 500)

        return JobEntity(
            id=job_id,
            company_id=company_id,
            title=title,
            description=description,
            segment=cls._truncate_to_bytes(dto.segmento, 255) if dto.segmento else None,
            work_mode=JobWorkMode.from_legacy(dto.modalidade),
            type=JobType.from_legacy(dto.tipo),
            pcd=bool(dto.pcd or False),
            minimum_education=JobEducation.from_legacy(dto.escolaridade_minima),
            minimum_age=dto.idade_minima,
            status=job_status,
            salary=float(dto.salario) if dto.salario is not None else None,
            maximum_salary=float(dto.salario_maximo) if dto.salario_maximo is not None else None,
            number_of_openings=dto.quantidade_vagas or 1,
            show_contact_email=bool(dto.mostrar_email_contato if dto.mostrar_email_contato is not None else True),
            show_contact_phone=bool(dto.mostrar_telefone_contato if dto.mostrar_telefone_contato is not None else True),
            show_salary=bool(dto.mostrar_salario if dto.mostrar_salario is not None else True),
            benefits=cls._truncate_to_bytes(dto.beneficios, 1000) if dto.beneficios else None,
            closing_date=dto.data_encerramento,
            published_at=published_at,
            updated_at=updated_at,
        )

    @classmethod
    def create_experience_from_legacy(
        cls,
        dto: LegacyExperienceDTO,
        id_mapper: IdMappingPort
    ) -> ExperienceEntity | None:
        user_id = id_mapper.get_mapping("student_to_user", dto.aluno_id)
        if not user_id:
            user_id = id_mapper.get_mapping("user", dto.aluno_id)
        if not user_id:
            return None

        exp_id = UUIDFactory.create_deterministic("experience", dto.id)
        now = datetime.now()

        return ExperienceEntity(
            id=exp_id,
            user_id=user_id,
            empresa=dto.empresa[:100] if dto.empresa else None,
            cargo=dto.cargo[:100] if dto.cargo else None,
            descricao=dto.descricao,
            data_inicio=dto.data_inicio,
            data_fim=dto.data_fim,
            atual=bool(dto.atual or False),
            criado_em=dto.data_criacao or now,
            atualizado_em=dto.data_atualizacao or now,
        )

    @classmethod
    def create_language_from_legacy(
        cls,
        dto: LegacyLanguageDTO,
        id_mapper: IdMappingPort
    ) -> LanguageEntity | None:
        user_id = id_mapper.get_mapping("student_to_user", dto.aluno_id)
        if not user_id:
            user_id = id_mapper.get_mapping("user", dto.aluno_id)
        if not user_id:
            return None

        lang_id = UUIDFactory.create_deterministic("language", dto.id)
        now = datetime.now()

        return LanguageEntity(
            id=lang_id,
            user_id=user_id,
            idioma=dto.idioma[:100] if dto.idioma else "Não informado",
            nivel=dto.fluencia[:50] if dto.fluencia else "Básico",
            criado_em=dto.data_criacao or now,
            atualizado_em=dto.data_atualizacao or now,
        )

    @classmethod
    def create_qualification_from_legacy(
        cls,
        dto: LegacyQualificationDTO,
        id_mapper: IdMappingPort
    ) -> QualificationEntity | None:
        user_id = id_mapper.get_mapping("student_to_user", dto.aluno_id)
        if not user_id:
            user_id = id_mapper.get_mapping("user", dto.aluno_id)
        if not user_id:
            return None

        qual_id = UUIDFactory.create_deterministic("qualification", dto.id)
        now = datetime.now()
        course = dto.curso[:100] if dto.curso else "Qualificação Profissional"

        return QualificationEntity(
            id=qual_id,
            user_id=user_id,
            titulo=course,
            curso=course,
            instituicao=dto.instituicao[:100] if dto.instituicao else "Senac Sergipe",
            descricao=dto.descricao,
            data_inicio=dto.data_inicio,
            data_fim=dto.data_fim,
            em_andamento=bool(dto.atual or False),
            criado_em=dto.data_criacao or now,
            atualizado_em=dto.data_atualizacao or now,
        )

    @classmethod
    def create_application_from_legacy(
        cls,
        dto: LegacyInscricaoDTO,
        id_mapper: IdMappingPort
    ) -> ApplicationEntity | None:
        job_id = id_mapper.get_mapping("job", dto.vaga_id)
        student_id = id_mapper.get_mapping("student", dto.aluno_id)

        if not job_id or not student_id:
            return None

        app_id = UUIDFactory.create_deterministic("application", dto.id)
        now = datetime.now()

        return ApplicationEntity(
            id=app_id,
            job_id=job_id,
            student_id=student_id,
            applied_at=dto.data_inscricao or now,
            status=ApplicationStatus.from_legacy(dto.status),
            status_changed_at=dto.data_atualizacao or dto.data_inscricao or now,
        )

    @classmethod
    def create_notification_from_legacy(
        cls,
        dto: LegacyNotificationDTO,
        id_mapper: IdMappingPort
    ) -> NotificationEntity | None:
        user_id = id_mapper.get_mapping("user", dto.usuario_id)
        if not user_id:
            return None

        notif_id = UUIDFactory.create_deterministic("notification", dto.id)
        now = datetime.now()

        return NotificationEntity(
            id=notif_id,
            user_id=user_id,
            title=dto.titulo[:100] if dto.titulo else "Notificação do Sistema",
            content=dto.conteudo[:500] if dto.conteudo else "Sem conteúdo adicional",
            is_read=bool(dto.is_read or False),
            type=dto.tipo[:50] if dto.tipo else "GENERAL",
            status=dto.status[:50] if dto.status else "DELIVERED",
            created_at=dto.data_criacao or now,
            updated_at=dto.updated_at or now,
        )

    @classmethod
    def create_log_from_admin(
        cls,
        dto: LegacyLogAdminDTO,
        id_mapper: IdMappingPort
    ) -> LogEntity:
        log_id = UUIDFactory.create_deterministic("log_admin", dto.id)
        user_id = id_mapper.get_mapping("user", f"admin_{dto.admin_id}")
        user_id_str = str(user_id) if user_id else str(dto.admin_id)

        now = datetime.now()
        created_at = dto.data_criacao or now

        return LogEntity(
            id=log_id,
            type_name="ADMIN",
            user_id=user_id_str[:255],
            user_name=dto.nome_de_usuario[:255] if dto.nome_de_usuario else None,
            type_action=dto.tipo_acao[:255] if dto.tipo_acao else "ACTION",
            description=dto.descricao[:255] if dto.descricao else None,
            reason=None,
            message=dto.user_agent[:500] if dto.user_agent else None,
            ip_address=dto.ipv4[:255] if dto.ipv4 else None,
            created_at=created_at,
            updated_at=created_at,
        )

    @classmethod
    def create_log_from_job(
        cls,
        dto: LegacyLogJobDTO,
        id_mapper: IdMappingPort
    ) -> LogEntity:
        log_id = UUIDFactory.create_deterministic("log_job", dto.id)
        user_id = id_mapper.get_mapping("user", dto.usuario_id)
        user_id_str = str(user_id) if user_id else str(dto.usuario_id or dto.admin_id or "")

        now = datetime.now()
        created_at = dto.data_criacao or now

        return LogEntity(
            id=log_id,
            type_name="JOB",
            user_id=user_id_str[:255] if user_id_str else None,
            user_name=dto.tipo_usuario[:255] if dto.tipo_usuario else None,
            type_action=dto.acao[:255] if dto.acao else "JOB_ACTION",
            description=f"Log associado à Vaga legada {dto.job_id}",
            reason=dto.motivo[:255] if dto.motivo else None,
            message=None,
            ip_address=None,
            created_at=created_at,
            updated_at=created_at,
        )

    @classmethod
    def create_log_from_user(
        cls,
        dto: LegacyLogUserDTO,
        id_mapper: IdMappingPort
    ) -> LogEntity:
        log_id = UUIDFactory.create_deterministic("log_user", dto.id)
        user_id = id_mapper.get_mapping("user", dto.usuario_id)
        user_id_str = str(user_id) if user_id else str(dto.usuario_id)

        now = datetime.utcnow()
        created_at = dto.data_criacao or now

        return LogEntity(
            id=log_id,
            type_name="USER",
            user_id=user_id_str[:255],
            user_name=dto.email[:255] if dto.email else None,
            type_action=dto.tipo_acao[:255] if dto.tipo_acao else "USER_ACTION",
            description=dto.descricao[:255] if dto.descricao else None,
            reason=None,
            message=dto.user_agent[:500] if dto.user_agent else None,
            ip_address=dto.ipv4[:255] if dto.ipv4 else None,
            created_at=created_at,
            updated_at=created_at,
        )
