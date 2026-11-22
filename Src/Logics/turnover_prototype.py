from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.filter_prototype import filter_prototype
from Src.Models.transaction_model import transaction_model
from Src.Models.turnover_statement_model import turnover_statement_model


class turnover_prototype(abstract_prototype):
    """Прототип формирования оборотно-сальдовой ведомости.

    Фильтрует транзакции через filter_prototype и группирует их
    по складу и номенклатуре с расчетом прихода, расхода и остатков.
    """

    __transactions: list = []

    def __init__(self, transactions: list[transaction_model]) -> None:
        """Инициализирует прототип ОСВ.

        :param transactions: Список транзакций для анализа.
        """
        self.__transactions = list(transactions) if transactions is not None else []

    @property
    def transactions(self) -> list[transaction_model]:
        """Возвращает текущий список транзакций."""
        return list(self.__transactions)

    def clone(self, filter_dto: filter_dto) -> "turnover_prototype":
        """Создает отфильтрованную копию прототипа.

        :param filter_dto: Условия фильтрации транзакций.
        :return: Новый экземпляр turnover_prototype с отфильтрованными данными.
        """
        if filter_dto is None:
            raise arguments_exception("filter_dto", "Фильтр не может быть None")

        filtered = self.__transactions
        if len(filter_dto.filters) > 0:
            prototype = filter_prototype(self.__transactions, "transactions")
            filtered = prototype.clone(filter_dto).data

        return turnover_prototype(filtered)

    def build_statements(self) -> list[turnover_statement_model]:
        """Формирует строки ОСВ по отфильтрованным транзакциям.

        Группирует транзакции по складу и номенклатуре, рассчитывает
        приход, расход и конечный остаток.

        :return: Список turnover_statement_model.
        """
        groups: dict[tuple, turnover_statement_model] = {}

        for transaction in self.__transactions:
            if not isinstance(transaction, transaction_model):
                continue

            key = (id(transaction.warehouse), id(transaction.nomenclature))
            if key not in groups:
                groups[key] = turnover_statement_model.create(
                    warehouse=transaction.warehouse,
                    nomenclature=transaction.nomenclature,
                )

            statement = groups[key]
            value = transaction.value
            if value > 0:
                statement.income += value
            else:
                statement.expense += abs(value)

        result = []
        for statement in groups.values():
            statement.recalculate_closing_balance()
            result.append(statement)

        return result
