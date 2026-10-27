from abc import ABC, abstractmethod
from typing import Any

from Src.Core.abstract_covertor import abstract_covertor


class abstract_convert_factory(ABC):
    """Абстрактная фабрика конвертеров.

    Задаёт семейство продуктов (basic, datetime, reference) и единый способ
    подбора конвертера по типу переданного объекта. Конкретная реализация
    обязана вернуть соответствующие экземпляры конвертеров и реализовать
    рекурсивное преобразование составных объектов.
    """

    @abstractmethod
    def create_basic(self) -> abstract_covertor:
        """Создать конвертер простых типов.

        :return: Экземпляр basic_convertor.
        """
        pass

    @abstractmethod
    def create_datetime(self) -> abstract_covertor:
        """Создать конвертер даты и времени.

        :return: Экземпляр datetime_convertor.
        """
        pass

    @abstractmethod
    def create_reference(self) -> abstract_covertor:
        """Создать конвертер ссылок.

        :return: Экземпляр reference_convertor.
        """
        pass

    @abstractmethod
    def create(self, source: Any) -> abstract_covertor:
        """Подобрать конвертер по типу переданного значения.

        :param source: Значение, для которого нужен конвертер.
        :return: Один из конвертеров семейства.
        """
        pass

    @abstractmethod
    def Convert(self, source: Any, seen=None) -> Any:
        """Рекурсивно преобразовать объект в JSON-совместимую структуру.

        :param source: Любой объект.
        :param seen: Множество id объектов в текущем пути рекурсии.
        :return: Словарь, список или скаляр.
        """
        pass

    def convert(self, source: Any, seen=None) -> Any:
        """snake_case-алиас метода Convert.

        :param source: Любой объект.
        :param seen: Множество id объектов в текущем пути рекурсии.
        :return: Словарь, список или скаляр.
        """
        return self.Convert(source, seen)
