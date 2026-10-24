from typing import Any

from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception


class reference_convertor(abstract_covertor):
    """Конвертер ссылок (Reference) на доменные модели в словарь.

    Ссылка раскрывается в полный вложенный словарь объекта. Если в рамках одной
    сериализации объект встречается повторно или образует цикл, вместо
    повторного раскрытия возвращается дескриптор {"unique_code", "name"}.
    """

    def Convert(self, source: Any, factory=None, seen=None) -> dict:
        """Преобразовать ссылку или объект в словарь Reference-полей.

        :param source: Доменная модель или объект с публичными свойствами.
        :param factory: Экземпляр convert_factory для рекурсивного раскрытия.
            Передаётся фабрикой, чтобы сохранять общий контекст обхода.
        :param seen: Множество id уже сериализованных объектов. Нужно для
            защиты от повторного раскрытия и циклических ссылок.
        :return: Словарь в формате {наименование_поля: данные_поля}.
        :raises arguments_exception: Если source равен None или является
            неподдерживаемым скалярным значением.
        """
        self._validate_source(source)

        if factory is None:
            # Локальный импорт исключает циклическую зависимость модулей.
            from Src.Logics.convert_factory import convert_factory

            factory = convert_factory()

        if isinstance(source, abstract_model):
            if seen is None:
                return factory.Convert(source)
            return factory.convert_model(source, seen)

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

            if isinstance(value, abstract_model):
                result[field_name] = factory.convert_model(value, visited)

        return result
