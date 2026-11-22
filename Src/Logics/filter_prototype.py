from Src.Core.abstract_model import abstract_model
from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.filter_index import filter_index
from Src.Logics.storage_manager import storage_manager


class filter_prototype(abstract_prototype):
    """Универсальный прототип фильтрации доменных моделей.

    Работает с любой доменной коллекцией через предварительно построенный
    filter_index. Поддерживает фильтрацию по собственным полям модели
    и по вложенным связанным сущностям (например, nomenclature.group.name
    или range.base.name) без полного перебора всех объектов.
    """

    __data: list = []
    __collection_name: str = ""

    def __init__(self, data: list, collection_name: str = "") -> None:
        """Инициализирует прототип фильтрации.

        :param data: Исходный список доменных сущностей.
        :param collection_name: Имя коллекции в хранилище.
        """
        self.__data = list(data) if data is not None else []
        self.__collection_name = collection_name

    @property
    def data(self) -> list:
        """Возвращает текущий набор данных прототипа."""
        return list(self.__data)

    def clone(self, filter_dto: filter_dto) -> "filter_prototype":
        """Создает отфильтрованную копию прототипа.

        :param filter_dto: Условия фильтрации.
        :return: Новый экземпляр filter_prototype с отфильтрованными данными.
        :raises arguments_exception: Если фильтр не задан.
        """
        if filter_dto is None:
            raise arguments_exception("filter_dto", "Фильтр не может быть None")

        filters = filter_dto.filters
        if len(filters) == 0:
            return filter_prototype(self.__data, self.__collection_name)

        result = {entity.unique_code: entity for entity in self.__data}
        index = self.__get_index()

        for item in filters:
            filtered = self.__apply_filter(item, index)
            allowed_codes = {entity.unique_code for entity in filtered}
            result = {
                code: entity
                for code, entity in result.items()
                if code in allowed_codes
            }
            if not result:
                break

        return filter_prototype(list(result.values()), self.__collection_name)

    def __apply_filter(self, item: filter_item_dto, index: filter_index) -> list:
        """Применяет одно условие фильтрации к текщему набору данных.

        :param item: Условие фильтрации.
        :param index: Индекс доменных сущностей.
        :return: Список сущностей, удовлетворяющих условию.
        """
        path = [part.strip() for part in item.field_name.split(".") if part.strip()]
        if len(path) == 0:
            raise arguments_exception("field_name", "Имя поля фильтра не может быть пустым")

        return self.__filter_by_path(
            self.__collection_name,
            self.__data,
            path,
            item.value,
            item.filter_type,
            index,
            cache={},
        )

    def __filter_by_path(
        self,
        collection_name: str,
        entities: list,
        path: list[str],
        value: str,
        filter_type: filter_type_enum,
        index: filter_index,
        cache: dict,
    ) -> list:
        """Рекурсивно фильтрует сущности по пути из имён полей.

        :param collection_name: Имя текущей коллекции.
        :param entities: Набор сущностей для фильтрации.
        :param path: Оставшийся путь полей.
        :param value: Искомое значение.
        :param filter_type: Тип сравнения.
        :param index: Индекс сущностей.
        :param cache: Кэш промежуточных результатов фильтрации.
        :return: Список отфильтрованных сущностей.
        """
        cache_key = (collection_name, tuple(path), value, filter_type.value)
        if cache_key in cache:
            return cache[cache_key]

        result = self.__filter_by_path_internal(
            collection_name, entities, path, value, filter_type, index, cache
        )
        cache[cache_key] = result
        return result

    def __filter_by_path_internal(
        self,
        collection_name: str,
        entities: list,
        path: list[str],
        value: str,
        filter_type: filter_type_enum,
        index: filter_index,
        cache: dict,
    ) -> list:
        """Внутренняя реализация рекурсивной фильтрации по пути полей."""
        if len(path) == 1 and path[0] in ("name", "unique_code"):
            return self.__filter_scalar(collection_name, path[0], value, filter_type, index)

        if len(path) == 1:
            # Одиночное поле связи: ищем по уникальному коду связанной сущности
            return self.__filter_by_relation(
                entities, path[0], value, filter_type, index
            )

        first_field = path[0]
        rest = path[1:]

        related_collection = self.__resolve_related_collection(collection_name, first_field, entities)
        if related_collection is None:
            return []

        all_related = self.__get_collection(related_collection)
        filtered_related = self.__filter_by_path(
            related_collection,
            all_related,
            rest,
            value,
            filter_type,
            index,
            cache,
        )

        result = self.__filter_parents_by_related(
            entities, first_field, filtered_related, index
        )
        return result

    def __filter_scalar(
        self,
        collection_name: str,
        field: str,
        value: str,
        filter_type: filter_type_enum,
        index: filter_index,
    ) -> list:
        """Фильтрует сущности по прямому скалярному полю через индекс.

        :param collection_name: Имя коллекции.
        :param field: Имя поля (name или unique_code).
        :param value: Искомое значение.
        :param filter_type: Тип сравнения.
        :param index: Индекс сущностей.
        :return: Список найденных сущностей.
        """
        if field == "unique_code":
            entity = index.find_by_code(collection_name, value)
            return [entity] if entity is not None else []

        if filter_type == filter_type_enum.EQUALS:
            return index.find_by_name(collection_name, value)

        return index.find_by_name_like(collection_name, value)

    def __filter_by_relation(
        self,
        entities: list,
        field_name: str,
        value: str,
        filter_type: filter_type_enum,
        index: filter_index,
    ) -> list:
        """Фильтрует сущности по уникальному коду связанной модели.

        :param entities: Набор сущностей.
        :param field_name: Имя поля связи.
        :param value: Искомый уникальный код связанной сущности.
        :param filter_type: Тип сравнения.
        :param index: Индекс сущностей.
        :return: Список сущностей, у которых связь указывает на искомый код.
        """
        if filter_type == filter_type_enum.EQUALS:
            return index.find_by_relation(self.__collection_name, field_name, value)

        # LIKE по коду связанной сущности: находим подходящие коды через индекс
        related_collection = self.__resolve_related_collection(self.__collection_name, field_name, entities)
        if related_collection is None:
            return []

        matched = index.find_by_name_like(related_collection, value)
        result = []
        for related in matched:
            result.extend(index.find_by_relation(self.__collection_name, field_name, related.unique_code))
        return result

    def __filter_parents_by_related(
        self,
        entities: list,
        field_name: str,
        related_entities: list,
        index: filter_index,
    ) -> list:
        """Оставляет только те сущности, которые ссылаются на найденные связанные.

        :param entities: Родительские сущности.
        :param field_name: Имя поля связи.
        :param related_entities: Связанные сущности, удовлетворяющие фильтру.
        :param index: Индекс сущностей.
        :return: Список родительских сущностей.
        """
        if len(related_entities) == 0:
            return []

        codes = {r.unique_code for r in related_entities if isinstance(r, abstract_model)}
        if len(codes) == 0:
            return []

        result = []
        for entity in entities:
            value = getattr(entity, field_name, None)
            if isinstance(value, abstract_model) and value.unique_code in codes:
                result.append(entity)
            elif isinstance(value, (list, tuple, set)):
                if any(isinstance(v, abstract_model) and v.unique_code in codes for v in value):
                    result.append(entity)
        return result

    def __resolve_related_collection(self, collection_name: str, field_name: str, entities: list) -> str | None:
        """Определяет имя коллекции связанной модели по имени поля.

        Анализирует сущности из текущей коллекции и ищет первую непустую связь.

        :param collection_name: Имя текущей коллекции.
        :param field_name: Имя поля связи.
        :param entities: Набор сущностей для анализа.
        :return: Имя коллекции связанной модели или None.
        """
        for sample in entities:
            value = getattr(sample, field_name, None)
            if value is None:
                continue

            if isinstance(value, abstract_model):
                return self.__find_collection_name(value)

            if isinstance(value, (list, tuple, set)) and len(value) > 0:
                first = next((item for item in value if isinstance(item, abstract_model)), None)
                if first is not None:
                    return self.__find_collection_name(first)

        return None

    def __find_collection_name(self, entity: abstract_model) -> str | None:
        """Находит имя коллекции в хранилище по экземпляру модели.

        :param entity: Доменная сущность.
        :return: Имя свойства коллекции в storage_manager или None.
        """
        entity_type = type(entity)
        collections = storage_manager().collection_models
        for prop_name, model_cls in collections.items():
            if entity_type is model_cls or issubclass(entity_type, model_cls):
                return prop_name
        return None

    def __get_collection(self, collection_name: str) -> list:
        """Возвращает коллекцию сущностей из хранилища по имени.

        :param collection_name: Имя коллекции.
        :return: Список сущностей.
        """
        try:
            return getattr(storage_manager(), collection_name, [])
        except Exception:
            return []

    def __get_index(self) -> filter_index:
        """Возвращает актуальный индекс доменных сущностей.

        :return: Экземпляр filter_index.
        """
        return storage_manager().get_filter_index()
