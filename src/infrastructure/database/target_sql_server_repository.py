from typing import List, Dict, Any, Tuple
from src.domain.entities.user import UserEntity
from src.domain.entities.address import AddressEntity
from src.domain.entities.contact import ContactEntity
from src.domain.entities.phone import PhoneEntity
from src.domain.entities.company import CompanyEntity
from src.domain.entities.student import StudentEntity
from src.domain.entities.job import JobEntity
from src.domain.entities.curriculum import ExperienceEntity, LanguageEntity, QualificationEntity
from src.domain.entities.application import ApplicationEntity
from src.domain.entities.notification import NotificationEntity
from src.domain.entities.log import LogEntity
from src.domain.ports.outbound.target_database_port import TargetDatabasePort
from src.infrastructure.config.settings import DatabaseSettings
from src.infrastructure.database.connection_factory import ConnectionFactory


class TargetSqlServerRepository(TargetDatabasePort):
    """
    Repositório de infraestrutura para persistência de dados no novo schema (RedeDeTalentos_DEV).
    Utiliza transações atômicas, inserções em lote parametrizadas via executemany
    e fallback resiliente linha por linha para garantir idempotência sem abortar a migração.
    """

    def __init__(self, settings: DatabaseSettings):
        self.settings = settings

    def test_connection(self) -> bool:
        try:
            with ConnectionFactory.create_connection(self.settings) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return cursor.fetchone() is not None
        except Exception:
            return False

    def get_row_counts(self) -> Dict[str, int]:
        counts = {}
        tables = [
            "user", "company", "address", "contact", "phone", "student",
            "job", "applications", "experience", "language", "qualification",
            "notification", "log", "feedbacks"
        ]
        with ConnectionFactory.create_connection(self.settings) as conn:
            cursor = conn.cursor()
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM [dbo].[{table}]")
                    counts[table] = cursor.fetchone()[0]
                except Exception:
                    counts[table] = 0
        return counts

    def clean_target_tables(self) -> None:
        """
        Remove todos os registros das tabelas do banco de destino respeitando
        a ordem estrita de integridade referencial (chaves estrangeiras).
        """
        delete_order = [
            "feedbacks",
            "applications",
            "qualification",
            "language",
            "experience",
            "job",
            "student",
            "company",
            "phone",
            "contact",
            "address",
            "notification",
            "log",
            "user",
        ]
        with ConnectionFactory.create_connection(self.settings) as conn:
            cursor = conn.cursor()
            for table in delete_order:
                try:
                    cursor.execute(f"DELETE FROM [dbo].[{table}]")
                except Exception:
                    pass
            conn.commit()

    def _execute_batch_resilient(self, sql: str, params: List[Tuple[Any, ...]], table_name: str = "") -> int:
        """
        Executa inserção em lote de alta performance.
        Caso ocorra erro de integridade (ex: duplicidade de chave primária ou índice único),
        aciona fallback resiliente inserindo linha-a-linha e ignorando registros conflitantes.
        """
        if not params:
            return 0

        with ConnectionFactory.create_connection(self.settings) as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(sql, params)
                conn.commit()
                return len(params)
            except Exception:
                conn.rollback()

            # Fallback seguro linha por linha
            saved = 0
            last_error = None
            for row in params:
                try:
                    cursor.execute(sql, row)
                    conn.commit()
                    saved += 1
                except Exception as row_e:
                    conn.rollback()
                    last_error = row_e

            if saved < len(params) and last_error:
                import sys
                print(
                    f"[AVISO-BD] Tabela [{table_name}]: {saved}/{len(params)} registros salvos. Último erro detectado: {last_error}",
                    file=sys.stderr,
                )

            return saved

    def save_users(self, users: List[UserEntity]) -> int:
        if not users:
            return 0
        sql = """
        INSERT INTO [dbo].[user] (
            id, name, email, password, role, status, created_at, updated_at,
            actived_at, re_actived_at, deactived_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            (
                str(u.id), u.name, str(u.email), u.password, u.role.value, u.status.value,
                u.created_at, u.updated_at, u.actived_at, u.re_actived_at, u.deactived_at
            )
            for u in users
        ]
        return self._execute_batch_resilient(sql, params, "user")

    def save_addresses(self, addresses: List[AddressEntity]) -> int:
        if not addresses:
            return 0
        sql = """
        INSERT INTO [dbo].[address] (
            id, street, number, neighborhood, city, state, complement, zipcode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            (
                str(a.id), a.street, a.number, a.neighborhood, a.city, a.state,
                a.complement, a.zipcode
            )
            for a in addresses
        ]
        update_sql = """
        UPDATE [dbo].[address]
        SET street = ?, number = ?, neighborhood = ?, city = ?, state = ?, complement = ?, zipcode = ?
        WHERE id = ?
        """
        return self._execute_upsert_resilient(sql, update_sql, params, "address")

    def save_contacts(self, contacts: List[ContactEntity]) -> int:
        if not contacts:
            return 0
        sql = """
        INSERT INTO [dbo].[contact] (
            id, email, show_email, show_phone
        ) VALUES (?, ?, ?, ?)
        """
        params = [
            (str(c.id), str(c.email), 1 if c.show_email else 0, 1 if c.show_phone else 0)
            for c in contacts
        ]
        update_sql = """
        UPDATE [dbo].[contact]
        SET email = ?, show_email = ?, show_phone = ?
        WHERE id = ?
        """
        return self._execute_upsert_resilient(sql, update_sql, params, "contact")

    def save_phones(self, phones: List[PhoneEntity]) -> int:
        if not phones:
            return 0
        sql = """
        INSERT INTO [dbo].[phone] (
            id, contact_id, ddi, ddd, number
        ) VALUES (?, ?, ?, ?, ?)
        """
        params = [
            (str(p.id), str(p.contact_id), p.phone.ddi, p.phone.ddd, p.phone.number)
            for p in phones
        ]
        update_sql = """
        UPDATE [dbo].[phone]
        SET contact_id = ?, ddi = ?, ddd = ?, number = ?
        WHERE id = ?
        """
        return self._execute_upsert_resilient(sql, update_sql, params, "phone")

    def _execute_upsert_resilient(
        self,
        insert_sql: str,
        update_sql: str,
        params: List[Tuple[Any, ...]],
        table_name: str,
    ) -> int:
        """Insere registros novos e atualiza IDs existentes para permitir reexecução."""
        if not params:
            return 0

        written = 0
        with ConnectionFactory.create_connection(self.settings) as conn:
            cursor = conn.cursor()
            try:
                for row in params:
                    # O primeiro parâmetro do INSERT é sempre o ID; no UPDATE ele vem por último.
                    cursor.execute(update_sql, *row[1:], row[0])
                    if cursor.rowcount == 0:
                        cursor.execute(insert_sql, *row)
                    written += 1
                conn.commit()
                return written
            except Exception as e:
                conn.rollback()
                raise RuntimeError(f"Falha ao persistir lote da tabela [{table_name}]: {e}") from e

    def save_companies(self, companies: List[CompanyEntity]) -> int:
        if not companies:
            return 0
        sql = """
        INSERT INTO [dbo].[company] (
            id, user_id, address_id, contact_id, cnpj, legal_name, trade_name, description,
            sector, state_registration, municipal_registration, is_senac_partner,
            approval_status, websiteurl, logourl, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            (
                str(c.id), str(c.user_id), str(c.address_id) if c.address_id else None,
                str(c.contact_id) if c.contact_id else None, str(c.cnpj), c.legal_name,
                c.trade_name, c.description, c.sector, c.state_registration, c.municipal_registration,
                1 if c.is_senac_partner else 0, c.approval_status.value, c.websiteurl,
                c.logourl, c.created_at, c.updated_at
            )
            for c in companies
        ]
        update_sql = """
        UPDATE [dbo].[company]
        SET user_id = ?, address_id = ?, contact_id = ?, cnpj = ?, legal_name = ?,
            trade_name = ?, description = ?, sector = ?, state_registration = ?,
            municipal_registration = ?, is_senac_partner = ?, approval_status = ?,
            websiteurl = ?, logourl = ?, created_at = ?, updated_at = ?
        WHERE id = ?
        """
        written = 0
        with ConnectionFactory.create_connection(self.settings) as conn:
            cursor = conn.cursor()
            for row in params:
                company_id = row[0]
                update_params = (*row[1:], company_id)
                try:
                    cursor.execute(update_sql, *update_params)
                    if cursor.rowcount == 0:
                        cursor.execute(sql, *row)
                    conn.commit()
                    written += 1
                except Exception:
                    conn.rollback()
                    raise
        return written

    def save_students(self, students: List[StudentEntity]) -> int:
        if not students:
            return 0
        sql = """
        INSERT INTO [dbo].[student] (
            id, user_id, contact_id, avatar_url, cpf, pcd, type_pcd, education,
            student_id_siga, linkedin_url, portfolio, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            (
                str(s.id), str(s.user_id), str(s.contact_id) if s.contact_id else None,
                s.avatar_url, str(s.cpf), 1 if s.pcd else 0,
                s.type_pcd.value if s.type_pcd else None,
                s.education.value if s.education else None,
                s.student_id_siga, s.linkedin_url, s.portfolio,
                s.created_at, s.updated_at
            )
            for s in students
        ]
        return self._execute_batch_resilient(sql, params, "student")

    def save_jobs(self, jobs: List[JobEntity]) -> int:
        if not jobs:
            return 0
        sql = """
        INSERT INTO [dbo].[job] (
            id, company_id, title, description, segment, work_mode, type, pcd,
            minimum_education, minimum_age, status, salary, maximum_salary,
            number_of_openings, show_contact_email, show_contact_phone,
            show_salary, benefits, skills, closing_date,
            published_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            (
                str(j.id), str(j.company_id), j.title, j.description, j.segment,
                j.work_mode.value, j.type.value, 1 if j.pcd else 0,
                j.minimum_education.value, j.minimum_age, j.status.value,
                j.salary, j.maximum_salary, j.number_of_openings,
                1 if j.show_contact_email else 0, 1 if j.show_contact_phone else 0,
                1 if j.show_salary else 0, j.benefits, j.skills,
                j.closing_date, j.published_at, j.updated_at
            )
            for j in jobs
        ]
        return self._execute_batch_resilient(sql, params, "job")

    def save_experiences(self, experiences: List[ExperienceEntity]) -> int:
        if not experiences:
            return 0
        sql = """
        INSERT INTO [dbo].[experience] (
            id, user_id, empresa, cargo, descricao, data_inicio, data_fim, atual, criado_em, atualizado_em
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            (
                str(e.id), str(e.user_id), e.empresa, e.cargo, e.descricao,
                e.data_inicio, e.data_fim, 1 if e.atual else 0, e.criado_em, e.atualizado_em
            )
            for e in experiences
        ]
        return self._execute_batch_resilient(sql, params, "experience")

    def save_languages(self, languages: List[LanguageEntity]) -> int:
        if not languages:
            return 0
        sql = """
        INSERT INTO [dbo].[language] (
            id, user_id, idioma, nivel, criado_em, atualizado_em
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = [
            (str(l.id), str(l.user_id), l.idioma, l.nivel, l.criado_em, l.atualizado_em)
            for l in languages
        ]
        return self._execute_batch_resilient(sql, params, "language")

    def save_qualifications(self, qualifications: List[QualificationEntity]) -> int:
        if not qualifications:
            return 0
        sql = """
        INSERT INTO [dbo].[qualification] (
            id, user_id, titulo, curso, instituicao, descricao, data_inicio, data_fim,
            em_andamento, criado_em, atualizado_em
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            (
                str(q.id), str(q.user_id), q.titulo, q.curso, q.instituicao,
                q.descricao, q.data_inicio, q.data_fim, 1 if q.em_andamento else 0,
                q.criado_em, q.atualizado_em
            )
            for q in qualifications
        ]
        return self._execute_batch_resilient(sql, params, "qualification")

    def save_applications(self, applications: List[ApplicationEntity]) -> int:
        if not applications:
            return 0
        sql = """
        INSERT INTO [dbo].[applications] (
            id, job_id, student_id, applied_at, status, status_changed_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = [
            (
                str(a.id), str(a.job_id), str(a.student_id), a.applied_at,
                a.status.value, a.status_changed_at
            )
            for a in applications
        ]
        return self._execute_batch_resilient(sql, params, "applications")

    def save_notifications(self, notifications: List[NotificationEntity]) -> int:
        if not notifications:
            return 0
        sql = """
        INSERT INTO [dbo].[notification] (
            id, user_id, title, content, type, is_read, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            (
                str(n.id), str(n.user_id), n.title, n.content, n.type,
                1 if n.is_read else 0, n.status, n.created_at, n.updated_at
            )
            for n in notifications
        ]
        return self._execute_batch_resilient(sql, params, "notification")

    def save_logs(self, logs: List[LogEntity]) -> int:
        if not logs:
            return 0
        params = [
            (
                str(l.id), l.user_id, l.type_name, l.user_name, l.type_action,
                l.description, l.reason, l.message, l.ip_address,
                l.created_at, l.updated_at
            )
            for l in logs
        ]
        # A migração é reexecutável: os UUIDs determinísticos já existentes precisam
        # ser atualizados para refletir o novo mapeamento, em vez de ignorados por PK.
        update_sql = """
        UPDATE [dbo].[log]
        SET user_id = ?, type_name = ?, user_name = ?, type_action = ?,
            description = ?, reason = ?, message = ?, ip_address = ?,
            created_at = ?, updated_at = ?
        WHERE id = ?
        """
        insert_sql = """
        INSERT INTO [dbo].[log] (
            id, user_id, type_name, user_name, type_action, description,
            reason, message, ip_address, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        written = 0
        with ConnectionFactory.create_connection(self.settings) as conn:
            cursor = conn.cursor()
            for row in params:
                log_id, user_id, type_name, user_name, type_action, description, reason, message, ip_address, created_at, updated_at = row
                try:
                    cursor.execute(update_sql, user_id, type_name, user_name, type_action, description,
                                   reason, message, ip_address, created_at, updated_at, log_id)
                    if cursor.rowcount == 0:
                        cursor.execute(insert_sql, *row)
                    conn.commit()
                    written += 1
                except Exception:
                    conn.rollback()
                    raise
        return written
