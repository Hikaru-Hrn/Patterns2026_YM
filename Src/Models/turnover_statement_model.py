from Src.Core.abstract_model import abstract_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.warehouse_model import warehouse_model


class turnover_statement_model(abstract_model):
    """Модель строки оборотно-сальдовой ведомости.

    Содержит информацию об остатках и оборотах номенклатуры
    в разрезе склада: начальный остаток, приход, расход, конечный остаток.
    """

    __warehouse: warehouse_model = None
    __nomenclature: nomenclature_model = None
    __opening_balance: float = 0.0
    __income: float = 0.0
    __expense: float = 0.0
    __closing_balance: float = 0.0

    def __init__(self) -> None:
        """Инициализирует пустую строку ОСВ."""
        super().__init__()

    @staticmethod
    def create(
        warehouse: warehouse_model,
        nomenclature: nomenclature_model,
        opening_balance: float = 0.0,
        income: float = 0.0,
        expense: float = 0.0,
    ) -> "turnover_statement_model":
        """Фабричный метод создания строки ОСВ.

        :param warehouse: Склад.
        :param nomenclature: Номенклатура.
        :param opening_balance: Начальный остаток.
        :param income: Приход.
        :param expense: Расход.
        :return: Заполненный экземпляр turnover_statement_model.
        """
        statement = turnover_statement_model()
        statement.warehouse = warehouse
        statement.nomenclature = nomenclature
        statement.opening_balance = opening_balance
        statement.income = income
        statement.expense = expense
        return statement

    @property
    def warehouse(self) -> warehouse_model:
        """Возвращает склад строки ОСВ."""
        return self.__warehouse

    @warehouse.setter
    def warehouse(self, value: warehouse_model) -> None:
        """Устанавливает склад строки ОСВ."""
        self.__warehouse = value

    @property
    def nomenclature(self) -> nomenclature_model:
        """Возвращает номенклатуру строки ОСВ."""
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        """Устанавливает номенклатуру строки ОСВ."""
        self.__nomenclature = value

    @property
    def opening_balance(self) -> float:
        """Возвращает начальный остаток."""
        return self.__opening_balance

    @opening_balance.setter
    def opening_balance(self, value: float) -> None:
        """Устанавливает начальный остаток."""
        self.__opening_balance = float(value)

    @property
    def income(self) -> float:
        """Возвращает приход за период."""
        return self.__income

    @income.setter
    def income(self, value: float) -> None:
        """Устанавливает приход за период."""
        self.__income = float(value)

    @property
    def expense(self) -> float:
        """Возвращает расход за период."""
        return self.__expense

    @expense.setter
    def expense(self, value: float) -> None:
        """Устанавливает расход за период."""
        self.__expense = float(value)

    @property
    def closing_balance(self) -> float:
        """Возвращает конечный остаток (начальный + приход - расход)."""
        return self.__closing_balance

    def recalculate_closing_balance(self) -> None:
        """Пересчитывает конечный остаток на основе остальных полей."""
        self.__closing_balance = self.__opening_balance + self.__income - self.__expense
