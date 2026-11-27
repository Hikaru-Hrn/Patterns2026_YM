from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator
from Src.Models.log_entry_model import log_entry_model


class log_report_model(abstract_model):
    """Модель отчета по записям лога."""

    __entries: list[log_entry_model] = []

    def __init__(self) -> None:
        """Инициализирует пустой отчет по логу."""
        super().__init__()
        self.__entries = []

    @staticmethod
    def create(entries: list[log_entry_model]) -> "log_report_model":
        """Фабричный метод создания отчета по логу.

        :param entries: Список записей лога.
        :return: Заполненный экземпляр log_report_model.
        """
        report = log_report_model()
        report.entries = entries
        return report

    @property
    def entries(self) -> list[log_entry_model]:
        """Возвращает список записей лога."""
        return list(self.__entries)

    @entries.setter
    def entries(self, value: list[log_entry_model]) -> None:
        """Устанавливает список записей лога.

        :param value: Список log_entry_model.
        """
        validator.validate(value, list)
        for item in value:
            validator.validate(item, log_entry_model)
        self.__entries = list(value)
