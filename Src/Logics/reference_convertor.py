from typing import Any

from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception


class reference_convertor(abstract_covertor):
    """Конвертер ссылок (Reference) на доменные модели.

    Конвертер не зависит от конкретной фабрики: при необходимости рекурсивного
    раскрытия ему передаётся абстрактная фабрика через параметр factory или
    конструктор. Без фабрики возвращается краткий дескриптор ссылки с
    уникальным кодом и наименованием.
    """

    def __init__(self, factory: abstract_convert_factory = None) -> None:
        """Создать конвертер ссылок.

        :param factory: Абстрактная фабрика для полного раскрытия ссылок.
            Может быть None, если достаточно краткого описания ссылки.
        """
        self.__factory = factory

    def Convert(
        self,
        source: Any,
        factory: abstract_convert_factory = None,
        seen=None,
    ) -> dict:
        """Преобразовать ссылку или объект в словарь Reference-полей.

        Если передана фабрика (явно или через конструктор), ссылка
        раскрывается полностью. Если фабрики нет, возвращается краткий
        дескриптор {"unique_code", "name"}.

        :param source: Доменная модель или объект с публичными свойствами.
        :param factory: Абстрактная фабрика для рекурсивного раскрытия.
        :param seen: Множество id объектов в текущем пути рекурсии.
        :return: Словарь в формате {наименование_поля: данные_поля}.
        :raises arguments_exception: Если source равен None или является
            неподдерживаемым скалярным значением.
        """
        self._validate_source(source)

        current_factory = factory or self.__factory

        if isinstance(source, abstract_model):
            if current_factory is None:
                return self.__make_short_reference(source)
            return current_factory.Convert(source, seen)

        if isinstance(source, (str, int, float, bool, bytes)):
            raise arguments_exception(
                "source",
                "reference_convertor принимает только объекты и ссылки!",
            )

        visited = set() if seen is None else seen
        result = {}
        for field_name in self._get_fields(source):
            try:
                value = getattr(source, field_name)
            except Exception:
                continue

            if not isinstance(value, abstract_model):
                continue

            if current_factory is None:
                result[field_name] = self.__make_short_reference(value)
            else:
                result[field_name] = current_factory.Convert(value, visited)

        return result

    @staticmethod
    def __make_short_reference(source: abstract_model) -> dict:
        """Сформировать краткий дескриптор ссылки.

        :param source: Доменная модель, на которую указывает ссылка.
        :return: Словарь с unique_code и (при наличии) name.
        """
        result = {"unique_code": source.unique_code}

        try:
            name = getattr(source, "name", None)
        except Exception:
            name = None

        if isinstance(name, str) and name.strip() != "":
            result["name"] = name

        return result
