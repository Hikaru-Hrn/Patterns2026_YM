from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class recipe_row_model(abstract_model):
    """Строка технологической карты (рецепта).

    Содержит номенклатуру (ингредиент, тару) либо ссылку на вложенную
    технологическую карту (полуфабрикат, принцип 'блюдо в блюде'),
    единицу измерения, вес брутто и вес нетто.
    """

    __nomenclature: nomenclature_model = None
    __sub_recipe = None
    __range: range_model = None
    __gross_weight: float = 0.0
    __net_weight: float = 0.0

    def __init__(self) -> None:
        """Инициализирует строку рецепта без параметров."""
        super().__init__()

    @property
    def nomenclature(self) -> nomenclature_model:
        """Возвращает номенклатуру строки рецепта."""
        if self.__nomenclature is None and self.__sub_recipe is not None:
            return self.__sub_recipe.dish
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
    def sub_recipe(self):
        """Возвращает вложенный рецепт (полуфабрикат), если строка является составной."""
        return self.__sub_recipe

    @sub_recipe.setter
    def sub_recipe(self, value) -> None:
        """Устанавливает вложенный рецепт (полуфабрикат) для реализации принципа 'блюдо в блюде'.

        :param value: Экземпляр recipe_model или None.
        """
        if value is not None:
            from Src.Models.recipe_model import recipe_model
            validator.validate(value, recipe_model, "sub_recipe")
            if self.__nomenclature is None and value.dish is not None:
                self.__nomenclature = value.dish
        self.__sub_recipe = value

    @property
    def recipe(self):
        """Синоним свойства sub_recipe."""
        return self.__sub_recipe

    @recipe.setter
    def recipe(self, value) -> None:
        """Синоним сеттера sub_recipe."""
        self.sub_recipe = value

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
        if self.__sub_recipe is not None and self.__gross_weight == 0.0:
            return self.__sub_recipe.gross_weight
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
        if self.__sub_recipe is not None and self.__net_weight == 0.0:
            return self.__sub_recipe.net_weight
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
    def create(item, range: range_model = None,
               gross_weight: float = 0.0, net_weight: float = 0.0) -> "recipe_row_model":
        """Фабричный метод создания строки рецепта.

        Поддерживает как простую номенклатуру (ингредиент, тара),
        так и вложенную технологическую карту (полуфабрикат 'блюдо в блюде').

        :param item: Экземпляр nomenclature_model или recipe_model.
        :param range: Единица измерения (опционально, если item - recipe_model, берется из блюда).
        :param gross_weight: Вес брутто (если 0 и передан recipe_model, рассчитывается рекурсивно).
        :param net_weight: Вес нетто (если 0 и передан recipe_model, рассчитывается рекурсивно).
        :return: Заполненный экземпляр recipe_row_model.
        """
        from Src.Models.recipe_model import recipe_model

        row = recipe_row_model()
        if isinstance(item, recipe_model):
            row.sub_recipe = item
            if range is not None:
                row.range = range
            elif item.dish is not None and item.dish.range is not None:
                row.range = item.dish.range
            row.gross_weight = gross_weight
            row.net_weight = net_weight
        else:
            row.nomenclature = item
            row.range = range
            row.gross_weight = gross_weight
            row.net_weight = net_weight
        return row
