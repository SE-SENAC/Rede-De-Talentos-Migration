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

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Executa em modo simulação: extrai, valida e mapeia os dados sem gravar no banco de destino.",
        )

        parser.add_argument(
            "--step",
            type=str,
            choices=["users", "companies", "students", "jobs", "curriculum", "applications", "notifications", "logs", "seed_credentials"],
            help="Executa exclusivamente uma etapa específica da migração.",
        )

        parser.add_argument(
            "--seed-credentials",
            action="store_true",
            help="Executa o seed de credenciais de desenvolvimento (admin, superadmin, empresa, aluno) no banco de destino.",
        )

        parser.add_argument(
            "--verify",
            action="store_true",
            help="Verifica a integridade da conexão com os bancos de dados de origem e destino e exibe as contagens.",
        )

        parser.add_argument(
            "--clean-target",
            action="store_true",
            help="Limpa com segurança todas as tabelas de destino (RedeDeTalentos_DEV) respeitando FKs antes da migração.",
        )

        parser.add_argument(
            "--source-db",
            type=str,
            help="Sobrescreve o nome do banco de dados de origem (padrão do .env: RedeDeTalentos).",
        )

        parser.add_argument(
            "--target-db",
            type=str,
            help="Sobrescreve o nome do banco de dados de destino (padrão do .env: RedeDeTalentos_DEV).",
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

        base_settings = MigrationSettings.load_from_env()

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

        settings = MigrationSettings(
            batch_size=batch_size,
            omit_recruiters=base_settings.omit_recruiters,
            deterministic_uuid=base_settings.deterministic_uuid,
            source_db=custom_source,
            target_db=custom_target,
        )

        container = Container(settings)
        reporter = container.get_reporter()

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

            if target_ok:
                reporter.log_info("Contagem de registros no banco de Destino:")
                for k, v in container.get_target_db().get_row_counts().items():
                    print(f"  - {k:<20}: {v} linhas")

            return 0 if (source_ok and target_ok) else 1

        # Limpeza prévia segura do banco de destino (se solicitado)
        if args.clean_target:
            reporter.log_warning(f"Limpando registros residuais do banco de destino [{target_name}] respeitando FKs...")
            container.get_target_db().clean_target_tables()
            reporter.log_info(f"Limpeza de [{target_name}] finalizada com sucesso.")

        # Execução de migração ou seed
        specific_step = "seed_credentials" if args.seed_credentials else args.step
        orchestrator = container.get_orchestrator()
        result = orchestrator.execute(dry_run=args.dry_run, specific_step=specific_step)

        return 0 if result.get("total_errors", 0) == 0 else 1

