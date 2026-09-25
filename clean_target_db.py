"""
Script utilitário para limpeza completa e segura do banco de dados de destino (RedeDeTalentos_DEV).
Executa DELETE em cascata respeitando a integridade referencial de chaves estrangeiras.
"""
from src.infrastructure.config.settings import MigrationSettings
from src.infrastructure.database.target_sql_server_repository import TargetSqlServerRepository

if __name__ == "__main__":
    settings = MigrationSettings.load_from_env()
    repo = TargetSqlServerRepository(settings.target_db)
    print(f"Limpando todas as tabelas em [{settings.target_db.name}] ({settings.target_db.server}:{settings.target_db.port})...")
    repo.clean_target_tables()
    print("Contagem final após limpeza:")
    for table, count in repo.get_row_counts().items():
        print(f"  {table:<15}: {count}")
    print("Banco de destino zerado e pronto para migração completa!")

