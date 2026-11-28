from datetime import datetime

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator


class log_entry_model(abstract_model):
    """Модель записи лога."""

    __period: datetime = None
    __subsystem: str = ""
    __level: str = ""
    __message: str = ""

    def __init__(self) -> None:
        """Инициализирует пустую запись лога."""
        super().__init__()

    @staticmethod
    def create(period: datetime, subsystem: str, level: str, message: str) -> "log_entry_model":
        """Фабричный метод создания записи лога.

        :param period: Дата и время события.
        :param subsystem: Название подсистемы.
        :param level: Уровень сообщения (ERROR, INFO, DEBUG).
        :param message: Текст сообщения.
        :return: Заполненный экземпляр log_entry_model.
        """
        entry = log_entry_model()
        entry.period = period
        entry.subsystem = subsystem
        entry.level = level
        entry.message = message
        return entry

    @property
    def period(self) -> datetime:
        """Возвращает дату и время события."""
        return self.__period

    @period.setter
    def period(self, value: datetime) -> None:
        """Устанавливает дату и время события.

        :param value: Экземпляр datetime.
        :raises arguments_exception: Если передан неверный тип.
        """
        validator.validate(value, datetime, "period")
        self.__period = value

    @property
    def subsystem(self) -> str:
        """Возвращает название подсистемы."""
        return self.__subsystem

    @subsystem.setter
    def subsystem(self, value: str) -> None:
        """Устанавливает название подсистемы.

        :param value: Непустая строка.
        :raises arguments_exception: Если значение не строка или пустое.
        """
        if value is None or not isinstance(value, str) or value.strip() == "":
            raise arguments_exception("subsystem", "Подсистема не может быть пустой")
        self.__subsystem = value.strip()

    @property
    def level(self) -> str:
        """Возвращает уровень сообщения."""
        return self.__level

    @level.setter
    def level(self, value: str) -> None:
        """Устанавливает уровень сообщения.

        :param value: Одно из значений: ERROR, INFO, DEBUG.
        :raises arguments_exception: Если передано неверное значение.
        """
        if value is None or not isinstance(value, str) or value.strip() == "":
            raise arguments_exception("level", "Уровень не может быть пустым")
        clean = value.strip().upper()
        if clean not in ("ERROR", "INFO", "DEBUG"):
            raise arguments_exception("level", "Уровень должен быть ERROR, INFO или DEBUG")
        self.__level = clean

    @property
    def message(self) -> str:
        """Возвращает текст сообщения."""
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        """Устанавливает текст сообщения.

        :param value: Строка сообщения.
        :raises arguments_exception: Если значение не строка.
        """
        if value is None:
            raise arguments_exception("message", "Сообщение не может быть None")
        self.__message = str(value).strip()
