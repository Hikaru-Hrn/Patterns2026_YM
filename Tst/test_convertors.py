from datetime import date, datetime, time

import pytest

from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.exception import arguments_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import recipe_row_model


class datetime_sample:
    """Тестовый объект с одним DateTime-свойством."""

    __moment: datetime

    def __init__(self, moment: datetime) -> None:
        """Сохранить переданное значение даты и времени.

        :param moment: Значение даты и времени.
        """
        self.__moment = moment

    @property
    def moment(self) -> datetime:
        """Вернуть значение даты и времени."""
        return self.__moment


def _build_nomenclature() -> nomenclature_model:
    """Создать номенклатуру со ссылками на группу и единицу измерения."""
    group = group_model.create("Ингредиенты")
    unit = range_model.create_gram()
    return nomenclature_model.create(
        "Мука",
        "Мука пшеничная высший сорт",
        group,
        unit,
    )


def _build_composite_recipe() -> tuple:
    """Создать рецепт с вложенным полуфабрикатом.

    :return: Кортеж (готовый рецепт, рецепт полуфабриката, ингредиент).
    """
    group = group_model.create("Ингредиенты")
    unit = range_model.create_gram()

    flour = nomenclature_model.create(
        "Мука",
        "Мука пшеничная высший сорт",
        group,
        unit,
    )
    dough = nomenclature_model.create(
        "Песочное тесто",
        "Песочное тесто (полуфабрикат)",
        group,
        unit,
    )
    cookies = nomenclature_model.create(
        "Песочное печенье",
        "Песочное печенье в упаковке",
        group,
        unit,
    )

    dough_recipe = receipt_model.create(
        "Песочное тесто",
        dough,
        [recipe_row_model.create(flour, unit, 250.0, 240.0)],
    )
    recipe = receipt_model.create(
        "Песочное печенье",
        cookies,
        [recipe_row_model.create(dough_recipe, unit)],
    )

    return recipe, dough_recipe, flour


def test_invalid_result_abstract_covertor_cannot_instantiate():
    """
    Проверяет, что абстрактный конвертер нельзя создать напрямую.

    1. Попытаться создать экземпляр abstract_covertor.

    <expected>TypeError, так как Convert является абстрактным методом.</expected>
    """
    with pytest.raises(TypeError):
        abstract_covertor()


@pytest.mark.parametrize(
    "value,expected",
    [
        ("текст", "текст"),
        (42, 42),
        (3.14, 3.14),
        (True, True),
    ],
)
def test_valid_result_basic_convertor_scalar(value, expected):
    """
    Проверяет конвертацию простых скалярных значений.

    1. Передать строку, число и bool в basic_convertor.Convert().

    <expected>Словарь {"value": исходное значение}.</expected>
    """
    result = basic_convertor().Convert(value)

    assert result == {"value": expected}


def test_valid_result_basic_convertor_model():
    """
    Проверяет конвертацию простых полей доменной модели.

    1. Создать group_model.
    2. Вызвать basic_convertor.Convert(group).

    <expected>Словарь содержит unique_code и name, но не содержит ссылок.</expected>
    """
    group = group_model.create("Ингредиенты")

    result = basic_convertor().Convert(group)

    assert result["unique_code"] == group.unique_code
    assert result["name"] == "Ингредиенты"
    assert set(result.keys()) == {"unique_code", "name"}


def test_valid_result_basic_convertor_enum():
    """
    Проверяет конвертацию перечисления как простого типа.

    1. Передать report_type_enum.CSV в basic_convertor.Convert().

    <expected>Словарь {"value": "CSV"}.</expected>
    """
    result = basic_convertor().Convert(report_type_enum.CSV)

    assert result == {"value": "CSV"}


def test_invalid_result_basic_convertor_none():
    """
    Проверяет реакцию basic_convertor на None.

    1. Вызвать Convert(None).

    <expected>arguments_exception.</expected>
    """
    with pytest.raises(arguments_exception):
        basic_convertor().Convert(None)


@pytest.mark.parametrize(
    "value,expected",
    [
        (datetime(2026, 10, 24, 19, 7, 0), "2026-10-24T19:07:00"),
        (date(2026, 10, 24), "2026-10-24"),
        (time(19, 7, 0), "19:07:00"),
    ],
)
def test_valid_result_datetime_convertor_scalar(value, expected):
    """
    Проверяет конвертацию DateTime-значений в ISO 8601.

    1. Передать datetime, date и time в datetime_convertor.Convert().

    <expected>Словарь {"value": ISO-строка}.</expected>
    """
    result = datetime_convertor().Convert(value)

    assert result == {"value": expected}


def test_valid_result_datetime_convertor_model():
    """
    Проверяет конвертацию DateTime-поля объекта.

    1. Создать объект с DateTime-свойством moment.
    2. Вызвать datetime_convertor.Convert(object).

    <expected>Словарь {"moment": ISO-строка}.</expected>
    """
    moment = datetime(2026, 10, 24, 19, 7, 0)
    source = datetime_sample(moment)

    result = datetime_convertor().Convert(source)

    assert result == {"moment": "2026-10-24T19:07:00"}


def test_invalid_result_datetime_convertor_none():
    """
    Проверяет реакцию datetime_convertor на None.

    1. Вызвать Convert(None).

    <expected>arguments_exception.</expected>
    """
    with pytest.raises(arguments_exception):
        datetime_convertor().Convert(None)


def test_valid_result_reference_convertor_nomenclature_without_factory():
    """
    Проверяет краткое описание ссылки без переданной фабрики.

    1. Создать номенклатуру с группой и единицей измерения.
    2. Вызвать reference_convertor.Convert(nomenclature) без фабрики.

    <expected>Возвращается дескриптор с unique_code и name.</expected>
    """
    nomenclature = _build_nomenclature()

    result = reference_convertor().Convert(nomenclature)

    assert result == {
        "unique_code": nomenclature.unique_code,
        "name": nomenclature.name,
    }


def test_valid_result_reference_convertor_nomenclature_with_factory():
    """
    Проверяет полное раскрытие ссылок через абстрактную фабрику.

    1. Создать номенклатуру с группой и единицей измерения.
    2. Получить reference_convertor у convert_factory.
    3. Вызвать Convert(nomenclature).

    <expected>group и range раскрыты вложенными словарями.</expected>
    """
    nomenclature = _build_nomenclature()
    factory = convert_factory()

    result = factory.reference.Convert(nomenclature)

    assert result["name"] == "Мука"
    assert result["group"]["name"] == "Ингредиенты"
    assert result["range"]["name"] == "грамм"
    assert result["range"]["conversion_factor"] == 1.0


def test_valid_result_reference_convertor_composite_recipe():
    """
    Проверяет раскрытие ссылок в составном рецепте через фабрику.

    1. Создать рецепт с вложенным полуфабрикатом.
    2. Получить reference_convertor у convert_factory.
    3. Вызвать Convert(recipe).

    <expected>Вложенный sub_recipe содержит строки состава и ингредиенты.</expected>
    """
    recipe, dough_recipe, flour = _build_composite_recipe()
    factory = convert_factory()

    result = factory.reference.Convert(recipe)

    assert result["dish"]["name"] == "Песочное печенье"
    assert result["rows"][0]["sub_recipe"]["name"] == dough_recipe.name
    assert (
        result["rows"][0]["sub_recipe"]["rows"][0]["nomenclature"]["name"]
        == flour.name
    )


def test_invalid_result_reference_convertor_none():
    """
    Проверяет реакцию reference_convertor на None.

    1. Вызвать Convert(None).

    <expected>arguments_exception.</expected>
    """
    with pytest.raises(arguments_exception):
        reference_convertor().Convert(None)


def test_invalid_result_reference_convertor_scalar():
    """
    Проверяет реакцию reference_convertor на неподдерживаемый скаляр.

    1. Передать строку в reference_convertor.Convert().

    <expected>arguments_exception.</expected>
    """
    with pytest.raises(arguments_exception):
        reference_convertor().Convert("текст")
