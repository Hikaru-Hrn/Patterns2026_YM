from Src.Core.entity_model import entity_model
from Src.Core.validator import validator

"""
Модель для хранения результата формирования отчета
"""
class report_result_dto(entity_model):
    __text: str = ""
    __binary: list

    """
    Тестовый результат
    """
    @property
    def text(self) -> str:
        return self.__text

    """
    Бинарный результат
    """
    @property
    def binary(self) -> list:
        return self.__binary

    @text.setter
    def text(self, value: str) -> None:
        validator.validate(value, str)
        self.__text = value
        self.__binary = []

    @binary.setter
    def binary(self, value: list) -> None:
        if len(value) > 0:
            self.__text = ""
            self.__binary = value
