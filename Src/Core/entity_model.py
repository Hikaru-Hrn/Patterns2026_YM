from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception, max_length_exception


class entity_model(abstract_model):
    """Общий класс для наследования доменных моделей.

    Содержит стандартные определения: уникальный код (в базовом классе)
    и наименование.
    """
    __name: str = ""
    __max_length: int = 50

    @property
    def name(self) -> str:
        """Возвращает наименование сущности."""
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        """Устанавливает наименование сущности.

        :param value: Наименование (строка, не пустая, без лишних пробелов по краям).
        :raises arguments_exception: Если значение не строка, None или пустое.
        :raises max_length_exception: Если длина превышает максимально допустимую.
        """
        if value is None or not isinstance(value, str) or value.strip() == "":
            raise arguments_exception("name", "Некорректно переданный аргумент")
        if len(value.strip()) > self.__max_length:
            raise max_length_exception("name", self.__max_length)
        self.__name = value.strip()

    @property
    def max_length(self) -> int:
        """Возвращает максимально допустимую длину наименования."""
        return self.__max_length