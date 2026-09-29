import re
from typing import Generator, Any, Dict
from src.domain.ports.outbound.source_database_port import SourceDatabasePort
from src.infrastructure.config.settings import DatabaseSettings
from src.infrastructure.database.connection_factory import ConnectionFactory


class SourceSqlServerRepository(SourceDatabasePort):
    """
    Repositório de infraestrutura para leitura do banco legado (RedeDeTalentos).
    SEGURANÇA ESTRITA:
    - Este repositório é 100% SOMENTE LEITURA.
    - Qualquer tentativa de CREATE, ALTER, DROP, INSERT, UPDATE, DELETE ou TRUNCATE
      é bloqueada imediatamente por guardrail antes do envio ao SGBD.
    - Utiliza nível de isolamento READ UNCOMMITTED (sem locks na origem).
    """

    def __init__(self, settings: DatabaseSettings):
        self.settings = settings

    def _assert_read_only_query(self, query: str) -> None:
        """
        Guardrail de segurança: assegura que apenas instruções SELECT sejam executadas.
        """
        cleaned = query.strip()
        if not cleaned.upper().startswith("SELECT"):
            raise PermissionError(
                f"[SEGURANÇA] Tentativa de execução de comando não-SELECT no banco de origem: '{query[:50]}...'. "
                f"O banco legado é estritamente somente leitura!"
            )
        # Proteção contra injeção de DDL/DML multi-statement
        forbidden = [
            r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b",
            r"\bCREATE\b", r"\bALTER\b", r"\bTRUNCATE\b", r"\bEXEC\b",
            r"\bEXECUTE\b", r"\bMERGE\b", r"\bBACKUP\b", r"\bRESTORE\b"
        ]
        for pattern in forbidden:
            if re.search(pattern, cleaned, re.IGNORECASE):
                raise PermissionError(
                    f"[SEGURANÇA] Palavra-chave modificadora proibida detectada na consulta: {pattern}. "
                    f"Operação cancelada para proteção do banco de origem."
                )

    def test_connection(self) -> bool:
        try:
            with ConnectionFactory.create_connection(self.settings) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return cursor.fetchone() is not None
        except Exception:
            return False

    def _query_table(self, table_name: str) -> Generator[Dict[str, Any], None, None]:
        query = f"SELECT * FROM [dbo].[{table_name}]"
        self._assert_read_only_query(query)

        with ConnectionFactory.create_connection(self.settings) as conn:
            cursor = conn.cursor()
            # Garante isolamento sem lock no banco legado de produção
            cursor.execute("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
            try:
                cursor.execute(query)
            except Exception:
                # Caso a tabela não exista ou haja erro de permissão na origem
                return

            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                if columns:
                    pk_val = row[0]
                    row_dict["_pk"] = pk_val
                    if "Id" not in row_dict or row_dict["Id"] is None:
                        row_dict["Id"] = pk_val
                # Cria aliases normalizados para evitar problemas de case e acentuação/encoding
                for col_name, val in list(row_dict.items()):
                    if isinstance(col_name, str):
                        clean_name = (
                            col_name.lower()
                            .replace("ç", "c")
                            .replace("ã", "a")
                            .replace("á", "a")
                            .replace("é", "e")
                            .replace("í", "i")
                            .replace("ó", "o")
                            .replace("ú", "u")
                        )
                        if clean_name not in row_dict:
                            row_dict[clean_name] = val
                yield row_dict

    def get_row_counts(self) -> Dict[str, int]:
        counts = {}
        tables = [
            "Usuario", "Admin", "Empresa", "Recruiter", "Students",
            "Vaga", "Experiencias", "Idiomas", "Inscricao", "Notification",
            "Qualificacoes", "LogAdmin", "LogJob", "LogUser"
        ]
        with ConnectionFactory.create_connection(self.settings) as conn:
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
            for table in tables:
                query = f"SELECT COUNT(*) FROM [dbo].[{table}]"
                self._assert_read_only_query(query)
                try:
                    cursor.execute(query)
                    counts[table] = cursor.fetchone()[0]
                except Exception:
                    counts[table] = 0
        return counts

    def get_usuarios(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Usuario")

    def get_admins(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Admin")

    def get_empresas(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Empresa")

    def get_recruiters(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Recruiter")

    def get_students(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Students")

    def get_vagas(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Vaga")

    def get_experiencias(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Experiencias")

    def get_idiomas(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Idiomas")

    def get_qualificacoes(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Qualificacoes")

    def get_inscricoes(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Inscricao")

    def get_notifications(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("Notification")

    def get_logs_admin(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("LogAdmin")

    def get_logs_job(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("LogJob")

    def get_logs_user(self) -> Generator[Dict[str, Any], None, None]:
        return self._query_table("LogUser")
