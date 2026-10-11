from Src.Core.entity_model import entity_model
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_row_model import recipe_row_model


class recipe_model(entity_model):
    """Модель технологической карты (рецепта).

    Описывает состав блюда или полуфабриката, нормы закладки ингредиентов,
    выходную номенклатуру, а также вычисляет суммарный вес брутто и нетто.
    Поддерживает вложенные рецепты (принцип 'блюдо в блюде') с рекурсивным
    расчетом веса.
    """

    __dish: nomenclature_model = None
    __rows: list = []
    __comments: str = ""

    def __init__(self) -> None:
        """Инициализирует технологическую карту без параметров."""
        super().__init__()
        self.__rows = []

    @property
    def dish(self) -> nomenclature_model:
        """Возвращает выходную номенклатуру (готовое блюдо или полуфабрикат)."""
        return self.__dish

    @dish.setter
    def dish(self, value: nomenclature_model) -> None:
        """Устанавливает выходную номенклатуру рецепта.

        :param value: Экземпляр nomenclature_model.
        :raises arguments_exception: Если передан неверный тип или None.
        """
        validator.validate(value, nomenclature_model, "dish")
        self.__dish = value

    @property
    def comments(self) -> str:
        """Возвращает описание технологии приготовления."""
        return self.__comments

    @comments.setter
    def comments(self, value: str) -> None:
        """Устанавливает описание технологии приготовления.

        :param value: Текстовое описание.
        :raises arguments_exception: Если передан неверный тип или пустая строка.
        """
        validator.validate(value, str, "comments")
        self.__comments = value.strip()

    @property
    def rows(self) -> list:
        """Возвращает список строк состава рецепта."""
        return list(self.__rows)

    def add_row(self, row: recipe_row_model) -> bool:
        """Добавляет строку ингредиента или вложенного рецепта в технологическую карту.

        Исключает добавление дублирующихся строк по одной номенклатуре или вложенному рецепту,
        а также защищает от циклической зависимости (добавления рецепта в самого себя).

        :param row: Экземпляр recipe_row_model.
        :return: True, если строка успешно добавлена, иначе False.
        """
        validator.validate(row, recipe_row_model, "row")
        if row.sub_recipe is not None and row.sub_recipe == self:
            return False

        for r in self.__rows:
            if r.sub_recipe is not None and row.sub_recipe is not None:
                if r.sub_recipe == row.sub_recipe:
                    return False
            elif r.nomenclature is not None and row.nomenclature is not None:
                if r.nomenclature == row.nomenclature:
                    return False

        self.__rows.append(row)
        return True

    def remove_row(self, row: recipe_row_model) -> bool:
        """Исключает строку ингредиента из технологической карты.

        :param row: Экземпляр recipe_row_model для удаления.
        :return: True, если строка найдена и удалена, иначе False.
        """
        if row in self.__rows:
            self.__rows.remove(row)
            return True
        for r in list(self.__rows):
            if r.unique_code == getattr(row, "unique_code", None):
                self.__rows.remove(r)
                return True
            if row.sub_recipe is not None and r.sub_recipe == row.sub_recipe:
                self.__rows.remove(r)
                return True
            if row.nomenclature is not None and r.nomenclature == row.nomenclature:
                self.__rows.remove(r)
                return True
        return False

    @property
    def gross_weight(self) -> float:
        """Вычисляет суммарный вес брутто всех ингредиентов с рекурсивным обходом вложенных рецептов.

        Принцип 'блюдо в блюде': если строка содержит вложенную технологическую карту (sub_recipe),
        ее вес брутто вычисляется рекурсивно через обращение к sub_recipe.gross_weight.
        """
        total = 0.0
        for r in self.__rows:
            if r.sub_recipe is not None and r.gross_weight == 0.0:
                total += r.sub_recipe.gross_weight
            else:
                total += r.gross_weight
        return round(total, 3)

    @property
    def net_weight(self) -> float:
        """Вычисляет суммарный вес нетто всех ингредиентов с рекурсивным обходом вложенных рецептов.

        Принцип 'блюдо в блюде': если строка содержит вложенную технологическую карту (sub_recipe),
        ее вес нетто вычисляется рекурсивно через обращение к sub_recipe.net_weight.
        """
        total = 0.0
        for r in self.__rows:
            if r.sub_recipe is not None and r.net_weight == 0.0:
                total += r.sub_recipe.net_weight
            else:
                total += r.net_weight
        return round(total, 3)

    @staticmethod
    def create(name: str, dish: nomenclature_model, rows: list = None,
               comments: str = "") -> "recipe_model":
        """Фабричный метод создания технологической карты.

        :param name: Наименование технологической карты (до 50 символов).
        :param dish: Выходное блюдо или полуфабрикат.
        :param rows: Список строк рецепта (recipe_row_model).
        :param comments: Описание технологии приготовления.
        :return: Заполненный экземпляр recipe_model.
        """
        recipe = recipe_model()
        recipe.name = name
        recipe.dish = dish
        if comments != "":
            recipe.comments = comments
        if rows:
            for r in rows:
                recipe.add_row(r)
        return recipe
