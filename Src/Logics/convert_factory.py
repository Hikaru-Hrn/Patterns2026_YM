from typing import Any

from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory:
    """Фабрика конвертации объектов в словари согласно их структуре.

    Фабрика хранит экземпляры basic_convertor, datetime_convertor и
    reference_convertor и выбирает нужный конвертер по типу значения.
    Составные объекты обходятся рекурсивно: списки преобразуются в списки
    словарей, словари — в словари, а ссылки на доменные модели раскрываются
    в полные вложенные словари.
    """

    def __init__(self) -> None:
        """Создать фабрику и инициализировать набор конвертеров."""
        self.__basic = basic_convertor()
        self.__datetime = datetime_convertor()
        self.__reference = reference_convertor()

    @property
    def basic(self) -> basic_convertor:
        """Вернуть конвертер простых типов."""
        return self.__basic

    @property
    def datetime(self) -> datetime_convertor:
        """Вернуть конвертер даты и времени."""
        return self.__datetime

    @property
    def reference(self) -> reference_convertor:
        """Вернуть конвертер ссылок на доменные модели."""
        return self.__reference

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

    def Convert(self, source: Any) -> Any:
        """Преобразовать любой объект в структуру словарей и списков.

        Для доменной модели возвращается вложенный словарь её полей. Ссылки
        раскрываются полностью, а повторно встречающиеся объекты заменяются
        дескриптором {"unique_code", "name"}, что защищает от циклов.

        :param source: Любой объект: модель, скаляр, список, словарь или
            объект с публичными свойствами.
        :return: JSON-совместимая структура данных.
        :raises arguments_exception: Если source равен None.
        """
        if source is None:
            raise arguments_exception("source", "Некорректно переданный аргумент!")

        return self.__convert(source, set())

    def convert(self, source: Any) -> Any:
        """snake_case-алиас метода Convert.

        :param source: Объект для преобразования.
        :return: JSON-совместимая структура данных.
        :raises arguments_exception: Если source равен None.
        """
        return self.Convert(source)

    def convert_model(self, source: abstract_model, seen=None) -> dict:
        """Преобразовать доменную модель в словарь с учётом контекста обхода.

        Метод используется reference_convertor при рекурсивном раскрытии
        ссылок. Если объект уже встречался, возвращается дескриптор ссылки.

        :param source: Доменная модель (наследник abstract_model).
        :param seen: Множество id уже сериализованных объектов.
        :return: Словарь полей модели или дескриптор повторной ссылки.
        :raises arguments_exception: Если source не является abstract_model.
        """
        if not isinstance(source, abstract_model):
            raise arguments_exception(
                "source",
                "Ожидалась доменная модель (наследник abstract_model)!",
            )

        visited = set() if seen is None else seen
        return self.__convert_model(source, visited)

    def __convert(self, source: Any, seen) -> Any:
        """Рекурсивно преобразовать значение в JSON-совместимую структуру.

        :param source: Преобразуемое значение.
        :param seen: Множество id уже сериализованных объектов.
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
        """Преобразовать доменную модель и защитить обход от повторов.

        :param source: Доменная модель.
        :param seen: Множество id уже сериализованных объектов.
        :return: Словарь полей модели или дескриптор повторной ссылки.
        """
        object_id = id(source)
        if object_id in seen:
            return self.__make_reference_link(source)

        seen.add(object_id)
        return self.__convert_object(source, seen)

    def __convert_object(self, source: Any, seen) -> dict:
        """Преобразовать объект, обходя его публичные свойства.

        :param source: Объект с публичными @property.
        :param seen: Множество id уже сериализованных объектов.
        :return: Словарь в формате {наименование_поля: данные_поля}.
        """
        result = {}

        for field_name in abstract_covertor._get_fields(source):
            try:
                value = getattr(source, field_name)
            except Exception:
                continue

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
    def __make_reference_link(source: abstract_model) -> dict:
        """Сформировать дескриптор повторной или циклической ссылки.

        :param source: Доменная модель, которая уже встречалась при обходе.
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
