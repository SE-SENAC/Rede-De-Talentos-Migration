#!/usr/bin/env python3
"""
Rede de Talentos Senac Sergipe
Script de Migração do Banco de Dados Legado para o Novo Schema (MS SQL Server 2022)
Arquitetura Limpa / Hexagonal (Ports & Adapters)
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para garantir resolução dos módulos
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.interface.cli.migration_cli import MigrationCLI

if __name__ == "__main__":
    exit_code = MigrationCLI.run()
    sys.exit(exit_code)

