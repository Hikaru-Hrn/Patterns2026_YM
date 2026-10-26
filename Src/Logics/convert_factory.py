from typing import Any

from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory(abstract_convert_factory):
    """Конкретная фабрика конвертеров и рекурсивного преобразования объектов.

    Фабрика создаёт семейство конвертеров (basic, datetime, reference),
    подбирает нужный по типу значения и обходит составные объекты: списки,
    словари и доменные модели. Повторные ссылки раскрываются полностью, а
    циклические — заменяются кратким дескриптором.
    """

    def __init__(self) -> None:
        """Создать фабрику и её семейство конвертеров."""
        self.__basic = self.create_basic()
        self.__datetime = self.create_datetime()
        self.__reference = self.create_reference()

    @property
    def basic(self) -> abstract_covertor:
        """Вернуть конвертер простых типов."""
        return self.__basic

    @property
    def datetime(self) -> abstract_covertor:
        """Вернуть конвертер даты и времени."""
        return self.__datetime

    @property
    def reference(self) -> abstract_covertor:
        """Вернуть конвертер ссылок."""
        return self.__reference

    def create_basic(self) -> abstract_covertor:
        """Создать конвертер простых типов.

        :return: Экземпляр basic_convertor.
        """
        return basic_convertor()

    def create_datetime(self) -> abstract_covertor:
        """Создать конвертер даты и времени.

        :return: Экземпляр datetime_convertor.
        """
        return datetime_convertor()

    def create_reference(self) -> abstract_covertor:
        """Создать конвертер ссылок, связанный с текущей фабрикой.

        :return: Экземпляр reference_convertor.
        """
        return reference_convertor(factory=self)

    def create(self, source: Any) -> abstract_covertor:
        """Подобрать конвертер по типу переданного значения.

        :param source: Значение, для которого нужно выбрать конвертер.
        :return: Экземпляр basic_convertor, datetime_convertor или
            reference_convertor.
        :raises arguments_exception: Если тип значения не поддерживается.
        """
        if source is None or self.__basic.is_basic(source):
            return self.__basic

        if self.__datetime.is_datetime(source):
            return self.__datetime

        if isinstance(source, abstract_model):
            return self.__reference

        raise arguments_exception(
            "source",
            f"Для типа {type(source).__name__} не найден подходящий конвертер!",
        )

    def Convert(self, source: Any, seen=None) -> Any:
        """Преобразовать любой объект в структуру словарей и списков.

        Для доменной модели возвращается вложенный словарь её полей. Ссылки
        раскрываются полностью, а объект, образующий цикл, заменяется
        дескриптором {"unique_code", "name"}.

        :param source: Любой объект: модель, скаляр, список, словарь или
            объект с публичными свойствами.
        :param seen: Множество id объектов в текущем пути рекурсии.
        :return: JSON-совместимая структура данных.
        :raises arguments_exception: Если source равен None.
        """
        if source is None:
            raise arguments_exception("source", "Некорректно переданный аргумент!")

        visited = set() if seen is None else seen
        return self.__convert(source, visited)

    def __convert(self, source: Any, seen) -> Any:
        """Рекурсивно преобразовать значение в JSON-совместимую структуру.

        :param source: Преобразуемое значение.
        :param seen: Множество id объектов в текущем пути рекурсии.
        :return: Словарь, список, скаляр или None.
        """
        if source is None:
            return None

        if self.__basic.is_basic(source):
            return self.__basic.to_value(source)

        if self.__datetime.is_datetime(source):
            return self.__datetime.to_value(source)

        if isinstance(source, abstract_model):
            return self.__convert_model(source, seen)

        if isinstance(source, (list, tuple, set)):
            return [self.__convert(item, seen) for item in source]

        if isinstance(source, dict):
            return {
                key: self.__convert(value, seen)
                for key, value in source.items()
            }

        if len(abstract_covertor._get_fields(source)) > 0:
            return self.__convert_object(source, seen)

        # Для объектов без публичных свойств оставляем читаемое представление,
        # чтобы результат гарантированно можно было сериализовать в JSON.
        return str(source)

    def __convert_model(self, source: abstract_model, seen) -> dict:
        """Преобразовать доменную модель с защитой от циклов.

        Объект добавляется в путь рекурсии только на время обхода. Поэтому
        повторная ссылка в соседней ветке раскрывается полностью, а ссылка
        на предка заменяется кратким дескриптором.

        :param source: Доменная модель.
        :param seen: Множество id объектов в текущем пути рекурсии.
        :return: Словарь полей модели или дескриптор циклической ссылки.
        """
        object_id = id(source)
        if object_id in seen:
            return self.__make_reference_link(source)

        seen.add(object_id)
        try:
            return self.__convert_object(source, seen)
        finally:
            seen.remove(object_id)

    def __convert_object(self, source: Any, seen) -> dict:
        """Преобразовать объект, обходя его публичные свойства.

        Поля-алиасы, возвращающие тот же объект или тот же список моделей,
        пропускаются, чтобы не дублировать данные (например, items и recipe).

        :param source: Объект с публичными @property.
        :param seen: Множество id объектов в текущем пути рекурсии.
        :return: Словарь в формате {наименование_поля: данные_поля}.
        """
        result = {}
        processed_values = set()

        for field_name in abstract_covertor._get_fields(source):
            try:
                value = getattr(source, field_name)
            except Exception:
                continue

            signature = self.__value_signature(value)
            if signature is not None:
                if signature in processed_values:
                    continue
                processed_values.add(signature)

            if isinstance(value, abstract_model):
                result[field_name] = self.__reference.Convert(
                    value,
                    factory=self,
                    seen=seen,
                )
            else:
                result[field_name] = self.__convert(value, seen)

        return result

    @staticmethod
    def __value_signature(value: Any):
        """Построить сигнатуру значения для отсечения полей-алиасов.

        Сравниваются только ссылки на модели и коллекции моделей. Скалярные
        значения не сравниваются, чтобы не потерять легитимные одинаковые
        числа или строки.

        :param value: Значение поля.
        :return: Хешируемая сигнатура или None, если значение не сравнивается.
        """
        if isinstance(value, (list, tuple, set)):
            items = list(value)
            if len(items) == 0:
                return None
            if all(isinstance(item, abstract_model) for item in items):
                return ("model_list", tuple(id(item) for item in items))
            return None

        if isinstance(value, dict):
            values = list(value.values())
            if len(values) == 0:
                return None
            if all(isinstance(item, abstract_model) for item in values):
                return (
                    "model_dict",
                    tuple(sorted((str(key), id(item)) for key, item in value.items())),
                )
            return None

        if isinstance(value, abstract_model):
            return ("model", id(value))

        return None

    @staticmethod
    def __make_reference_link(source: abstract_model) -> dict:
        """Сформировать дескриптор циклической ссылки.

        :param source: Доменная модель, которая уже есть в пути рекурсии.
        :return: Словарь {"unique_code": ..., "name": ...}.
        """
        result = {}

        try:
            unique_code = getattr(source, "unique_code", None)
        except Exception:
            unique_code = None
        if isinstance(unique_code, str) and unique_code.strip() != "":
            result["unique_code"] = unique_code

        try:
            name = getattr(source, "name", None)
        except Exception:
            name = None
        if isinstance(name, str) and name.strip() != "":
            result["name"] = name

        if len(result) == 0:
            result["type"] = type(source).__name__

        return result
