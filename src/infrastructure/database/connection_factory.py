import pyodbc
from src.infrastructure.config.settings import DatabaseSettings


class ConnectionFactory:
    """
    Fábrica de conexões com o Microsoft SQL Server utilizando pyodbc.
    """

    @staticmethod
    def create_connection(settings: DatabaseSettings) -> pyodbc.Connection:
        try:
            conn = pyodbc.connect(
                settings.connection_string,
                timeout=settings.timeout,
                readonly=settings.read_only
            )
            return conn
        except Exception as e:
            raise ConnectionError(
                f"Falha ao conectar ao banco de dados [{settings.name}] em {settings.server}:{settings.port}: {e}"
            ) from e

