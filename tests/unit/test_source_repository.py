import pytest
from src.infrastructure.config.settings import DatabaseSettings
from src.infrastructure.database.source_sql_server_repository import SourceSqlServerRepository


def test_source_repository_blocks_non_select_queries():
    settings = DatabaseSettings(
        driver="ODBC Driver 18 for SQL Server",
        server="127.0.0.1",
        port=1440,
        name="RedeDeTalentos",
        user="sa",
        password="pwd",
        trust_server_certificate="yes",
        timeout=5,
        read_only=True,
    )
    repo = SourceSqlServerRepository(settings)

    # Queries válidas
    repo._assert_read_only_query("SELECT * FROM [dbo].[Usuario]")
    repo._assert_read_only_query("SELECT COUNT(*) FROM [dbo].[Empresa]")

    # Tentativas de operações modificadoras devem disparar PermissionError
    with pytest.raises(PermissionError):
        repo._assert_read_only_query("INSERT INTO [dbo].[Usuario] VALUES ('a')")

    with pytest.raises(PermissionError):
        repo._assert_read_only_query("UPDATE [dbo].[Usuario] SET Status = 0")

    with pytest.raises(PermissionError):
        repo._assert_read_only_query("DELETE FROM [dbo].[Usuario]")

    with pytest.raises(PermissionError):
        repo._assert_read_only_query("DROP TABLE [dbo].[Usuario]")

    with pytest.raises(PermissionError):
        repo._assert_read_only_query("CREATE TABLE [dbo].[Teste] (id INT)")

    with pytest.raises(PermissionError):
        repo._assert_read_only_query("ALTER TABLE [dbo].[Usuario] ADD Coluna INT")

    with pytest.raises(PermissionError):
        repo._assert_read_only_query("TRUNCATE TABLE [dbo].[Usuario]")

    with pytest.raises(PermissionError):
        repo._assert_read_only_query("SELECT 1; DROP TABLE [dbo].[Usuario]")

