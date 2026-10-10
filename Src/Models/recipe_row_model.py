from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class recipe_row_model(abstract_model):
    """Строка технологической карты (рецепта).

    Содержит номенклатуру (ингредиент, полуфабрикат или упаковку),
    единицу измерения, вес брутто и вес нетто.
    """

    __nomenclature: nomenclature_model = None
    __range: range_model = None
    __gross_weight: float = 0.0
    __net_weight: float = 0.0

    def __init__(self) -> None:
        """Инициализирует строку рецепта без параметров."""
        super().__init__()

    @property
    def nomenclature(self) -> nomenclature_model:
        """Возвращает номенклатуру строки рецепта."""
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        """Устанавливает номенклатуру строки рецепта.

        :param value: Экземпляр nomenclature_model.
        :raises arguments_exception: Если передан неверный тип или None.
        """
        validator.validate(value, nomenclature_model, "nomenclature")
        self.__nomenclature = value

    @property
    def range(self) -> range_model:
        """Возвращает единицу измерения строки рецепта."""
        return self.__range

    @range.setter
    def range(self, value: range_model) -> None:
        """Устанавливает единицу измерения строки рецепта.

        :param value: Экземпляр range_model.
        :raises arguments_exception: Если передан неверный тип или None.
        """
        validator.validate(value, range_model, "range")
        self.__range = value

    @property
    def gross_weight(self) -> float:
        """Возвращает вес брутто строки рецепта."""
        return self.__gross_weight

    @gross_weight.setter
    def gross_weight(self, value: float) -> None:
        """Устанавливает вес брутто строки рецепта.

        :param value: Неотрицательное числовое значение.
        :raises arguments_exception: Если значение не число или меньше нуля.
        """
        validator.validate(value, (int, float), "gross_weight")
        if value < 0:
            raise arguments_exception("gross_weight", "Вес брутто не может быть отрицательным!")
        self.__gross_weight = float(value)

    @property
    def net_weight(self) -> float:
        """Возвращает вес нетто строки рецепта."""
        return self.__net_weight

    @net_weight.setter
    def net_weight(self, value: float) -> None:
        """Устанавливает вес нетто строки рецепта.

        :param value: Неотрицательное числовое значение.
        :raises arguments_exception: Если значение не число или меньше нуля.
        """
        validator.validate(value, (int, float), "net_weight")
        if value < 0:
            raise arguments_exception("net_weight", "Вес нетто не может быть отрицательным!")
        self.__net_weight = float(value)

    @staticmethod
    def create(nomenclature: nomenclature_model, range: range_model,
               gross_weight: float, net_weight: float) -> "recipe_row_model":
        """Фабричный метод создания строки рецепта.

        :param nomenclature: Номенклатура ингредиента / полуфабриката / тары.
        :param range: Единица измерения.
        :param gross_weight: Вес брутто.
        :param net_weight: Вес нетто.
        :return: Заполненный экземпляр recipe_row_model.
        """
        row = recipe_row_model()
        row.nomenclature = nomenclature
        row.range = range
        row.gross_weight = gross_weight
        row.net_weight = net_weight
        return row
