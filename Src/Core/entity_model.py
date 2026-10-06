from Src.Core.abstract_model import abstract_model
from Src.Core.validator import validator


class entity_model(abstract_model):
    """Общий класс для сущностей, содержащий уникальный код и наименование."""

    __name: str = ""
    __max_len_name: int = 50

    @property
    def name(self) -> str:
        """Возвращает краткое наименование сущности."""
        return self.__name

    @name.setter
    def name(self, value: str):
        """Устанавливает краткое наименование сущности.

        :param value: Непустая строка длиной до 50 символов.
        :raises arguments_exception: Если передан неверный тип или пустая строка.
        :raises max_length_exception: Если длина превышает 50 символов.
        """
        validator.validate(value, str, "name", max_len=self.__max_len_name)
        self.__name = value.strip()