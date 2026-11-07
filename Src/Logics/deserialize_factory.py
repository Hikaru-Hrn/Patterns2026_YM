from typing import Any

from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import recipe_row_model
from Src.Models.warehouse_model import warehouse_model


class deserialize_factory(abstract_deserialize_factory):
    """Фабрика рекурсивного восстановления доменных моделей из JSON.

    Тип модели определяется по набору полей JSON. Восстановленные объекты
    кэшируются по ``unique_code``, поэтому общие и циклические ссылки снова
    указывают на один экземпляр, а не на копии.
    """

    _collections = ("warehouses", "ranges", "groups", "nomenclatures", "recipes")

    def create(self, source: dict) -> abstract_model:
        """Создать пустую модель по структуре JSON-словаря.

        :param source: Словарь с полями одной модели.
        :return: Экземпляр receipt_model, recipe_row_model, nomenclature_model,
            warehouse_model, range_model или group_model.
        :raises arguments_exception: Если тип модели определить нельзя.
        """
        if not isinstance(source, dict):
            raise arguments_exception("source", "Ожидался словарь JSON!")

        if "rows" in source or "dish" in source:
            return receipt_model()

        if "nomenclature" in source or "sub_recipe" in source:
            return recipe_row_model()

        if "full_name" in source:
            return nomenclature_model()

        if "address" in source:
            return warehouse_model()

        if "conversion_factor" in source or "base" in source:
            return range_model()

        if "name" in source:
            return group_model()

        raise arguments_exception("source", "Не удалось определить тип модели по данным JSON!")

    def Convert(self, source: Any) -> Any:
        """Рекурсивно восстановить модели из JSON-структуры.

        :param source: Словарь хранилища, словарь модели или список.
        :return: Словарь коллекций, модель, список или скаляр.
        :raises arguments_exception: Если source равен None.
        """
        if source is None:
            raise arguments_exception("source", "Некорректно переданный аргумент!")

        return self.__convert(source, {})

    def __convert(self, source: Any, cache: dict) -> Any:
        """Рекурсивно преобразовать JSON-узел в модели.

        :param source: Текущий узел JSON.
        :param cache: Восстановленные модели по unique_code.
        :return: Модель, список, словарь коллекций или скаляр.
        """
        if isinstance(source, dict):
            if self.__is_collection(source):
                return {
                    key: self.__convert(value, cache)
                    for key, value in source.items()
                    if key in self._collections
                }
            return self.__convert_model(source, cache)

        if isinstance(source, (list, tuple)):
            return [self.__convert(item, cache) for item in source]

        return source

    @classmethod
    def __is_collection(cls, source: dict) -> bool:
        """Проверить, является ли словарь корневым набором коллекций.

        :param source: Проверяемый словарь.
        :return: True, если есть ключи коллекций storage_manager.
        """
        return "unique_code" not in source and any(key in source for key in cls._collections)

    def __convert_model(self, source: dict, cache: dict) -> abstract_model:
        """Создать модель и заполнить её поля с учётом кэша ссылок.

        :param source: Словарь с полями модели.
        :param cache: Восстановленные модели по unique_code.
        :return: Заполненный экземпляр модели.
        """
        unique_code = source.get("unique_code")
        if isinstance(unique_code, str) and unique_code in cache:
            return cache[unique_code]

        model = self.create(source)
        if isinstance(unique_code, str) and unique_code.strip() != "":
            model.unique_code = unique_code
            cache[unique_code] = model

        self.__fill(model, source, cache)
        return model

    def __fill(self, model: abstract_model, source: dict, cache: dict) -> None:
        """Заполнить свойства модели значениями из JSON.

        Поля без сеттера (вычисляемые и алиасы) пропускаются. Строки рецепта
        добавляются через add_row, так как у свойства rows нет сеттера.

        :param model: Восстанавливаемая модель.
        :param source: Словарь с полями модели.
        :param cache: Восстановленные модели по unique_code.
        """
        for field_name, raw in source.items():
            if field_name == "unique_code":
                continue

            if field_name in ("address", "comments") and raw == "":
                continue

            if isinstance(model, receipt_model) and field_name == "rows":
                if isinstance(raw, list):
                    for row in raw:
                        model.add_row(self.__convert(row, cache))
                continue

            attribute = getattr(type(model), field_name, None)
            if not isinstance(attribute, property) or attribute.fset is None:
                continue

            setattr(model, field_name, self.__convert(raw, cache))
