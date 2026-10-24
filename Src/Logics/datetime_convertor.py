from datetime import date, datetime, time
from typing import Any

from Src.Core.abstract_covertor import abstract_covertor


class datetime_convertor(abstract_covertor):
    """Конвертер значений типа DateTime в словарь с ISO 8601-представлением."""

    @staticmethod
    def is_datetime(source: Any) -> bool:
        """Проверить, относится ли значение к дате или времени.

        :param source: Проверяемое значение.
        :return: True для datetime, date и time.
        """
        return isinstance(source, (datetime, date, time))

    @staticmethod
    def to_value(source: Any) -> str:
        """Привести дату/время к строке ISO 8601.

        :param source: Значение datetime, date или time.
        :return: Строковое представление значения.
        """
        return source.isoformat()

    def Convert(self, source: Any) -> dict:
        """Преобразовать дату/время или объект в словарь datetime-полей.

        Для скалярного значения возвращается словарь {"value": ISO-строка}.
        Для объекта возвращается словарь только тех его полей, которые имеют
        тип datetime, date или time.

        :param source: Значение даты/времени или объект с публичными свойствами.
        :return: Словарь в формате {наименование_поля: данные_поля}.
        :raises arguments_exception: Если source равен None.
        """
        self._validate_source(source)

        if self.is_datetime(source):
            return {"value": self.to_value(source)}

        result = {}
        for field_name in self._get_fields(source):
            try:
                value = getattr(source, field_name)
            except Exception:
                continue

            if self.is_datetime(value):
                result[field_name] = self.to_value(value)

        return result
