import argparse
import sys
from src.infrastructure.config.settings import MigrationSettings, DatabaseSettings
from src.infrastructure.di.container import Container


class MigrationCLI:
    """
    Interface de Linha de Comando (CLI / Controller).
    Converte comandos e parâmetros do terminal em DTOs e orquestra a chamada aos Use Cases.
    NÃO contém regras de negócio.
    """

    @classmethod
    def create_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Rede de Talentos Senac SE • Script de Migração de Dados (SQL Server -> Novo Schema)",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        environment = parser.add_mutually_exclusive_group(required=True)
        environment.add_argument(
            "--dev", dest="environment", action="store_const", const="dev",
            help="Seleciona o destino de desenvolvimento (TARGET_DB_*).",
        )
        environment.add_argument(
            "--prod", dest="environment", action="store_const", const="prod",
            help="Seleciona o destino de produção (TARGET_PROD_DB_*).",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Executa em modo simulação: extrai, valida e mapeia os dados sem gravar no banco de destino.",
        )

        parser.add_argument(
            "--step",
            type=str,
            choices=["users", "companies", "students", "jobs", "curriculum", "applications", "notifications", "logs"],
            help="Executa exclusivamente uma etapa específica da migração.",
        )

        parser.add_argument(
            "--verify",
            action="store_true",
            help="Verifica a integridade da conexão com os bancos de dados de origem e destino e exibe as contagens.",
        )

        parser.add_argument(
            "--clean-target",
            action="store_true",
            help="Limpa as tabelas do destino selecionado, respeitando FKs; disponivel somente com --dev.",
        )

        parser.add_argument(
            "--source-db",
            type=str,
            help="Sobrescreve o nome do banco de dados de origem (padrão do .env: RedeDeTalentos).",
        )

        parser.add_argument(
            "--target-db",
            type=str,
            help="Sobrescreve o nome do banco selecionado por --dev ou --prod.",
        )

        parser.add_argument(
            "--batch-size",
            type=int,
            help="Quantidade de registros processados por lote de inserção.",
        )

        return parser

    @classmethod
    def run(cls, args_list: list | None = None) -> int:
        parser = cls.create_parser()
        args = parser.parse_args(args_list)

        if args.clean_target and args.dry_run:
            parser.error("--clean-target cannot be combined with --dry-run.")
        if args.clean_target and args.environment == "prod":
            parser.error("--clean-target is disabled for --prod to protect production data.")

        try:
            base_settings = MigrationSettings.load_from_env(args.environment)
        except ValueError as e:
            parser.error(str(e))

        # Sobrescrita por parâmetros da CLI
        source_name = args.source_db or base_settings.source_db.name
        target_name = args.target_db or base_settings.target_db.name
        batch_size = args.batch_size or base_settings.batch_size

        custom_source = DatabaseSettings(
            driver=base_settings.source_db.driver,
            server=base_settings.source_db.server,
            port=base_settings.source_db.port,
            name=source_name,
            user=base_settings.source_db.user,
            password=base_settings.source_db.password,
            trust_server_certificate=base_settings.source_db.trust_server_certificate,
            timeout=base_settings.source_db.timeout,
            read_only=True,
        )

        custom_target = DatabaseSettings(
            driver=base_settings.target_db.driver,
            server=base_settings.target_db.server,
            port=base_settings.target_db.port,
            name=target_name,
            user=base_settings.target_db.user,
            password=base_settings.target_db.password,
            trust_server_certificate=base_settings.target_db.trust_server_certificate,
            timeout=base_settings.target_db.timeout,
        )

        same_database = (
            custom_source.server.strip().lower() == custom_target.server.strip().lower()
            and custom_source.port == custom_target.port
            and custom_source.name.strip().lower() == custom_target.name.strip().lower()
        )
        if args.environment == "prod" and same_database:
            parser.error("Production source and target point to the same database; migration cancelled.")

        settings = MigrationSettings(
            batch_size=batch_size,
            omit_recruiters=base_settings.omit_recruiters,
            deterministic_uuid=base_settings.deterministic_uuid,
            source_db=custom_source,
            target_db=custom_target,
        )

        container = Container(settings)
        reporter = container.get_reporter()
        reporter.log_info(
            f"Ambiente selecionado: {'PRODUCAO' if args.environment == 'prod' else 'DESENVOLVIMENTO'}"
        )

        # Modo de verificação
        if args.verify:
            reporter.log_info(f"Testando conexão com banco de origem: [{source_name}]...")
            source_ok = container.get_source_db().test_connection()
            reporter.log_info(f"Conexão Origem [{source_name}]: {'OK (Ativo)' if source_ok else 'FALHA (Inacessível)'}")

            reporter.log_info(f"Testando conexão com banco de destino: [{target_name}]...")
            target_ok = container.get_target_db().test_connection()
            reporter.log_info(f"Conexão Destino [{target_name}]: {'OK (Ativo)' if target_ok else 'FALHA (Inacessível)'}")

            if source_ok:
                reporter.log_info("Contagem de registros no banco de Origem:")
                for k, v in container.get_source_db().get_row_counts().items():
                    print(f"  - {k:<20}: {v} linhas")

            schema_ok = False
            if target_ok:
                try:
                    database_name, missing_tables = container.get_target_db().get_target_schema_status()
                    if missing_tables:
                        reporter.log_error(
                            f"Schema incompleto no banco de destino [{database_name}]. "
                            f"Tabelas ausentes: {', '.join(missing_tables)}"
                        )
                    else:
                        schema_ok = True
                        reporter.log_info(f"Schema de destino [{database_name}]: OK")
                except Exception as e:
                    reporter.log_error(f"Não foi possível verificar o schema de destino: {e}", e)
                reporter.log_info("Contagem de registros no banco de Destino:")
                for k, v in container.get_target_db().get_row_counts().items():
                    print(f"  - {k:<20}: {v} linhas")

            return 0 if (source_ok and target_ok and schema_ok) else 1

        if not args.dry_run:
            try:
                database_name, missing_tables = container.get_target_db().get_target_schema_status()
            except Exception as e:
                reporter.log_error(f"Nao foi possivel verificar o schema do banco de destino: {e}", e)
                return 1

            if missing_tables:
                reporter.log_error(
                    f"Migracao cancelada antes de gravar dados: o schema do banco [{database_name}] "
                    f"esta incompleto. Tabelas ausentes: {', '.join(missing_tables)}. "
                    "Inicialize o schema do backend nesse banco e execute novamente."
                )
                return 1

            reporter.log_info(f"Schema do banco de destino [{database_name}]: OK")

        if args.clean_target:
            reporter.log_warning(f"Limpando registros residuais do banco de destino [{target_name}] respeitando FKs...")
            container.get_target_db().clean_target_tables()
            reporter.log_info(f"Limpeza de [{target_name}] finalizada com sucesso.")

        # Executa a migracao
        orchestrator = container.get_orchestrator()
        result = orchestrator.execute(dry_run=args.dry_run, specific_step=args.step)

        return 0 if result.get("total_errors", 0) == 0 else 1
