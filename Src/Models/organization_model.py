from Src.Core.entity_model import entity_model
from Src.Core.exception import (
    arguments_exeption,
    max_length_exeption,
    length_exeption,
    validation_exeptoion,
)

class organization_model(entity_model):
    """Модель организации

    Содержит определения:
        - наименование,
        - ИНН,
        - БИК,
        - счёт,
        - форму собственности, их длины/ограничения
    """

    __inn: str = ""
    __bic: str = ""
    __account: str = ""
    __owner: str = ""
    __len_inn: int = 10
    __len_bic: int = 9
    __len_account: int = 20
    __max_len_owner: int = 50

    def __init__(self, name: str = "", inn: str = "", bic: str = "", account: str = "", owner: str = "") -> None:
        """Инициализирует организацию.

        :param name: Наименование организации
        :param inn: ИНН организации
        :param bic: БИК банка
        :param account: Расчётный счёт
        :param owner: Форма собственности / владелец
        """
        super().__init__()
        self.name = name
        self.inn = inn
        self.bic = bic
        self.account = account
        self.owner = owner

    def __check_inn(self, value: str) -> bool:
        """Проверяет контрольную сумму ИНН

        :param value: Строка ИНН длиной 10 символов
        :return: True, если контрольная сумма корректна, иначе False
        """
        total = (2 * int(value[0]) + 4 * int(value[1]) + 10 * int(value[2]) +
                 3 * int(value[3]) + 5 * int(value[4]) + 9 * int(value[5]) +
                 4 * int(value[6]) + 6 * int(value[7]) + 8 * int(value[8]))
        result = total % 11
        if result > 9:
            result %= 10
        return result == int(value[-1])

    def __check_account(self, value: str) -> bool:
        """Проверяет контрольную сумму расчётного счёта

        Использует последние три цифры БИК текущей организации

        :param value: Строка расчётного счёта длиной 20 символов
        :return: True, если контрольная сумма корректна, иначе False
        """
        last = self.bic[-3:]
        new_value = last + value
        cnt = 1
        total = 0
        for i in range(23):
            match cnt:
                case 1:
                    total += 7 * int(new_value[i])
                    cnt += 1
                case 2:
                    total += 1 * int(new_value[i])
                    cnt += 1
                case 3:
                    total += 3 * int(new_value[i])
                    cnt = 1
        return total % 10 == 0

    @property
    def inn(self) -> str:
        """Возвращает ИНН организации"""
        return self.__inn

    @inn.setter
    def inn(self, value: str) -> None:
        """Устанавливает ИНН организации

        :param value: Строка ИНН длиной 10 символов
        :raises arguments_exeption: Если значение не строка или None
        :raises length_exeption: Если длина не равна 10
        :raises validation_exeptoion: Если значение содержит не цифры или контрольная сумма некорректна
        """
        if value is None or not isinstance(value, str):
            raise arguments_exeption("inn", "Некорректно переданный аргумент!")
        if len(value.strip()) != self.__len_inn:
            raise length_exeption("inn", self.__len_inn, "ИНН")
        if value.isdigit() == False:
            raise validation_exeptoion("inn", "ИНН должен состоять только из цифр!")
        if self.__check_inn(value) == False:
            raise validation_exeptoion("inn", "Некорректный ИНН!")
        self.__inn = value

    @property
    def bic(self) -> str:
        """Возвращает БИК банка"""
        return self.__bic

    @bic.setter
    def bic(self, value: str) -> None:
        """Устанавливает БИК банка

        :param value: Строка БИК длиной 9 символов
        :raises arguments_exeption: Если значение не строка или присвоен None
        :raises length_exeption: Если длина не равна 9
        :raises validation_exeptoion: Если значение содержит не цифры
        """
        if value is None or not isinstance(value, str):
            raise arguments_exeption("bic", "Некорректно переданный аргумент!")
        if len(value.strip()) != self.__len_bic:
            raise length_exeption("bic", self.__len_bic, "БИК")
        if value.isdigit() == False:
            raise validation_exeptoion("bic", "БИК должен состоять только из цифр!")
        self.__bic = value

    @property
    def account(self) -> str:
        """Возвращает расчётный счёт"""
        return self.__account

    @account.setter
    def account(self, value: str) -> None:
        """Устанавливает расчётный счёт

        :param value: Строка счёта длиной 20 символов
        :raises arguments_exeption: Если значение не строка или присвоен None
        :raises length_exeption: Если длина не равна 20
        :raises validation_exeptoion: Если значение содержит не цифры или контрольная сумма некорректна
        """
        if value is None or not isinstance(value, str):
            raise arguments_exeption("account", "Некорректно переданный аргумент!")
        if len(value.strip()) != self.__len_account:
            raise length_exeption("account", self.__len_account, "Счет")
        if value.isdigit() == False:
            raise validation_exeptoion("account", "Счет должен состоять только из цифр!")
        if self.__check_account(value) == False:
            raise validation_exeptoion("account", "Некорректный Счет!")
        self.__account = value

    @property
    def owner(self) -> str:
        """Возвращает форму собственности / владельца"""
        return self.__owner

    @owner.setter
    def owner(self, value: str) -> None:
        """Устанавливает форму собственности / владельца

        :param value: Строка длиной не более 50 символов
        :raises arguments_exeption: Если значение не строка или присвоен None
        :raises max_length_exeption: Если длина превышает 50 символов
        """
        if value is None or not isinstance(value, str):
            raise arguments_exeption("owner", "Некорректно переданный аргумент!")
        if len(value.strip()) > self.__max_len_owner:
            raise max_length_exeption("owner", self.__max_len_owner)
        self.__owner = value