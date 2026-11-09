from datetime import date, datetime, time
from enum import Enum
import importlib
import pkgutil
from typing import Any, Type, get_args, get_origin

from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
import Src.Models


class deserialize_factory(abstract_deserialize_factory):
    """Фабрика рекурсивного восстановления доменных моделей из JSON.

    Тип модели определяется вызывающим кодом или аннотацией свойства (@property),
    поэтому переименование доменных моделей или их полей не требует правки фабрики.
    Восстановленные объекты кэшируются по ``unique_code``, сохраняя общие и
    циклические ссылки на один и тот же экземпляр.
    """

    def create(self, model_type: Type[abstract_model]) -> abstract_model:
        """Создать пустую модель указанного класса.

        :param model_type: Класс доменной модели (наследник abstract_model).
        :return: Экземпляр переданного класса.
        :raises arguments_exception: Если передан не класс доменной модели.
        """
        if not isinstance(model_type, type) or not issubclass(model_type, abstract_model):
            raise arguments_exception("model_type", "Ожидался класс доменной модели!")

        try:
            return model_type()
        except Exception:
            model = object.__new__(model_type)
            abstract_model.__init__(model)
            return model

    def Convert(self, source: Any, model_type: Any = None) -> Any:
        """Рекурсивно восстановить модели из JSON-структуры.

        :param source: Словарь хранилища, словарь модели, список или скаляр.
        :param model_type: Класс модели, ``list[cls]``, словарь ``{ключ: класс}``
            либо контейнер (например, ``storage_manager``) с типизированными @property.
        :return: Словарь коллекций, модель, список или скаляр.
        :raises arguments_exception: Если source равен None или тип модели
            определить нельзя.
        """
        if source is None:
            raise arguments_exception("source", "Некорректно переданный аргумент!")

        resolved_target = self.__extract_schema(model_type)
        return self.__convert(source, resolved_target, {}, set())

    def __convert(self, source: Any, model_type: Any, cache: dict, filling: set) -> Any:
        """Рекурсивно преобразовать JSON-узел в доменные модели или скаляры.

        :param source: Текущий узел JSON.
        :param model_type: Ожидаемый тип узла или словарь {ключ: класс}.
        :param cache: Восстановленные модели по unique_code.
        :param filling: Множество unique_code моделей, находящихся в процессе заполнения.
        :return: Модель, список, словарь коллекций или скаляр.
        :raises arguments_exception: Если для JSON-словаря не задан тип модели.
        """
        if source is None:
            return None

        if isinstance(model_type, dict):
            if not isinstance(source, dict):
                raise arguments_exception("source", "Ожидался словарь коллекций JSON!")
            return {
                key: self.__convert(value, model_type[key], cache, filling)
                for key, value in source.items()
                if key in model_type
            }

        if isinstance(source, dict):
            if not isinstance(model_type, type) or not issubclass(model_type, abstract_model):
                raise arguments_exception(
                    "model_type",
                    "Не удалось определить тип модели для JSON-словаря!",
                )
            return self.__convert_model(source, model_type, cache, filling)

        if isinstance(source, list):
            element_type = self.__resolve_type(self.__element_type(model_type))
            return [self.__convert(item, element_type, cache, filling) for item in source]

        return self.__convert_scalar(source, model_type)

    def __convert_model(
        self,
        source: dict,
        model_type: Type[abstract_model],
        cache: dict,
        filling: set,
    ) -> abstract_model:
        """Создать модель и заполнить её поля с учётом кэша ссылок и циклов.

        :param source: Словарь с полями модели.
        :param model_type: Класс создаваемой модели.
        :param cache: Восстановленные модели по unique_code.
        :param filling: Множество unique_code моделей в текущем стеке заполнения.
        :return: Заполненный экземпляр модели.
        """
        unique_code = source.get("unique_code")
        has_code = isinstance(unique_code, str) and unique_code.strip() != ""
        if has_code:
            unique_code = unique_code.strip()
            if unique_code in cache:
                model = cache[unique_code]
                if unique_code not in filling:
                    filling.add(unique_code)
                    try:
                        self.__fill(model, source, cache, filling)
                    finally:
                        filling.remove(unique_code)
                return model

        model = self.create(model_type)
        if has_code:
            model.unique_code = unique_code
            cache[unique_code] = model
            filling.add(unique_code)

        try:
            self.__fill(model, source, cache, filling)
        finally:
            if has_code:
                filling.discard(unique_code)

        return model

    def __fill(self, model: abstract_model, source: dict, cache: dict, filling: set) -> None:
        """Заполнить свойства модели значениями из JSON в порядке MRO класса.

        Тип каждого значения берётся из аннотации геттера. Поля без сеттера
        и значения, совпадающие с текущими дефолтными, пропускаются.

        :param model: Восстанавливаемая модель.
        :param source: Словарь с полями модели.
        :param cache: Восстановленные модели по unique_code.
        :param filling: Множество unique_code моделей в текущем стеке заполнения.
        """
        for field_name in abstract_covertor._get_fields(model):
            if field_name == "unique_code" or field_name not in source:
                continue

            attribute = getattr(type(model), field_name, None)
            if not isinstance(attribute, property) or attribute.fset is None:
                continue

            annotation = attribute.fget.__annotations__.get("return")
            target_type = self.__resolve_type(annotation)
            value = self.__convert(source[field_name], target_type, cache, filling)

            if value is None:
                continue

            try:
                if getattr(model, field_name) == value:
                    continue
            except Exception:
                pass

            setattr(model, field_name, value)

    @staticmethod
    def __convert_scalar(source: Any, model_type: Any) -> Any:
        """Преобразовать скалярное значение с учётом ожидаемого типа (Enum, ISO-дата).

        :param source: Скалярное значение из JSON.
        :param model_type: Ожидаемый тип свойства.
        :return: Преобразованное значение.
        """
        if isinstance(source, str) and isinstance(model_type, type):
            if issubclass(model_type, Enum):
                if hasattr(model_type, "from_string"):
                    return model_type.from_string(source)
                if source in model_type.__members__:
                    return model_type[source]
            if issubclass(model_type, datetime):
                return datetime.fromisoformat(source)
            if issubclass(model_type, date):
                return date.fromisoformat(source)
            if issubclass(model_type, time):
                return time.fromisoformat(source)
        return source

    @classmethod
    def __extract_schema(cls, target: Any) -> Any:
        """Извлечь схему коллекций из контейнера, если передан менеджер или его класс.

        :param target: Класс модели, список, словарь типов или объект/класс контейнера.
        :return: Исходный тип либо словарь {имя_свойства: тип_элемента}.
        """
        if target is None or isinstance(target, dict) or get_origin(target) is not None:
            return target

        if isinstance(target, type) and issubclass(target, abstract_model):
            return target

        container_cls = target if isinstance(target, type) else type(target)
        schema = {}
        for cls_item in reversed(container_cls.__mro__):
            for name, attribute in cls_item.__dict__.items():
                if name.startswith("_") or not isinstance(attribute, property) or attribute.fget is None:
                    continue
                element_type = cls.__element_type(attribute.fget.__annotations__.get("return"))
                if element_type is not None:
                    schema[name] = cls.__resolve_type(element_type)

        return schema if len(schema) > 0 else target

    @staticmethod
    def __element_type(model_type: Any) -> Any:
        """Вернуть тип элемента списка из аннотации вида ``list[cls]``.

        :param model_type: Аннотация списка или иной тип.
        :return: Тип элемента списка либо None.
        """
        if isinstance(model_type, type) and issubclass(model_type, abstract_model):
            return model_type
        if get_origin(model_type) in (list, tuple, set):
            args = get_args(model_type)
            return args[0] if args else None
        return None

    @classmethod
    def __resolve_type(cls, annotation: Any) -> Any:
        """Разрешить строковую аннотацию в класс модели без жёстких импортов.

        :param annotation: Аннотация геттера.
        :return: Класс модели, иной тип или None.
        :raises arguments_exception: Если строковая аннотация неизвестна.
        """
        if not isinstance(annotation, str):
            return annotation

        name = annotation.strip().strip("\"'")
        registry = cls.__model_registry()
        if name not in registry:
            cls.__load_models_package()
            registry = cls.__model_registry()

        if name not in registry:
            raise arguments_exception(
                "model_type",
                f"Неизвестный тип модели '{annotation}'!",
            )
        return registry[name]

    @staticmethod
    def __load_models_package() -> None:
        """Динамически загрузить все модули пакета Src.Models без привязки к именам."""
        for module_info in pkgutil.iter_modules(Src.Models.__path__):
            importlib.import_module(f"{Src.Models.__name__}.{module_info.name}")

    @staticmethod
    def __model_registry() -> dict:
        """Собрать все загруженные наследники abstract_model по имени класса.

        :return: Словарь {имя класса: класс модели}.
        """
        registry = {}
        stack = list(abstract_model.__subclasses__())
        while stack:
            model_type = stack.pop()
            registry[model_type.__name__] = model_type
            stack.extend(model_type.__subclasses__())
        return registry
