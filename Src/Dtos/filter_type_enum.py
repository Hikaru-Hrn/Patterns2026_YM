from enum import Enum
from Src.Core.exception import arguments_exception


class filter_type_enum(Enum):
    """Перечисление вариантов фильтрации данных.

    EQUALS - полное совпадение значения.
    LIKE   - вхождение подстроки без учета регистра.
    """

    EQUALS = 1
    LIKE = 2

    @staticmethod
    def from_string(value: str) -> "filter_type_enum":
        """Преобразует строковое наименование типа фильтра в значение перечисления.

        :param value: Строковое имя фильтра (EQUALS, LIKE).
        :return: Значение filter_type_enum.
        :raises arguments_exception: Если передан неподдерживаемый тип фильтра.
        """
        if not isinstance(value, str) or value.strip() == "":
            raise arguments_exception("filter_type", "Тип фильтра не может быть пустым")

        clean_value = value.strip().upper()
        mapping = {
            "EQUALS": filter_type_enum.EQUALS,
            "EQ": filter_type_enum.EQUALS,
            "=": filter_type_enum.EQUALS,
            "LIKE": filter_type_enum.LIKE,
            "~": filter_type_enum.LIKE,
        }

        if clean_value not in mapping:
            raise arguments_exception(
                "filter_type",
                f"Неподдерживаемый тип фильтра: {value}. Доступные: EQUALS, LIKE",
            )

        return mapping[clean_value]
