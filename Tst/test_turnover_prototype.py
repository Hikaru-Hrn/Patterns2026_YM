import pytest

from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.turnover_prototype import turnover_prototype


@pytest.fixture(autouse=True)
def reset_storage():
    """Сбрасывает singleton-хранилище перед каждым тестом ОСВ."""
    sm = storage_manager()
    sm._groups = []
    sm._ranges = []
    sm._nomenclatures = []
    sm._warehouses = []
    sm._recipes = []
    sm._transactions = []
    sm._is_loaded = False
    sm._data = {}
    sm._invalidate_filter_index()

    mgr = settings_manager()
    if not mgr.is_loaded:
        mgr.load("Tst/settings.json")
    mgr.settings.first_launch_flag = True
    sm.first_start("Tst/settings.json")
    yield


def test_valid_result_turnover_prototype_build_statements():
    """
    Проверяет формирование строк ОСВ по всем транзакциям.

    1. Создать turnover_prototype для всех транзакций.
    2. Вызвать build_statements.

    <expected>Сформировано по одной строке ОСВ для каждой пары склад-номенклатура.</expected>
    """
    transactions = storage_manager().transactions
    prototype = turnover_prototype(transactions)

    statements = prototype.build_statements()

    assert len(statements) == 3


def test_valid_result_turnover_prototype_calculations():
    """
    Проверяет корректность расчета прихода, расхода и остатков ОСВ.

    1. Отфильтровать транзакции по номенклатуре 'Мука пшеничная'.
    2. Построить ОСВ.

    <expected>Приход = 1000, расход = 200, конечный остаток = 800.</expected>
    """
    transactions = storage_manager().transactions
    dto = filter_dto.create(filter_item_dto.create("nomenclature.name", "Мука пшеничная"))
    prototype = turnover_prototype(transactions).clone(dto)

    statements = prototype.build_statements()

    assert len(statements) == 1
    statement = statements[0]
    assert statement.income == 1000.0
    assert statement.expense == 200.0
    assert statement.closing_balance == 800.0


def test_valid_result_turnover_prototype_filter_by_warehouse():
    """
    Проверяет формирование ОСВ с фильтрацией по складу.

    1. Создать filter_dto с условием warehouse.name EQUALS 'Кухня/Производство'.
    2. Применить фильтр через turnover_prototype.

    <expected>В результирующей ОСВ только строки по указанному складу.</expected>
    """
    transactions = storage_manager().transactions
    dto = filter_dto.create(filter_item_dto.create("warehouse.name", "Кухня/Производство"))
    prototype = turnover_prototype(transactions).clone(dto)

    statements = prototype.build_statements()

    assert len(statements) == 1
    assert statements[0].warehouse.name == "Кухня/Производство"


def test_valid_result_turnover_prototype_empty_result():
    """
    Проверяет формирование ОСВ при отсутствии подходящих транзакций.

    1. Создать filter_dto с несуществующей номенклатурой.
    2. Применить фильтр через turnover_prototype.

    <expected>Список строк ОСВ пуст.</expected>
    """
    transactions = storage_manager().transactions
    dto = filter_dto.create(filter_item_dto.create("nomenclature.name", "несуществующая"))
    prototype = turnover_prototype(transactions).clone(dto)

    statements = prototype.build_statements()

    assert len(statements) == 0
