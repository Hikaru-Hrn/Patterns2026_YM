from Src.Core.validator import validator


class entity_description_header_dto:
    """DTO для описания одного заголовочного поля доменной сущности."""

    __field: str = ""
    __value: str = ""

    @property
    def field(self) -> str:
        """Возвращает наименование поля."""
        return self.__field

    @field.setter
    def field(self, value: str) -> None:
        """Устанавливает наименование поля.

        :param value: Имя поля.
        """
        validator.validate(value, str, "field")
        self.__field = value.strip()

    @property
    def value(self) -> str:
        """Возвращает строковое значение поля."""
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        """Устанавливает строковое значение поля.

        :param value: Строковое представление значения.
        """
        self.__value = str(value).strip() if value is not None else ""
