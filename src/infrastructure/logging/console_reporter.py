import sys
from datetime import datetime
from typing import Dict, Any
from src.domain.ports.outbound.migration_reporter_port import MigrationReporterPort


class ConsoleMigrationReporter(MigrationReporterPort):
    """
    Implementação de console para emissão de logs e relatórios da migração.
    """

    def __init__(self):
        # Garantir suporte UTF-8 no Windows terminal
        try:
            if sys.stdout and hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def log_info(self, message: str) -> None:
        print(f"[{self._timestamp()}] [INFO] {message}")

    def log_warning(self, message: str) -> None:
        print(f"[{self._timestamp()}] [AVISO] ⚠️  {message}")

    def log_error(self, message: str, error: Exception | None = None) -> None:
        err_detail = f" | Detalhe: {error}" if error else ""
        print(f"[{self._timestamp()}] [ERRO] ❌ {message}{err_detail}")

    def log_step_start(self, step_name: str) -> None:
        print(f"\n[{self._timestamp()}] --------------------------------------------------")
        print(f"[{self._timestamp()}] ▶ Iniciando Fase: {step_name}")

    def log_step_completed(self, step_name: str, extracted: int, migrated: int, skipped: int) -> None:
        print(
            f"[{self._timestamp()}] ✔ Fase Concluída: {step_name} | "
            f"Extraídos: {extracted} | Migrados: {migrated} | Ignorados: {skipped}"
        )

    def log_summary(self, summary_data: Dict[str, Any]) -> None:
        print("\n" + "=" * 80)
        print("  SENAC SERGIPE • RELATÓRIO CONSOLIDADO DE MIGRAÇÃO")
        print("=" * 80)
        mode = "DRY-RUN (Simulação - Sem gravação)" if summary_data.get("dry_run") else "PRODUÇÃO (Persistido no Banco)"
        print(f"Modo de Operação    : {mode}")
        print(f"Duração Total       : {summary_data.get('duration_seconds')} segundos")
        print(f"Total Extraído      : {summary_data.get('total_extracted')}")
        print(f"Total Migrado       : {summary_data.get('total_migrated')}")
        print(f"Total Ignorado      : {summary_data.get('total_skipped')}")
        print(f"Total de Erros      : {summary_data.get('total_errors')}")
        print("-" * 80)
        print(f"{'Etapa':<20} | {'Extraídos':<10} | {'Migrados':<10} | {'Ignorados':<10} | {'Duração (s)':<12}")
        print("-" * 80)

        steps = summary_data.get("steps", {})
        for name, data in steps.items():
            ext = data.get("extracted", 0)
            mig = data.get("migrated", 0)
            skp = data.get("skipped", 0)
            dur = round(data.get("duration_seconds", 0.0), 2)
            print(f"{name:<20} | {ext:<10} | {mig:<10} | {skp:<10} | {dur:<12}")

        print("=" * 80 + "\n")

