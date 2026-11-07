from abc import ABC, abstractmethod
from typing import Any

from Src.Core.abstract_model import abstract_model


class abstract_deserialize_factory(ABC):
    """Абстрактная фабрика восстановления доменных моделей из JSON.

    Задаёт контракт: ``create`` создаёт пустую модель нужного типа по данным
    JSON, ``Convert`` рекурсивно заполняет её поля и вложенные ссылки.
    """

    @abstractmethod
    def create(self, source: dict) -> abstract_model:
        """Создать пустую модель по структуре JSON-словаря.

        :param source: Словарь с полями одной модели.
        :return: Экземпляр соответствующей доменной модели.
        """
        pass

    @abstractmethod
    def Convert(self, source: Any) -> Any:
        """Рекурсивно восстановить модели из JSON-структуры.

        :param source: Словарь, список или скалярное значение.
        :return: Модель, словарь моделей, список или скаляр.
        """
        pass

    def convert(self, source: Any) -> Any:
        """snake_case-алиас метода Convert.

        :param source: Словарь, список или скалярное значение.
        :return: Модель, словарь моделей, список или скаляр.
        """
        return self.Convert(source)
