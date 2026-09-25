from abc import ABC, abstractmethod
from typing import List, Dict
from src.domain.entities.user import UserEntity
from src.domain.entities.address import AddressEntity
from src.domain.entities.contact import ContactEntity
from src.domain.entities.phone import PhoneEntity
from src.domain.entities.company import CompanyEntity
from src.domain.entities.student import StudentEntity
from src.domain.entities.job import JobEntity
from src.domain.entities.curriculum import ExperienceEntity, LanguageEntity, QualificationEntity
from src.domain.entities.application import ApplicationEntity
from src.domain.entities.notification import NotificationEntity
from src.domain.entities.log import LogEntity


class TargetDatabasePort(ABC):
    """
    Porta de saída para persistência de dados no novo schema (RedeDeTalentos_DEV).
    """

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    @abstractmethod
    def get_row_counts(self) -> Dict[str, int]:
        pass

    @abstractmethod
    def save_users(self, users: List[UserEntity]) -> int:
        pass

    @abstractmethod
    def save_addresses(self, addresses: List[AddressEntity]) -> int:
        pass

    @abstractmethod
    def save_contacts(self, contacts: List[ContactEntity]) -> int:
        pass

    @abstractmethod
    def save_phones(self, phones: List[PhoneEntity]) -> int:
        pass

    @abstractmethod
    def save_companies(self, companies: List[CompanyEntity]) -> int:
        pass

    @abstractmethod
    def save_students(self, students: List[StudentEntity]) -> int:
        pass

    @abstractmethod
    def save_jobs(self, jobs: List[JobEntity]) -> int:
        pass

    @abstractmethod
    def save_experiences(self, experiences: List[ExperienceEntity]) -> int:
        pass

    @abstractmethod
    def save_languages(self, languages: List[LanguageEntity]) -> int:
        pass

    @abstractmethod
    def save_qualifications(self, qualifications: List[QualificationEntity]) -> int:
        pass

    @abstractmethod
    def save_applications(self, applications: List[ApplicationEntity]) -> int:
        pass

    @abstractmethod
    def save_notifications(self, notifications: List[NotificationEntity]) -> int:
        pass

    @abstractmethod
    def save_logs(self, logs: List[LogEntity]) -> int:
        pass

    @abstractmethod
    def clean_target_tables(self) -> None:
        pass


