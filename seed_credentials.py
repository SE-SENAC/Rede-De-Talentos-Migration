"""
Script dedicado para injeção de credenciais de desenvolvimento/teste no banco de destino.
Pode ser executado diretamente via:
    python seed_credentials.py
ou via CLI principal:
    python main.py --seed-credentials
"""
import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.config.settings import MigrationSettings
from src.infrastructure.di.container import Container


def main():
    print("=" * 60)
    print("  REDE DE TALENTOS SENAC SE • SEED DE CREDENCIAIS DE TESTE")
    print("=" * 60)
    
    settings = MigrationSettings.load_from_env()
    container = Container(settings)
    reporter = container.get_reporter()
    
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        reporter.log_info("Modo de simulação ativado (--dry-run). Nenhuma gravação será feita.")
        
    orchestrator = container.get_orchestrator()
    result = orchestrator.execute(dry_run=dry_run, specific_step="seed_credentials")
    
    total_errors = result.get("total_errors", 0)
    if total_errors == 0:
        reporter.log_info("✔ Seed de credenciais concluído com sucesso!")
        sys.exit(0)
    else:
        reporter.log_error(f"Seed concluído com {total_errors} erros.")
        sys.exit(1)


if __name__ == "__main__":
    main()
