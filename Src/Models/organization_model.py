from Src.Core.entity_model import entity_model
from Src.Core.exception import (
    arguments_exception,
    max_length_exception,
    length_exception,
    validation_exception,
)
from Src.Core.validator import validator


class organization_model(entity_model):
    """Модель организации.

    Содержит определения: наименование, ИНН, БИК, счёт,
    форму собственности и их длины/ограничения.
    """

    __inn: str = ""
    __bic: str = ""
    __account: str = ""
    __owner: str = ""
    __len_inn: int = 10
    __len_bic: int = 9
    __len_account: int = 20
    __max_len_owner: int = 50

    def __init__(self, name: str = "", inn: str = "", bic: str = "",
                 account: str = "", owner: str = "") -> None:
        """Инициализирует организацию.

        :param name: Наименование организации.
        :param inn: ИНН организации.
        :param bic: БИК банка.
        :param account: Расчётный счёт.
        :param owner: Форма собственности / владелец.
        """
        super().__init__()
        if name != "":
            self.name = name
        self.inn = inn
        self.bic = bic
        self.account = account
        if owner != "":
            self.owner = owner

    @property
    def inn(self) -> str:
        """Возвращает ИНН организации."""
        return self.__inn

    @inn.setter
    def inn(self, value: str) -> None:
        """Устанавливает ИНН организации.

        :param value: Строка ИНН длиной 10 символов.
        :raises arguments_exception: Если значение не строка или None.
        :raises length_exception: Если длина не равна 10.
        :raises validation_exception: Если значение содержит нецифры
            или контрольная сумма некорректна.
        """
        validator.validate(value, str, "inn", self.__len_inn, document="ИНН")
        validator.digit_validate(value, "inn")
        validator.check_inn(value)
        self.__inn = value

    @property
    def bic(self) -> str:
        """Возвращает БИК банка."""
        return self.__bic

    @bic.setter
    def bic(self, value: str) -> None:
        """Устанавливает БИК банка.

        :param value: Строка БИК длиной 9 символов.
        :raises arguments_exception: Если значение не строка или None.
        :raises length_exception: Если длина не равна 9.
        :raises validation_exception: Если значение содержит нецифры.
        """
        validator.validate(value, str, "bic", self.__len_bic, document="БИК")
        validator.digit_validate(value, "bic")
        self.__bic = value

    @property
    def account(self) -> str:
        """Возвращает расчётный счёт."""
        return self.__account

    @account.setter
    def account(self, value: str) -> None:
        """Устанавливает расчётный счёт.

        :param value: Строка счёта длиной 20 символов.
        :raises arguments_exception: Если значение не строка или None.
        :raises length_exception: Если длина не равна 20.
        :raises validation_exception: Если значение содержит нецифры
            или контрольная сумма некорректна.
        """
        validator.validate(value, str, "account", self.__len_account, document="Счет")
        validator.digit_validate(value, "account")
        validator.check_account(value, self.__bic)
        self.__account = value

    @property
    def owner(self) -> str:
        """Возвращает форму собственности / владельца."""
        return self.__owner

    @owner.setter
    def owner(self, value: str) -> None:
        """Устанавливает форму собственности / владельца.

        :param value: Строка длиной не более 50 символов.
        :raises arguments_exception: Если значение не строка или None.
        :raises max_length_exception: Если длина превышает 50 символов.
        """
        validator.validate(value, str, "owner", max_len=self.__max_len_owner)
        self.__owner = value

