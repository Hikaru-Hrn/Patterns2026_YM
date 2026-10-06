from Src.Core.entity_model import entity_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception, max_length_exception

class nomenclature_model(entity_model):
    """Модель номенклатурной позиции (товара, ингредиента или блюда).

    Содержит краткое наименование (до 50 символов), полное наименование (до 255 символов),
    ссылку на группу номенклатуры и единицу измерения.
    """

    __full_name: str = ""
    __full_name_max_length: int = 255
    __group: group_model = None
    __range: range_model = None

    def __init__(self) -> None:
        """Инициализирует экземпляр номенклатуры без параметров.

        Все свойства (name, full_name, group, range) устанавливаются через
        соответствующие сеттеры.
        """
        super().__init__()

    @property
    def full_name(self) -> str:
        """Возвращает полное наименование номенклатуры"""
        return self.__full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        """Устанавливает полное наименование номенклатуры

        :param value: Полное наименование
        :raises arguments_exception: Если значение не строка или присвоен None
        :raises max_length_exception: Если длина превышает максимальную длину
        """
        if value is None or not isinstance(value, str):
            raise arguments_exception("full_name", "Некорректно переданный аргумент!")
        if len(value.strip()) > self.__full_name_max_length:
            raise max_length_exception("full_name", self.__full_name_max_length)
        self.__full_name = value

    @property
    def group(self) -> group_model:
        """Возвращает группу номенклатуры"""
        return self.__group

    @group.setter
    def group(self, value: group_model) -> None:
        """Устанавливает группу номенклатуры

        :param value: Группа номенклатуры или None
        :raises arguments_exception: Если значение не group_model и не None
        """
        if value is not None and not isinstance(value, group_model):
            raise arguments_exception("group", "Некорректно переданный аргумент!")
        self.__group = value

    @property
    def range(self) -> range_model:
        """Возвращает единицу измерения номенклатуры"""
        return self.__range

    @range.setter
    def range(self, value: range_model) -> None:
        """Устанавливает единицу измерения номенклатуры

        :param value: Единица измерения или None
        :raises arguments_exception: Если значение не range_model и не None
        """
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception("range", "Некорректно переданный аргумент!")
        self.__range = value