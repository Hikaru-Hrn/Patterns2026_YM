from abc import ABC
import uuid
from Src.Core.exception import arguments_exception

"""
Абстрактный класс для наследования моделей
Содержит в себе только генерацию уникального кода
"""


class abstract_model(ABC):
    __unique_code: str

    def __init__(self) -> None:
        super().__init__()
        self.__unique_code = uuid.uuid4().hex

    """
    Уникальный код
    """

    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str):
        if value.strip() == "":
            raise argument_exception("value", "Некорректно передан параметр!")

        self.__unique_code = value.strip()

    """
    Перегрузка штатного варианта сравнения
    """

    def __eq__(self, value) -> bool:
        if not isinstance(value, abstract_model): return False

        return self.unique_code == value.unique_code
