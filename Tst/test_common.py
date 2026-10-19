import pytest

from Src.Core.common import common
from Src.Core.exception import arguments_exception
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import recipe_row_model


def test_valid_result_common_get_fields():
    """
    Проверяет получение списка свойств модели через get_fields.

    1. Передать в get_fields экземпляр group_model.

    <expected>В списке присутствуют свойства name и unique_code.</expected>
    """
    grp = group_model.create("Ингредиенты")
    fields = common.get_fields(grp)

    assert "name" in fields
    assert "unique_code" in fields


def test_valid_result_common_get_entity_header():
    """
    Проверяет формирование DTO заголовков для сущности через get_entity_header.

    1. Передать в get_entity_header экземпляр range_model.

    <expected>Возвращается непустой список DTO заголовков с полями name и conversion_factor.</expected>
    """
    unit = range_model.create_gram()
    headers = common.get_entity_header(unit)

    assert len(headers) > 0
    header_fields = [h.field for h in headers]
    assert "name" in header_fields
    assert "conversion_factor" in header_fields

    name_dto = next((h for h in headers if h.field == "name"), None)
    assert name_dto is not None
    assert name_dto.value == "грамм"


def test_valid_result_common_get_entity_table_aggregate():
    """
    Проверяет формирование DTO табличной части для агрегата (рецепта).

    1. Создать рецепт со строками состава.
    2. Вызвать get_entity_table(receipt).

    <expected>Возвращается непустой список строк таблицы, колонки содержат поля строк рецепта.</expected>
    """
    grp = group_model.create("Сырье")
    unit = range_model.create_gram()
    flour = nomenclature_model.create("Мука", "Мука в/с", grp, unit)
    row = recipe_row_model.create(flour, unit, 250.0, 240.0)
    recipe = receipt_model.create("Рецепт", flour, [row])

    table = common.get_entity_table(recipe)

    assert len(table) > 0
    assert len(table[0].columns) > 0
    assert "gross_weight" in table[0].columns
    assert "net_weight" in table[0].columns


def test_valid_result_common_get_entity_table_empty():
    """
    Проверяет, что для простой сущности без списков табличная часть пуста.

    1. Вызвать get_entity_table для group_model.

    <expected>len(table) == 0</expected>
    """
    grp = group_model.create("Сырье")
    table = common.get_entity_table(grp)

    assert len(table) == 0


def test_invalid_result_common_none_source():
    """
    Проверяет реакцию методов common на передачу None.

    1. Вызвать get_fields, get_entity_header, get_entity_table с аргументом None.

    <expected>arguments_exception</expected>
    """
    with pytest.raises(arguments_exception):
        common.get_fields(None)
    with pytest.raises(arguments_exception):
        common.get_entity_header(None)
    with pytest.raises(arguments_exception):
        common.get_entity_table(None)
