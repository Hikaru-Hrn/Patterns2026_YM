from datetime import datetime

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


class transaction_model(abstract_model):
    """Модель складской транзакции (движения номенклатуры).

    Описывает операцию прихода или расхода номенклатуры на складе.
    Положительное значение value означает приход, отрицательное — расход.
    """

    __warehouse: warehouse_model = None
    __nomenclature: nomenclature_model = None
    __range: range_model = None
    __value: float = 0.0
    __period: datetime = None

    def __init__(self) -> None:
        """Инициализирует пустую транзакцию."""
        super().__init__()

    @staticmethod
    def create(
        warehouse: warehouse_model,
        nomenclature: nomenclature_model,
        range: range_model,
        value: float,
        period: datetime,
    ) -> "transaction_model":
        """Фабричный метод создания транзакции.

        :param warehouse: Склад движения.
        :param nomenclature: Номенклатура.
        :param range: Единица измерения.
        :param value: Количество (приход > 0, расход < 0).
        :param period: Дата и время операции.
        :return: Заполненный экземпляр transaction_model.
        """
        transaction = transaction_model()
        transaction.warehouse = warehouse
        transaction.nomenclature = nomenclature
        transaction.range = range
        transaction.value = value
        transaction.period = period
        return transaction

    @property
    def warehouse(self) -> warehouse_model:
        """Возвращает склад транзакции."""
        return self.__warehouse

    @warehouse.setter
    def warehouse(self, value: warehouse_model) -> None:
        """Устанавливает склад транзакции.

        :param value: Экземпляр warehouse_model.
        :raises arguments_exception: Если передан неверный тип.
        """
        validator.validate(value, warehouse_model, "warehouse")
        self.__warehouse = value

    @property
    def nomenclature(self) -> nomenclature_model:
        """Возвращает номенклатуру транзакции."""
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        """Устанавливает номенклатуру транзакции.

        :param value: Экземпляр nomenclature_model.
        :raises arguments_exception: Если передан неверный тип.
        """
        validator.validate(value, nomenclature_model, "nomenclature")
        self.__nomenclature = value

    @property
    def range(self) -> range_model:
        """Возвращает единицу измерения транзакции."""
        return self.__range

    @range.setter
    def range(self, value: range_model) -> None:
        """Устанавливает единицу измерения транзакции.

        :param value: Экземпляр range_model.
        :raises arguments_exception: Если передан неверный тип.
        """
        validator.validate(value, range_model, "range")
        self.__range = value

    @property
    def value(self) -> float:
        """Возвращает количество транзакции (приход > 0, расход < 0)."""
        return self.__value

    @value.setter
    def value(self, value: float) -> None:
        """Устанавливает количество транзакции.

        :param value: Числовое значение, не равное нулю.
        :raises arguments_exception: Если значение не число или равно нулю.
        """
        if value is None or not isinstance(value, (int, float)):
            raise arguments_exception("value", "Значение транзакции должно быть числом!")
        if value == 0:
            raise arguments_exception("value", "Значение транзакции не может быть равно нулю!")
        self.__value = float(value)

    @property
    def period(self) -> datetime:
        """Возвращает дату и время транзакции."""
        return self.__period

    @period.setter
    def period(self, value: datetime) -> None:
        """Устанавливает дату и время транзакции.

        :param value: Экземпляр datetime.
        :raises arguments_exception: Если передан неверный тип.
        """
        validator.validate(value, datetime, "period")
        self.__period = value
