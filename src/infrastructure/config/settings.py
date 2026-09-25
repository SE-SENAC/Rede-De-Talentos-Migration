import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback seguro para leitura de .env sem biblioteca externa
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k not in os.environ:
                        os.environ[k] = v


@dataclass(frozen=True)
class DatabaseSettings:
    driver: str
    server: str
    port: int
    name: str
    user: str
    password: str
    trust_server_certificate: str
    timeout: int
    read_only: bool = False

    @property
    def connection_string(self) -> str:
        conn_str = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.name};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"TrustServerCertificate={self.trust_server_certificate};"
        )
        if self.read_only:
            conn_str += "ApplicationIntent=ReadOnly;"
        return conn_str


@dataclass(frozen=True)
class MigrationSettings:
    batch_size: int
    omit_recruiters: bool
    deterministic_uuid: bool
    source_db: DatabaseSettings
    target_db: DatabaseSettings

    @classmethod
    def load_from_env(cls) -> "MigrationSettings":
        source_db = DatabaseSettings(
            driver=os.getenv("SOURCE_DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            server=os.getenv("SOURCE_DB_SERVER", "127.0.0.1"),
            port=int(os.getenv("SOURCE_DB_PORT", "1440")),
            name=os.getenv("SOURCE_DB_NAME", "RedeDeTalentos"),
            user=os.getenv("SOURCE_DB_USER", "sa"),
            password=os.getenv("SOURCE_DB_PASSWORD", "SenacDRSE@2026"),
            trust_server_certificate=os.getenv("SOURCE_DB_TRUST_SERVER_CERTIFICATE", "yes"),
            timeout=int(os.getenv("SOURCE_DB_TIMEOUT", "15")),
            read_only=True,  # Banco de Origem SEMPRE estritamente somente leitura
        )

        target_db = DatabaseSettings(
            driver=os.getenv("TARGET_DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            server=os.getenv("TARGET_DB_SERVER", "127.0.0.1"),
            port=int(os.getenv("TARGET_DB_PORT", "1440")),
            name=os.getenv("TARGET_DB_NAME", "RedeDeTalentos_DEV"),
            user=os.getenv("TARGET_DB_USER", "sa"),
            password=os.getenv("TARGET_DB_PASSWORD", "SenacDRSE@2026"),
            trust_server_certificate=os.getenv("TARGET_DB_TRUST_SERVER_CERTIFICATE", "yes"),
            timeout=int(os.getenv("TARGET_DB_TIMEOUT", "15")),
            read_only=False,
        )

        return cls(
            batch_size=int(os.getenv("MIGRATION_BATCH_SIZE", "250")),
            omit_recruiters=os.getenv("MIGRATION_OMIT_RECRUITERS", "true").lower() in ("true", "1", "yes"),
            deterministic_uuid=os.getenv("MIGRATION_DETERMINISTIC_UUID", "true").lower() in ("true", "1", "yes"),
            source_db=source_db,
            target_db=target_db,
        )
