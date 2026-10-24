from abc import ABC, abstractmethod
from typing import Any

from Src.Core.exception import arguments_exception


class abstract_covertor(ABC):
    """Абстрактный конвертер объектов в словарь.

    Контракт класса: метод Convert принимает любой объект и возвращает
    словарь, где ключ — наименование поля, а значение — данные этого поля.
    """

    @abstractmethod
    def Convert(self, source: Any) -> dict:
        """Преобразовать объект в словарь полей.

        :param source: Любой объект: модель, скалярное значение или объект
            с публичными свойствами.
        :return: Словарь в формате {наименование_поля: данные_поля}.
        :raises arguments_exception: Если source равен None.
        """
        pass

    def convert(self, source: Any) -> dict:
        """snake_case-алиас метода Convert для совместимости со стилем проекта.

        :param source: Объект для преобразования.
        :return: Словарь в формате {наименование_поля: данные_поля}.
        :raises arguments_exception: Если source равен None.
        """
        return self.Convert(source)

    @staticmethod
    def _validate_source(source: Any) -> None:
        """Проверить, что для конвертации передан не None.

        :param source: Проверяемый объект.
        :raises arguments_exception: Если source равен None.
        """
        if source is None:
            raise arguments_exception("source", "Некорректно переданный аргумент!")

    @staticmethod
    def _get_fields(source: Any) -> list:
        """Получить публичные @property объекта в порядке их объявления.

        Обход выполняется по MRO от базового класса к наследнику. Такой порядок
        сохраняет естественную структуру модели: например, у receipt_model
        свойство rows идёт раньше алиаса items, а у recipe_row_model
        sub_recipe — раньше алиаса recipe.

        :param source: Объект, свойства которого нужно перечислить.
        :return: Список имён публичных свойств.
        :raises arguments_exception: Если source равен None.
        """
        abstract_covertor._validate_source(source)

        field_names = []
        for cls in reversed(type(source).__mro__):
            for name, attribute in cls.__dict__.items():
                if name.startswith("_"):
                    continue
                if isinstance(attribute, property) and name not in field_names:
                    field_names.append(name)

        return field_names
