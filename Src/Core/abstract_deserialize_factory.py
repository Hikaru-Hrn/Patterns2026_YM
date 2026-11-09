from abc import ABC, abstractmethod
from typing import Any, Type

from Src.Core.abstract_model import abstract_model


class abstract_deserialize_factory(ABC):
    """Абстрактная фабрика восстановления доменных моделей из JSON.

    Задаёт контракт: ``create`` создаёт пустую модель переданного класса,
    ``Convert`` рекурсивно заполняет её поля и вложенные ссылки. Конкретная
    реализация сама решает, как определять типы вложенных объектов.
    """

    @abstractmethod
    def create(self, model_type: Type[abstract_model]) -> abstract_model:
        """Создать пустую модель указанного класса.

        :param model_type: Класс доменной модели.
        :return: Экземпляр переданного класса.
        """
        pass

    @abstractmethod
    def Convert(self, source: Any, model_type: Any = None) -> Any:
        """Рекурсивно восстановить модели из JSON-структуры.

        :param source: Словарь, список или скалярное значение.
        :param model_type: Класс модели, класс списка (``list[cls]``) или
            словарь ``{ключ: класс}`` для корневого набора коллекций.
        :return: Модель, словарь моделей, список или скаляр.
        """
        pass

    def convert(self, source: Any, model_type: Any = None) -> Any:
        """snake_case-алиас метода Convert.

        :param source: Словарь, список или скалярное значение.
        :param model_type: Класс модели, класс списка или словарь классов.
        :return: Модель, словарь моделей, список или скаляр.
        """
        return self.Convert(source, model_type)
