import pytest

from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.filter_prototype import filter_prototype
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.transaction_model import transaction_model


@pytest.fixture(autouse=True)
def reset_storage():
    """Сбрасывает singleton-хранилище перед каждым тестом фильтрации."""
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


def test_valid_result_filter_prototype_equals_by_name():
    """
    Проверяет фильтрацию EQUALS по наименованию номенклатуры.

    1. Создать filter_dto с условием name EQUALS 'Мука пшеничная'.
    2. Применить прототип к коллекции номенклатуры.

    <expected>Результат содержит ровно одну номенклатуру с указанным именем.</expected>
    """
    items = storage_manager().nomenclatures
    dto = filter_dto.create(filter_item_dto.create("name", "Мука пшеничная"))
    prototype = filter_prototype(items, "nomenclatures")

    result = prototype.clone(dto).data

    assert len(result) == 1
    assert result[0].name == "Мука пшеничная"


def test_valid_result_filter_prototype_like_by_name():
    """
    Проверяет фильтрацию LIKE по наименованию номенклатуры.

    1. Создать filter_dto с условием name LIKE 'Песочное'.
    2. Применить прототип к коллекции номенклатуры.

    <expected>Результат содержит номенклатуры, в имени которых есть подстрока 'Песочное'.</expected>
    """
    items = storage_manager().nomenclatures
    dto = filter_dto.create(
        filter_item_dto.create("name", "Песочное", filter_type_enum.LIKE)
    )
    prototype = filter_prototype(items, "nomenclatures")

    result = prototype.clone(dto).data

    assert len(result) == 2
    names = {item.name for item in result}
    assert "Песочное тесто" in names
    assert "Песочное печенье" in names


def test_valid_result_filter_prototype_by_unique_code():
    """
    Проверяет фильтрацию EQUALS по уникальному коду.

    1. Получить unique_code первой группы.
    2. Создать filter_dto с условием unique_code EQUALS.

    <expected>Результат содержит ровно одну группу с указанным кодом.</expected>
    """
    items = storage_manager().groups
    target = items[0]
    dto = filter_dto.create(filter_item_dto.create("unique_code", target.unique_code))
    prototype = filter_prototype(items, "groups")

    result = prototype.clone(dto).data

    assert len(result) == 1
    assert result[0].unique_code == target.unique_code


def test_valid_result_filter_prototype_by_nested_group_name():
    """
    Проверяет фильтрацию номенклатуры по наименованию группы.

    1. Создать filter_dto с условием group.name EQUALS 'Ингредиенты'.
    2. Применить прототип к номенклатуре.

    <expected>Результат содержит только номенклатуру группы 'Ингредиенты'.</expected>
    """
    items = storage_manager().nomenclatures
    dto = filter_dto.create(filter_item_dto.create("group.name", "Ингредиенты"))
    prototype = filter_prototype(items, "nomenclatures")

    result = prototype.clone(dto).data

    assert len(result) > 0
    assert all(item.group.name == "Ингредиенты" for item in result)


def test_valid_result_filter_prototype_by_nested_range_base_name():
    """
    Проверяет фильтрацию единиц измерения по базовой единице.

    1. Создать filter_dto с условием base.name EQUALS 'грамм'.
    2. Применить прототип к единицам измерения.

    <expected>Результат содержит единицы измерения, у которых базовая единица 'грамм'.</expected>
    """
    items = storage_manager().ranges
    dto = filter_dto.create(filter_item_dto.create("base.name", "грамм"))
    prototype = filter_prototype(items, "ranges")

    result = prototype.clone(dto).data

    assert len(result) == 1
    assert result[0].name == "килограмм"


def test_valid_result_filter_prototype_multiple_conditions():
    """
    Проверяет совместное применение нескольких условий фильтрации.

    1. Создать filter_dto с условиями group.name 'Ингредиенты' и name LIKE 'а'.
    2. Применить прототип к номенклатуре.

    <expected>Результат удовлетворяет обоим условиям одновременно.</expected>
    """
    items = storage_manager().nomenclatures
    dto = filter_dto.create(
        filter_item_dto.create("group.name", "Ингредиенты"),
        filter_item_dto.create("name", "а", filter_type_enum.LIKE),
    )
    prototype = filter_prototype(items, "nomenclatures")

    result = prototype.clone(dto).data

    assert len(result) > 0
    assert all(item.group.name == "Ингредиенты" for item in result)
    assert all("а" in item.name.lower() for item in result)


def test_valid_result_filter_prototype_no_matches():
    """
    Проверяет фильтрацию, при которой ничего не найдено.

    1. Создать filter_dto с условием name EQUALS 'несуществующее_имя'.
    2. Применить прототип к номенклатуре.

    <expected>Результат пустой.</expected>
    """
    items = storage_manager().nomenclatures
    dto = filter_dto.create(filter_item_dto.create("name", "несуществующее_имя"))
    prototype = filter_prototype(items, "nomenclatures")

    result = prototype.clone(dto).data

    assert len(result) == 0


def test_valid_result_filter_prototype_empty_filter():
    """
    Проверяет, что пустой фильтр возвращает все данные.

    1. Создать пустой filter_dto.
    2. Применить прототип к номенклатуре.

    <expected>Результат совпадает с исходной коллекцией.</expected>
    """
    items = storage_manager().nomenclatures
    dto = filter_dto()
    prototype = filter_prototype(items, "nomenclatures")

    result = prototype.clone(dto).data

    assert len(result) == len(items)


def test_valid_result_filter_prototype_transaction_by_nomenclature_name():
    """
    Проверяет фильтрацию транзакций по наименованию номенклатуры.

    1. Создать filter_dto с условием nomenclature.name EQUALS 'Мука пшеничная'.
    2. Применить прототип к транзакциям.

    <expected>Результат содержит транзакции только по указанной номенклатуре.</expected>
    """
    items = storage_manager().transactions
    dto = filter_dto.create(filter_item_dto.create("nomenclature.name", "Мука пшеничная"))
    prototype = filter_prototype(items, "transactions")

    result = prototype.clone(dto).data

    assert len(result) == 2
    assert all(isinstance(item, transaction_model) for item in result)
    assert all(item.nomenclature.name == "Мука пшеничная" for item in result)
