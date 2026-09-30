from datetime import datetime, timedelta
from src.application.dtos.legacy_dtos import (
    LegacyUserDTO,
    LegacyAdminDTO,
    LegacyCompanyDTO,
    LegacyStudentDTO,
    LegacyVagaDTO,
    LegacyExperienceDTO,
    LegacyLogAdminDTO,
    LegacyLogJobDTO,
    LegacyLogUserDTO,
)
from src.application.factories.uuid_factory import UUIDFactory
from src.application.factories.entity_factory import EntityFactory
from src.infrastructure.id_mapping.in_memory_id_mapper import InMemoryIdMapper
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.domain.enums.job_enums import JobWorkMode, JobType, JobStatus


def test_user_factory_normal_and_recruiter():
    id_mapper = InMemoryIdMapper()

    # Usuário Estudante normal
    student_dto = LegacyUserDTO(
        id=1,
        nome="João Aluno",
        email="joao@aluno.senac.br",
        senha="hash_password",
        tipo_usuario="STUDENT",
        status=1,
    )
    user_entity = EntityFactory.create_user_from_legacy(student_dto, id_mapper, omit_recruiters=True)
    assert user_entity is not None
    assert user_entity.name == "João Aluno"
    assert user_entity.role == UserRole.STUDENT
    assert user_entity.status == UserStatus.ACTIVE

    # Usuário Recrutador legado -> Deve ser ignorado quando omit_recruiters=True
    recruiter_dto = LegacyUserDTO(
        id=2,
        nome="Recrutador RH",
        email="rh@recrutador.com",
        senha="hash_password",
        tipo_usuario="RECRUITER",
        status=1,
    )
    omitted = EntityFactory.create_user_from_legacy(recruiter_dto, id_mapper, omit_recruiters=True)
    assert omitted is None


def test_admin_factory():
    id_mapper = InMemoryIdMapper()
    admin_dto = LegacyAdminDTO(
        id=10,
        login="admin_ntic",
        senha="senha_forte_bcrypt",
        email="admin.ntic@se.senac.br",
        tipo_admin="SUPER_ADMIN",
        status="ACTIVE",
    )
    admin_entity = EntityFactory.create_user_from_admin(admin_dto, id_mapper)
    assert admin_entity.name == "admin_ntic"
    assert admin_entity.role == UserRole.SUPER_ADMIN
    assert admin_entity.is_admin is True


def test_legacy_admin_log_maps_to_backend_activity_contract():
    entity = EntityFactory.create_log_from_admin(
        LegacyLogAdminDTO(1, 10, "Admin", "DELETE", "Excluiu uma vaga", "127.0.0.1", "Mozilla", datetime(2020, 1, 2)),
        InMemoryIdMapper(),
    )
    assert entity.type_name == "LOG_ATIVIDATE"
    assert entity.type_action == "DELETAR"
    assert entity.description == "Excluiu uma vaga"
    assert entity.message == "Mozilla"
    assert entity.created_at == datetime(2020, 1, 2)
    assert entity.user_id is None  # legacy integer IDs must not be persisted as UUIDs


def test_legacy_log_error_and_job_action_mapping():
    mapper = InMemoryIdMapper()
    error = EntityFactory.create_log_from_user(
        LegacyLogUserDTO(2, 20, "user@example.com", "LOGIN", "Falha HTTP 401 ao autenticar", "127.0.0.1", None, None),
        mapper,
    )
    assert error.type_name == "LOG_ERRO"
    assert error.type_action == "ATUALIZAR"
    assert error.reason == "Falha registrada na trilha do usuário"

    job = EntityFactory.create_log_from_job(
        LegacyLogJobDTO(3, 99, "Atualização de status", "Status alterado", None, "Empresa", 30, None),
        mapper,
    )
    assert job.type_name == "LOG_ATIVIDATE"
    assert job.type_action == "ATUALIZAR"
    assert job.description == "Atualização de status"
    assert job.message == "Status alterado"


def test_job_factory_removes_recruiter_and_maps_company():
    id_mapper = InMemoryIdMapper()
    # Registra empresa com ID legado 100
    company_uuid = UUIDFactory.create_deterministic("company", 100)
    id_mapper.set_mapping("company", 100, company_uuid)

    # 1. Vaga com EmpresaId explícito e RecrutadorId
    vaga_dto = LegacyVagaDTO(
        id=50,
        empresa_id=100,
        titulo="Desenvolvedor Java Spring Boot Júnior",
        descricao="Oportunidade para egressos do Senac",
        data_publicacao=None,
        data_atualizacao=None,
        data_encerramento=None,
        segmento="Tecnologia",
        modalidade="REMOTO",
        tipo="CLT",
        pcd=False,
        escolaridade_minima="SUPERIOR_INCOMPLETO",
        idade_minima=18,
        status="ABERTA",
        salario=3500.0,
        salario_maximo=4500.0,
        beneficios="VR, VT, Plano de Saúde",
        recrutador_id=999,  # Campo antigo de recrutador
        mostrar_email_contato=True,
        mostrar_salario=True,
        mostrar_telefone_contato=False,
        quantidade_vagas=2,
    )

    job_entity = EntityFactory.create_job_from_legacy(vaga_dto, id_mapper)
    assert job_entity is not None
    assert job_entity.title == "Desenvolvedor Java Spring Boot Júnior"
    assert job_entity.company_id == company_uuid
    # Valida que não existe atributo recrutador_id na entidade nova
    assert not hasattr(job_entity, "recrutador_id")
    assert not hasattr(job_entity, "recruiter_id")
    assert job_entity.work_mode == JobWorkMode.REMOTE
    assert job_entity.type == JobType.CLT
    assert job_entity.status == JobStatus.OPEN
    assert job_entity.number_of_openings == 2

    # 2. Vaga com EmpresaId nulo, mas RecrutadorId mapeado
    vaga_fallback_dto = LegacyVagaDTO(
        id=51,
        empresa_id=None,
        titulo="Assistente Administrativo",
        descricao="Vaga recuperada via recrutador",
        data_publicacao=None,
        data_atualizacao=None,
        data_encerramento=None,
        segmento="Administração",
        modalidade="PRESENCIAL",
        tipo="CLT",
        pcd=False,
        escolaridade_minima=None,
        idade_minima=None,
        status="ABERTO",
        salario=1800.0,
        salario_maximo=None,
        beneficios=None,
        recrutador_id=888,
        mostrar_email_contato=True,
        mostrar_salario=True,
        mostrar_telefone_contato=True,
        quantidade_vagas=1,
    )
    recruiter_map = {888: 100}  # Recrutador 888 pertence à empresa 100
    fallback_job = EntityFactory.create_job_from_legacy(vaga_fallback_dto, id_mapper, recruiter_empresa_map=recruiter_map)
    assert fallback_job is not None
    assert fallback_job.company_id == company_uuid


def test_job_status_calculated_by_closing_date():
    from datetime import timedelta
    id_mapper = InMemoryIdMapper()
    company_uuid = UUIDFactory.create_deterministic("company", 10)
    id_mapper.set_mapping("company", 10, company_uuid)
    now = datetime.now()

    # Vaga com status "ABERTA" mas data de encerramento no passado deve se tornar CLOSED
    vaga_expirada_dto = LegacyVagaDTO(
        id=60,
        empresa_id=10,
        titulo="Vaga Expirada",
        descricao="Vaga cujo prazo já encerrou",
        data_publicacao=now - timedelta(days=60),
        data_atualizacao=now - timedelta(days=60),
        data_encerramento=now - timedelta(days=5),
        segmento="TI",
        modalidade="REMOTO",
        tipo="CLT",
        pcd=False,
        escolaridade_minima=None,
        idade_minima=None,
        status="ABERTA",
        salario=3000.0,
        salario_maximo=None,
        beneficios=None,
        recrutador_id=None,
        mostrar_email_contato=True,
        mostrar_salario=True,
        mostrar_telefone_contato=False,
        quantidade_vagas=1,
    )
    job_expirado = EntityFactory.create_job_from_legacy(vaga_expirada_dto, id_mapper)
    assert job_expirado is not None
    assert job_expirado.status == JobStatus.CLOSED

    # Vaga com status "ABERTA" e data de encerramento no futuro deve continuar OPEN
    vaga_futura_dto = LegacyVagaDTO(
        id=61,
        empresa_id=10,
        titulo="Vaga Futura",
        descricao="Vaga ainda aberta",
        data_publicacao=now - timedelta(days=2),
        data_atualizacao=now - timedelta(days=2),
        data_encerramento=now + timedelta(days=15),
        segmento="TI",
        modalidade="REMOTO",
        tipo="CLT",
        pcd=False,
        escolaridade_minima=None,
        idade_minima=None,
        status="ABERTA",
        salario=3000.0,
        salario_maximo=None,
        beneficios=None,
        recrutador_id=None,
        mostrar_email_contato=True,
        mostrar_salario=True,
        mostrar_telefone_contato=False,
        quantidade_vagas=1,
    )
    job_futuro = EntityFactory.create_job_from_legacy(vaga_futura_dto, id_mapper)
    assert job_futuro is not None
    assert job_futuro.status == JobStatus.OPEN



def test_company_and_student_bundle_creation():
    id_mapper = InMemoryIdMapper()
    user_uuid = UUIDFactory.create_deterministic("user", 5)
    id_mapper.set_mapping("user", 5, user_uuid)

    company_dto = LegacyCompanyDTO(
        id=20,
        nome_fantasia="Tecnologia Senac",
        razao_social="Senac Tecnologia Ltda",
        cnpj="12.345.678/0001-99",
        telefone="79988776655",
        logradouro="Avenida Ivo do Prado",
        numero="564",
        complemento="Andar 2",
        bairro="Centro",
        cidade="Aracaju",
        estado="SE",
        cep="49010-050",
        parceira_senac=True,
        logo_url=None,
        website_url="https://senac.br",
        usuario_id=5,
        descricao="Empresa parceira de TI",
        status_aprovacao="APPROVED",
        data_criacao=None,
        data_atualizacao=None,
        email_contato="ti@senac.br",
        mostrar_email_contato=True,
        mostrar_telefone_contato=True,
    )

    addr, cont, phone, comp = EntityFactory.create_company_bundle(company_dto, id_mapper)
    assert addr.street == "Avenida Ivo do Prado"
    assert addr.number == 564
    assert str(comp.cnpj) == "12345678000199"
    assert cont.show_email is True
    assert phone.phone.ddd == "79"
    assert comp.is_senac_partner is True


def test_education_enums_match_database_constraints():
    from src.domain.enums.student_enums import StudentEducation
    from src.domain.enums.job_enums import JobEducation

    valid_db_values = {
        "FUNDAMENTAL_INCOMPLETO",
        "FUNDAMENTAL_COMPLETO",
        "MEDIO_INCOMPLETO",
        "MEDIO_COMPLETO",
        "TECNICO_INCOMPLETO",
        "TECNICO_COMPLETO",
        "SUPERIOR_INCOMPLETO",
        "SUPERIOR_COMPLETO",
        "POS_GRADUACAO",
        "MESTRADO",
        "DOUTORADO",
        "NAO_INFORMADO",
    }

    for item in StudentEducation:
        assert item.value in valid_db_values

    for item in JobEducation:
        assert item.value in valid_db_values

    assert StudentEducation.from_legacy("MÉDIO_COMPLETO").value == "MEDIO_COMPLETO"
    assert StudentEducation.from_legacy("ENSINO_SUPERIOR_COMPLETO").value == "SUPERIOR_COMPLETO"
    assert StudentEducation.COMPLETE_HIGH_SCHOOL.value == "MEDIO_COMPLETO"
    assert JobEducation.from_legacy("POS_GRADUACAO").value == "POS_GRADUACAO"
    assert JobEducation.POSTGRADUATE_DEGREE.value == "POS_GRADUACAO"


def test_job_short_title_and_description_normalization():
    id_mapper = InMemoryIdMapper()
    company_uuid = UUIDFactory.create_deterministic("company", 99)
    id_mapper.set_mapping("company", 99, company_uuid)

    # Vaga com título curto (< 4) e descrição curta (< 10)
    dto = LegacyVagaDTO(
        id=184,
        empresa_id=99,
        titulo="TI",
        descricao="atendente",
        data_publicacao=None,
        data_atualizacao=None,
        data_encerramento=None,
        segmento="Comércio",
        modalidade="PRESENCIAL",
        tipo="CLT",
        pcd=False,
        escolaridade_minima=None,
        idade_minima=None,
        status="ABERTO",
        salario=1500.0,
        salario_maximo=None,
        beneficios=None,
        recrutador_id=None,
        mostrar_email_contato=True,
        mostrar_salario=True,
        mostrar_telefone_contato=True,
        quantidade_vagas=1,
    )

    job = EntityFactory.create_job_from_legacy(dto, id_mapper)
    assert job is not None
    assert len(job.title) >= 4
    assert len(job.description) >= 10
    assert job.description == "Nesta vaga vai ser realizado atividades de: atendente"

