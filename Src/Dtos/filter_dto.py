from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Dtos.filter_type_enum import filter_type_enum


class filter_item_dto:
    """Одно условие фильтрации данных.

    Содержит имя поля, тип сравнения и значение для поиска.
    """

    __field_name: str = ""
    __filter_type: filter_type_enum = filter_type_enum.EQUALS
    __value: str = ""

    def __init__(self) -> None:
        """Инициализирует пустое условие фильтрации."""
        self.__field_name = ""
        self.__filter_type = filter_type_enum.EQUALS
        self.__value = ""

    @property
    def field_name(self) -> str:
        """Возвращает имя поля, по которому выполняется фильтрация."""
        return self.__field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        """Устанавливает имя поля для фильтрации.

        :param value: Непустая строка с именем поля.
        :raises arguments_exception: Если значение не строка или пустое.
        """
        if value is None or not isinstance(value, str) or value.strip() == "":
            raise arguments_exception("field_name", "Имя поля фильтра не может быть пустым")
        self.__field_name = value.strip()

    @property
    def filter_type(self) -> filter_type_enum:
        """Возвращает тип сравнения условия фильтрации."""
        return self.__filter_type

    @filter_type.setter
    def filter_type(self, value: filter_type_enum) -> None:
        """Устанавливает тип сравнения условия фильтрации.

        :param value: Значение filter_type_enum.
        :raises arguments_exception: Если передан неверный тип.
        """
        if isinstance(value, str):
            value = filter_type_enum.from_string(value)
        if not isinstance(value, filter_type_enum):
            raise arguments_exception("filter_type", "Некорректный тип фильтрации")
        self.__filter_type = value

    @property
    def value(self) -> str:
        """Возвращает значение для фильтрации."""
        return self.__value

    @value.setter
    def value(self, value: str) -> None:
        """Устанавливает значение для фильтрации.

        :param value: Строковое значение условия.
        :raises arguments_exception: Если значение не строка.
        """
        if value is None:
            raise arguments_exception("value", "Значение фильтра не может быть None")
        self.__value = str(value).strip()

    @staticmethod
    def create(field_name: str, value: str, filter_type: filter_type_enum = filter_type_enum.EQUALS) -> "filter_item_dto":
        """Фабричный метод создания условия фильтрации.

        :param field_name: Имя поля.
        :param value: Значение для поиска.
        :param filter_type: Тип сравнения.
        :return: Заполненный экземпляр filter_item_dto.
        """
        item = filter_item_dto()
        item.field_name = field_name
        item.value = value
        item.filter_type = filter_type
        return item

    @staticmethod
    def from_dict(source: dict) -> "filter_item_dto":
        """Создает условие фильтрации из JSON-словаря.

        :param source: Словарь с ключами field_name, value, filter_type.
        :return: Заполненный экземпляр filter_item_dto.
        :raises arguments_exception: Если передан не словарь.
        """
        if not isinstance(source, dict):
            raise arguments_exception("source", "Ожидался словарь для создания filter_item_dto")

        item = filter_item_dto()
        item.field_name = source.get("field_name", "")
        item.value = source.get("value", "")
        item.filter_type = source.get("filter_type", filter_type_enum.EQUALS)
        return item


class filter_dto:
    """Модель данных для передачи условий фильтрации.

    Содержит набор условий filter_item_dto, которые применяются совместно.
    """

    __filters: list = []

    def __init__(self) -> None:
        """Инициализирует пустой набор условий фильтрации."""
        self.__filters = []

    @property
    def filters(self) -> list[filter_item_dto]:
        """Возвращает список условий фильтрации."""
        return list(self.__filters)

    @filters.setter
    def filters(self, value: list[filter_item_dto]) -> None:
        """Устанавливает список условий фильтрации.

        :param value: Список filter_item_dto.
        :raises arguments_exception: Если передан не список или элемент не filter_item_dto.
        """
        validator.validate(value, list)
        for item in value:
            validator.validate(item, filter_item_dto)
        self.__filters = list(value)

    def add_filter(self, item: filter_item_dto) -> None:
        """Добавляет условие фильтрации в набор.

        :param item: Экземпляр filter_item_dto.
        """
        validator.validate(item, filter_item_dto)
        self.__filters.append(item)

    @staticmethod
    def create(*filters: filter_item_dto) -> "filter_dto":
        """Фабричный метод создания DTO фильтрации.

        :param filters: Условия фильтрации.
        :return: Заполненный экземпляр filter_dto.
        """
        dto = filter_dto()
        for item in filters:
            dto.add_filter(item)
        return dto

    @staticmethod
    def from_dict(source: dict) -> "filter_dto":
        """Создает DTO фильтрации из JSON-словаря.

        :param source: Словарь с ключом filters, содержащим список условий.
        :return: Заполненный экземпляр filter_dto.
        :raises arguments_exception: Если передан не словарь или неверная структура.
        """
        if not isinstance(source, dict):
            raise arguments_exception("source", "Ожидался словарь для создания filter_dto")

        dto = filter_dto()
        filters_data = source.get("filters", [])
        if not isinstance(filters_data, list):
            raise arguments_exception("filters", "Поле filters должно быть списком")

        dto.filters = [filter_item_dto.from_dict(item) for item in filters_data]
        return dto
