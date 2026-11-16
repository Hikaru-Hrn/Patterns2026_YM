from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.abstract_model import abstract_model


class entity_reference_helper:
    """Сервисный helper для проверки ссылок между доменными сущностями."""

    @staticmethod
    def is_referenced(target: abstract_model, collections: dict[str, list]) -> bool:
        """Проверяет, ссылается ли любая другая сущность хранилища на target.

        :param target: Проверяемая доменная сущность.
        :param collections: Словарь коллекций хранилища {имя_свойства: список_сущностей}.
        :return: True, если на target есть ссылка, иначе False.
        """
        if not isinstance(target, abstract_model):
            return False

        collection_types = tuple(
            {type(entity) for items in collections.values() for entity in items}
        )

        for items in collections.values():
            for entity in items:
                if entity is target or entity == target:
                    continue
                if entity_reference_helper._references(entity, target, set(), collection_types):
                    return True
        return False

    @staticmethod
    def _references(
        obj: abstract_model,
        target: abstract_model,
        visited: set,
        collection_types: tuple[type, ...],
    ) -> bool:
        """Рекурсивно ищет ссылку на target внутри полей объекта.

        :param obj: Текущий проверяемый объект.
        :param target: Искомая сущность.
        :param visited: Множество id уже пройденных объектов (защита от циклов).
        :param collection_types: Классы сущностей верхнего уровня хранилища.
        :return: True, если найдена ссылка на target.
        """
        if obj is None or id(obj) in visited:
            return False
        visited.add(id(obj))

        for field_name in abstract_covertor._get_fields(obj):
            if field_name == "unique_code":
                continue

            value = getattr(obj, field_name, None)
            if isinstance(value, abstract_model):
                if value is target or value == target:
                    return True
                if not isinstance(value, collection_types) and entity_reference_helper._references(
                    value, target, visited, collection_types
                ):
                    return True
            elif isinstance(value, (list, tuple, set)):
                for item in value:
                    if isinstance(item, abstract_model):
                        if item is target or item == target:
                            return True
                        if not isinstance(item, collection_types) and entity_reference_helper._references(
                            item, target, visited, collection_types
                        ):
                            return True
        return False
