from Src.Core.abstract_report import abstractmethod
from Src.Dtos.report_type_enum import report_type_enum
from abc import ABC


"""
Абстрактная фабрика отчетов.
"""
class abstract_report_factory(ABC):

    """
    Подобрать и создать инстанс нужного отчета
    """
    @abstractmethod
    def create(self, report_type: report_type_enum):
        pass