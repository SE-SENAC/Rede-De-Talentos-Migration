from abc import ABC, abstractmethod
from typing import Generator, Any, Dict


class SourceDatabasePort(ABC):
    """
    Porta de saída para extração de dados do banco de dados legado (RedeDeTalentos).
    """

    @abstractmethod
    def test_connection(self) -> bool:
        """Valida se a conexão com o banco legado está ativa."""
        pass

    @abstractmethod
    def get_row_counts(self) -> Dict[str, int]:
        """Retorna contagem de linhas de todas as tabelas legadas."""
        pass

    @abstractmethod
    def get_usuarios(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_admins(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_empresas(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_recruiters(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_students(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_vagas(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_experiencias(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_idiomas(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_qualificacoes(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_inscricoes(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_notifications(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_logs_admin(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_logs_job(self) -> Generator[Dict[str, Any], None, None]:
        pass

    @abstractmethod
    def get_logs_user(self) -> Generator[Dict[str, Any], None, None]:
        pass

