from abc import ABC, abstractmethod
import uuid

class AbstractClass(ABC):
    def __init__(self):
        self.__id = uuid.uuid4()
        self.__name = None

    @abstractmethod
    def set_name(self, name):
        if name is not None:
            self.__name = name
        else:
            raise ValueError("Имя должно быть заполнено")

    @abstractmethod
    @property
    def name(self):
        return self.__name

    @abstractmethod
    @property
    def id(self):
        return self.__id



