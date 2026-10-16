from abc import ABC, abstractmethod
from Src.Dtos.report_type_enum import report_type_enum


class abstract_report_factory(ABC):
    """Абстрактная фабрика отчетов."""

    @abstractmethod
    def create(self, report_type: report_type_enum):
        """Подобрать и создать инстанс нужного отчета."""
        pass

    @abstractmethod
    def create_default(self):
        """Создать инстанс отчета по умолчанию на основе настроек."""
        pass
