from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception


class filter_index:
    """Индекс доменных сущностей для быстрой фильтрации без полного перебора.

    Строит индексы по наименованию, уникальному коду и связям между моделями
    один раз при изменении данных. Все последующие фильтрации выполняются
    преимущественно по ключу O(1) или по списку ключей.
    """

    # Индекс по наименованию: {collection_name: {name_lower: [entity, ...]}}
    __name_index: dict = {}
    # Индекс по уникальному коду: {collection_name: {unique_code: entity}}
    __code_index: dict = {}
    # Индекс обратных связей: {(collection_name, field_name, related_code): [entity, ...]}
    __relation_index: dict = {}

    def __init__(self) -> None:
        """Инициализирует пустой индекс."""
        self.__name_index = {}
        self.__code_index = {}
        self.__relation_index = {}

    def build(self, collections: dict[str, list]) -> None:
        """Перестраивает индексы по переданным коллекциям.

        :param collections: Словарь {имя_коллекции: список_сущностей}.
        """
        if not isinstance(collections, dict):
            raise arguments_exception("collections", "Ожидался словарь коллекций")

        self.__name_index = {}
        self.__code_index = {}
        self.__relation_index = {}

        for collection_name, items in collections.items():
            self.__index_collection(collection_name, items)

    def __index_collection(self, collection_name: str, items: list) -> None:
        """Индексирует одну коллекцию сущностей.

        :param collection_name: Имя коллекции.
        :param items: Список доменных сущностей.
        """
        for entity in items:
            if not isinstance(entity, abstract_model):
                continue

            self.__index_scalar(collection_name, entity)
            self.__index_relations(collection_name, entity)

    def __index_scalar(self, collection_name: str, entity: abstract_model) -> None:
        """Индексирует скалярные поля name и unique_code сущности.

        :param collection_name: Имя коллекции.
        :param entity: Доменная сущность.
        """
        code = getattr(entity, "unique_code", None)
        if isinstance(code, str) and code.strip() != "":
            self.__code_index.setdefault(collection_name, {})[code] = entity

        name = getattr(entity, "name", None)
        if isinstance(name, str) and name.strip() != "":
            self.__name_index.setdefault(collection_name, {}).setdefault(name.lower(), []).append(entity)

    def __index_relations(self, collection_name: str, entity: abstract_model, visited: set | None = None) -> None:
        """Индексирует обратные связи от вложенных моделей к родительской сущности.

        :param collection_name: Имя коллекции родительской сущности.
        :param entity: Родительская доменная сущность.
        :param visited: Множество id уже пройденных объектов (защита от циклов).
        """
        if visited is None:
            visited = set()

        object_id = id(entity)
        if object_id in visited:
            return
        visited.add(object_id)

        fields = self.__get_relation_fields(entity)
        for field_name in fields:
            value = getattr(entity, field_name, None)
            if value is None:
                continue

            if isinstance(value, abstract_model):
                self.__register_relation(collection_name, field_name, value, entity)
            elif isinstance(value, (list, tuple, set)):
                for item in value:
                    if isinstance(item, abstract_model):
                        self.__register_relation(collection_name, field_name, item, entity)

    @staticmethod
    def __get_relation_fields(entity: abstract_model) -> list[str]:
        """Возвращает публичные свойства сущности, которые могут содержать связи.

        Исключает базовые поля unique_code и name.

        :param entity: Доменная сущность.
        :return: Список имён свойств.
        """
        result = []
        for item in dir(entity):
            if item.startswith("_") or item in ("unique_code", "name"):
                continue
            attribute = getattr(entity.__class__, item, None)
            if isinstance(attribute, property):
                result.append(item)
        return result

    def __register_relation(self, collection_name: str, field_name: str, related: abstract_model, entity: abstract_model) -> None:
        """Регистрирует одну обратную связь.

        :param collection_name: Имя коллекции родительской сущности.
        :param field_name: Имя поля связи.
        :param related: Связанная модель.
        :param entity: Родительская сущность.
        """
        related_code = getattr(related, "unique_code", None)
        if not isinstance(related_code, str) or related_code.strip() == "":
            return

        key = (collection_name, field_name, related_code)
        self.__relation_index.setdefault(key, []).append(entity)

    def find_by_code(self, collection_name: str, unique_code: str) -> abstract_model | None:
        """Находит сущность по уникальному коду через индекс.

        :param collection_name: Имя коллекции.
        :param unique_code: Уникальный код.
        :return: Сущность или None.
        """
        return self.__code_index.get(collection_name, {}).get(unique_code)

    def find_by_name(self, collection_name: str, name: str) -> list:
        """Находит сущности по точному наименованию через индекс.

        :param collection_name: Имя коллекции.
        :param name: Наименование.
        :return: Список найденных сущностей.
        """
        return self.__name_index.get(collection_name, {}).get(name.lower(), [])

    def find_by_name_like(self, collection_name: str, pattern: str) -> list:
        """Находит сущности по вхождению подстроки в наименование.

        :param collection_name: Имя коллекции.
        :param pattern: Подстрока для поиска.
        :return: Список найденных сущностей.
        """
        pattern_lower = pattern.lower()
        result = []
        names = self.__name_index.get(collection_name, {})
        for name, entities in names.items():
            if pattern_lower in name:
                result.extend(entities)
        return result

    def find_by_relation(self, collection_name: str, field_name: str, related_code: str) -> list:
        """Находит родительские сущности по уникальному коду связанной модели.

        :param collection_name: Имя коллекции родительских сущностей.
        :param field_name: Имя поля связи.
        :param related_code: Уникальный код связанной модели.
        :return: Список родительских сущностей.
        """
        return self.__relation_index.get((collection_name, field_name, related_code), [])

    @property
    def name_index(self) -> dict:
        """Возвращает индекс по наименованиям."""
        return self.__name_index

    @property
    def code_index(self) -> dict:
        """Возвращает индекс по уникальным кодам."""
        return self.__code_index

    @property
    def relation_index(self) -> dict:
        """Возвращает индекс обратных связей."""
        return self.__relation_index
