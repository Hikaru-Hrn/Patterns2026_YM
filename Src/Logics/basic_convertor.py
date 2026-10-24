from enum import Enum
from typing import Any

from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.exception import arguments_exception


class basic_convertor(abstract_covertor):
    """Конвертер простых типов (numeric, str, bool, None, Enum) в словарь."""

    @staticmethod
    def is_basic(source: Any) -> bool:
        """Проверить, относится ли значение к простым типам.

        :param source: Проверяемое значение.
        :return: True, если значение является простым типом.
        """
        return source is None or isinstance(source, (str, int, float, bool, Enum))

    @staticmethod
    def to_value(source: Any) -> Any:
        """Привести простое значение к JSON-совместимому виду.

        :param source: Простое значение.
        :return: Исходное значение, а для Enum — его строковое имя.
        """
        if isinstance(source, Enum):
            return source.name
        return source

    def Convert(self, source: Any) -> dict:
        """Преобразовать простое значение или объект в словарь простых полей.

        Для скалярного значения возвращается словарь {"value": значение}.
        Для объекта возвращается словарь только тех его полей, которые имеют
        простой тип.

        :param source: Скалярное значение или объект с публичными свойствами.
        :return: Словарь в формате {наименование_поля: данные_поля}.
        :raises arguments_exception: Если source равен None.
        """
        self._validate_source(source)

        if self.is_basic(source):
            return {"value": self.to_value(source)}

        result = {}
        for field_name in self._get_fields(source):
            try:
                value = getattr(source, field_name)
            except Exception:
                continue

            if self.is_basic(value):
                result[field_name] = self.to_value(value)

        return result
