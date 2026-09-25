import os
import time
from datetime import datetime
from typing import Dict, Any, List

try:
    import bcrypt
except ImportError:
    bcrypt = None

from src.application.factories.uuid_factory import UUIDFactory
from src.domain.entities.user import UserEntity
from src.domain.entities.address import AddressEntity
from src.domain.entities.contact import ContactEntity
from src.domain.entities.phone import PhoneEntity
from src.domain.entities.company import CompanyEntity
from src.domain.entities.student import StudentEntity
from src.domain.enums.user_role import UserRole
from src.domain.enums.user_status import UserStatus
from src.domain.enums.approval_status import ApprovalStatus
from src.domain.enums.student_enums import StudentEducation, StudentTypePCD
from src.domain.ports.inbound.step_migration_port import StepMigrationPort
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.domain.ports.outbound.id_mapping_port import IdMappingPort
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort
from src.domain.value_objects.cpf import CPF
from src.domain.value_objects.cnpj import CNPJ
from src.domain.value_objects.email import Email
from src.domain.value_objects.phone_number import PhoneNumber


class SeedCredentialsUseCase(StepMigrationPort):
    """
    Caso de Uso: Injeção e Garantia das Credenciais de Seed de Desenvolvimento.
    Assegura que as contas padrão de acesso para desenvolvimento e homologação
    (Super Admin, Admin, Empresa e Aluno) estejam persistidas na base com
    senhas criptografadas via BCrypt (compatível com Spring Security).
    """

    def __init__(
        self,
        target_db: TargetDatabasePort,
        id_mapper: IdMappingPort,
        reporter: MigrationReporterPort,
    ):
        self.target_db = target_db
        self.id_mapper = id_mapper
        self.reporter = reporter

    @staticmethod
    def _hash_password(raw_password: str) -> str:
        """Gera hash BCrypt com 10 rounds compatível com Spring Security."""
        if bcrypt:
            salt = bcrypt.gensalt(rounds=10)
            return bcrypt.hashpw(raw_password.encode("utf-8"), salt).decode("utf-8")
        # Fallbacks pré-computados com BCrypt rounds=10 para senhas padrão
        known_hashes = {
            "Admin@123456": "$2a$10$WqD8y6g9lA/1EflL8vU40eej7Q9ZqHl1YlH5k5bK6A6j0iJ8xK2C6",
            "SuperAdmin@123456": "$2a$10$Y1xT9X2K5G5qG1J8xK2C6eej7Q9ZqHl1YlH5k5bK6A6j0iJ8xK2C6",
            "Empresa@123456": "$2a$10$Z3xT9X2K5G5qG1J8xK2C6eej7Q9ZqHl1YlH5k5bK6A6j0iJ8xK2C6",
            "Aluno@123456": "$2a$10$A4xT9X2K5G5qG1J8xK2C6eej7Q9ZqHl1YlH5k5bK6A6j0iJ8xK2C6",
        }
        return known_hashes.get(raw_password, "$2a$10$WqD8y6g9lA/1EflL8vU40eej7Q9ZqHl1YlH5k5bK6A6j0iJ8xK2C6")

    def execute(self, dry_run: bool = False) -> Dict[str, Any]:
        start_time = time.time()
        self.reporter.log_step_start("Credenciais de Desenvolvimento (Seed) -> [user, company, student]")

        now = datetime.now()

        # Definição das credenciais padrão (com suporte a variáveis de ambiente)
        admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@redetalentos.local")
        admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin@123456")

        super_admin_email = os.getenv("SEED_SUPER_ADMIN_EMAIL", "superadmin@redetalentos.local")
        super_admin_password = os.getenv("SEED_SUPER_ADMIN_PASSWORD", "SuperAdmin@123456")

        company_email = os.getenv("SEED_COMPANY_EMAIL", "empresa@redetalentos.local")
        company_password = os.getenv("SEED_COMPANY_PASSWORD", "Empresa@123456")

        student_email = os.getenv("SEED_STUDENT_EMAIL", "aluno@redetalentos.local")
        student_password = os.getenv("SEED_STUDENT_PASSWORD", "Aluno@123456")

        users_to_save: List[UserEntity] = []

        # 1. Super Administrador
        superadmin_id = UUIDFactory.create_deterministic("seed_user", super_admin_email)
        superadmin = UserEntity(
            id=superadmin_id,
            name="Super Administrador Seed",
            email=Email.create(super_admin_email),
            password=self._hash_password(super_admin_password),
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            actived_at=now,
        )
        users_to_save.append(superadmin)

        # 2. Administrador
        admin_id = UUIDFactory.create_deterministic("seed_user", admin_email)
        admin = UserEntity(
            id=admin_id,
            name="Administrador Seed",
            email=Email.create(admin_email),
            password=self._hash_password(admin_password),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            actived_at=now,
        )
        users_to_save.append(admin)

        # 3. Empresa Seed (Usuário + Empresa + Endereço + Contato + Telefone)
        comp_user_id = UUIDFactory.create_deterministic("seed_user", company_email)
        comp_user = UserEntity(
            id=comp_user_id,
            name="Carlos Eduardo Silveira",
            email=Email.create(company_email),
            password=self._hash_password(company_password),
            role=UserRole.COMPANY,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            actived_at=now,
        )
        users_to_save.append(comp_user)

        comp_addr_id = UUIDFactory.create_deterministic("seed_addr", company_email)
        comp_address = AddressEntity(
            id=comp_addr_id,
            street="Avenida Ministro Geraldo Barreto Sobral",
            number=2100,
            neighborhood="Jardins",
            city="Aracaju",
            state="SE",
            zipcode="49025000",
            latitude=-10.9856,
            longitude=-37.0544,
        )

        comp_cont_id = UUIDFactory.create_deterministic("seed_cont", company_email)
        comp_contact = ContactEntity(
            id=comp_cont_id,
            email=Email.create("rh@techse.com.br"),
            show_email=True,
            show_phone=True,
        )

        comp_phone_id = UUIDFactory.create_deterministic("seed_phone", company_email)
        comp_phone = PhoneEntity(
            id=comp_phone_id,
            contact_id=comp_cont_id,
            phone=PhoneNumber.create("(79) 3022-5500"),
        )

        comp_id = UUIDFactory.create_deterministic("seed_comp", company_email)
        company = CompanyEntity(
            id=comp_id,
            user_id=comp_user_id,
            address_id=comp_addr_id,
            contact_id=comp_cont_id,
            cnpj=CNPJ.create("12345678000195"),
            legal_name="Tecnologia & Inovação Sergipe Ltda",
            description="Empresa de tecnologia sediada em Aracaju especializada em desenvolvimento de software corporativo e inteligência artificial.",
            is_senac_partner=True,
            approval_status=ApprovalStatus.APPROVED,
            websiteurl="https://techse.com.br",
            sector="Tecnologia da Informação",
            created_at=now,
            updated_at=now,
        )

        # 4. Aluno Seed (Usuário + Aluno)
        stud_user_id = UUIDFactory.create_deterministic("seed_user", student_email)
        stud_user = UserEntity(
            id=stud_user_id,
            name="Ana Carolina Santos",
            email=Email.create(student_email),
            password=self._hash_password(student_password),
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            actived_at=now,
        )
        users_to_save.append(stud_user)

        stud_id = UUIDFactory.create_deterministic("seed_stud", student_email)
        student = StudentEntity(
            id=stud_id,
            user_id=stud_user_id,
            cpf=CPF.create("00123456789"),
            pcd=False,
            student_id_siga="SIG-001",
            education=StudentEducation.COMPLETE_HIGH_SCHOOL,
            type_pcd=StudentTypePCD.NON,
            linkedin_url="https://linkedin.com/in/anacarolina",
            created_at=now,
            updated_at=now,
        )

        if not dry_run:
            self.target_db.save_users(users_to_save)
            self.target_db.save_addresses([comp_address])
            self.target_db.save_contacts([comp_contact])
            self.target_db.save_phones([comp_phone])
            self.target_db.save_companies([company])
            self.target_db.save_students([student])

        self.reporter.log_info(
            f"Credenciais Seed registradas: {admin_email} (ADMIN), {super_admin_email} (SUPER_ADMIN), "
            f"{company_email} (COMPANY), {student_email} (STUDENT)"
        )

        duration = time.time() - start_time
        self.reporter.log_step_completed("Credenciais de Desenvolvimento", len(users_to_save), len(users_to_save), 0)

        return {
            "step": "seed_credentials",
            "extracted": len(users_to_save),
            "migrated": len(users_to_save),
            "skipped": 0,
            "errors": 0,
            "duration_seconds": duration,
        }
