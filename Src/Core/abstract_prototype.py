from abc import ABC, abstractmethod

from Src.Dtos.filter_dto import filter_dto


class abstract_prototype(ABC):
    """Абстрактный базовый класс для шаблона 'Прототип' фильтрации данных.

    Определяет контракт создания отфильтрованной копии набора данных
    на основе переданных условий фильтрации.
    """

    @abstractmethod
    def clone(self, filter_dto: filter_dto) -> "abstract_prototype":
        """Создает отфильтрованную копию прототипа.

        :param filter_dto: Условия фильтрации.
        :return: Новый экземпляр прототипа с отфильтрованными данными.
        """
        pass
