from Src.Core.entity_model import entity_model
from Src.Core.exception import arguments_exeption

class range_model(entity_model):
    """
    Модель единицы измерения

    Содержит:
        - базовая единица измерения,
        - коэффициент пересчета
    """

    __base: "range_model" = None
    __convertion_factor: float = None

    def __init__(self, name: str = "", convertion_factor:float = 1.0, base: "range_model" = None) -> None:
        """Инициализирует единицу измерения

        :param name: Наименование
        :param convertion_factor: Коэффициент пересчёта к базовой единице
        :param base: Базовая единица измерения
        """
        super().__init__()
        self.name = name
        self.base = base
        self.convertion_factor = convertion_factor

    @property
    def base(self) -> "range_model":
        """Возвращает базовую единицу измерения"""
        return self.__base

    @base.setter
    def base(self, value: "range_model") -> None:
        """Устанавливает базовую единицу измерения

        :param value: Базовая единица измерения или присвоен None
        :raises arguments_exeption: Если значение не range_model и не None
        """
        if value is not None and not isinstance(value, range_model):
            raise arguments_exeption("base", "Некорректно переданный аргумент!")
        self.__base = value

    @property
    def conversion_factor(self) -> float:
        """Возвращает коэффициент пересчёта относительно базовой единицы"""
        return self.__convertion_factor

    @conversion_factor.setter
    def conversion_factor(self, value: float) -> None:
        """Устанавливает коэффициент пересчёта

        :param value: Числовое значение коэффициента
        :raises arguments_exeption: Если значение не число или меньше/равно нулю
        """
        if value is None or not isinstance(value, (int, float)):
            raise arguments_exeption("conversion_factor", "Коэффициент должен быть числом!")
        if value <= 0:
            raise arguments_exeption("conversion_factor", "Коэффициент должен быть больше нуля!")
        self.__convertion_factor = float(value)
