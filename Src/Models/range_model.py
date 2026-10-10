from Src.Core.entity_model import entity_model
from Src.Core.exception import arguments_exception

class range_model(entity_model):
    """
    Модель единицы измерения

    Содержит:
        - базовая единица измерения,
        - коэффициент пересчета
    """

    __base: "range_model" = None
    __conversion_factor: float = None

    def __init__(self, name: str = "", conversion_factor:float = 1.0, base: "range_model" = None) -> None:
        """Инициализирует единицу измерения

        :param name: Наименование
        :param conversion_factor: Коэффициент пересчёта к базовой единице
        :param base: Базовая единица измерения
        """
        super().__init__()
        if name != "":
            self.name = name
        self.base = base
        self.conversion_factor = conversion_factor

    @staticmethod
    def create(name: str, conversion_factor: float = 1.0, base: "range_model" = None) -> "range_model":
        """Фабричный метод создания единицы измерения.

        :param name: Наименование единицы измерения.
        :param conversion_factor: Коэффициент пересчёта к базовой единице.
        :param base: Базовая единица измерения или None.
        :return: Заполненный экземпляр range_model.
        """
        unit = range_model()
        unit.name = name
        unit.conversion_factor = conversion_factor
        unit.base = base
        return unit

    @property
    def base(self) -> "range_model":
        """Возвращает базовую единицу измерения"""
        return self.__base

    @base.setter
    def base(self, value: "range_model") -> None:
        """Устанавливает базовую единицу измерения

        :param value: Базовая единица измерения или присвоен None
        :raises arguments_exception: Если значение не range_model и не None
        """
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception("base", "Некорректно переданный аргумент!")
        self.__base = value

    @property
    def conversion_factor(self) -> float:
        """Возвращает коэффициент пересчёта относительно базовой единицы"""
        return self.__conversion_factor

    @conversion_factor.setter
    def conversion_factor(self, value: float) -> None:
        """Устанавливает коэффициент пересчёта

        :param value: Числовое значение коэффициента
        :raises arguments_exception: Если значение не число или меньше/равно нулю
        """
        if value is None or not isinstance(value, (int, float)):
            raise arguments_exception("conversion_factor", "Коэффициент должен быть числом!")
        if value <= 0:
            raise arguments_exception("conversion_factor", "Коэффициент должен быть больше нуля!")
        self.__conversion_factor = float(value)
