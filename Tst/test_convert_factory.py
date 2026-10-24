import json
from datetime import datetime
from pathlib import Path

import pytest

from Src.Core.abstract_model import abstract_model
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


class linked_node(abstract_model):
    """Тестовая модель со ссылкой на другой узел (для проверки циклов)."""

    __name: str
    __child = None

    def __init__(self, name: str) -> None:
        """Создать узел с наименованием.

        :param name: Наименование узла.
        """
        super().__init__()
        self.__name = name

    @property
    def name(self) -> str:
        """Вернуть наименование узла."""
        return self.__name

    @property
    def child(self):
        """Вернуть ссылку на дочерний узел."""
        return self.__child

    @child.setter
    def child(self, value) -> None:
        """Установить ссылку на дочерний узел.

        :param value: Экземпляр linked_node или None.
        """
        self.__child = value


class datetime_sample:
    """Тестовый объект с DateTime-свойством."""

    __moment: datetime

    def __init__(self, moment: datetime) -> None:
        """Сохранить значение даты и времени.

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


def test_valid_result_convert_factory_create_selects_converters():
    """
    Проверяет выбор конвертера по типу значения.

    1. Вызвать create() для числа, datetime и доменной модели.

    <expected>Возвращаются basic_convertor, datetime_convertor и reference_convertor.</expected>
    """
    factory = convert_factory()

    assert isinstance(factory.create(42), basic_convertor)
    assert isinstance(factory.create(datetime(2026, 10, 24)), datetime_convertor)
    assert isinstance(factory.create(group_model.create("Группа")), reference_convertor)


def test_invalid_result_convert_factory_unknown_type():
    """
    Проверяет реакцию create() на объект без поддерживаемых свойств.

    1. Передать object() в create().

    <expected>arguments_exception.</expected>
    """
    factory = convert_factory()

    with pytest.raises(arguments_exception):
        factory.create(object())


def test_valid_result_convert_factory_scalar():
    """
    Проверяет конвертацию простого значения через фабрику.

    1. Передать число 42 в Convert().

    <expected>Возвращается исходное число.</expected>
    """
    result = convert_factory().Convert(42)

    assert result == 42


def test_valid_result_convert_factory_enum():
    """
    Проверяет конвертацию перечисления через фабрику.

    1. Передать report_type_enum.CSV в Convert().

    <expected>Возвращается строка "CSV".</expected>
    """
    result = convert_factory().Convert(report_type_enum.CSV)

    assert result == "CSV"


def test_valid_result_convert_factory_simple_model():
    """
    Проверяет конвертацию простой доменной модели.

    1. Создать group_model.
    2. Вызвать convert_factory.Convert(group).

    <expected>Словарь содержит unique_code и name.</expected>
    """
    group = group_model.create("Ингредиенты")

    result = convert_factory().Convert(group)

    assert result["unique_code"] == group.unique_code
    assert result["name"] == "Ингредиенты"


def test_valid_result_convert_factory_composite_model():
    """
    Проверяет вложенное раскрытие ссылок составной модели.

    1. Создать номенклатуру с группой и единицей измерения.
    2. Вызвать convert_factory.Convert(nomenclature).

    <expected>group и range являются вложенными словарями с полями.</expected>
    """
    nomenclature = _build_nomenclature()

    result = convert_factory().Convert(nomenclature)

    assert result["group"]["name"] == "Ингредиенты"
    assert result["range"]["name"] == "грамм"
    assert result["range"]["base"] is None


def test_valid_result_convert_factory_aggregate():
    """
    Проверяет конвертацию агрегата со списком строк.

    1. Создать рецепт с вложенным полуфабрикатом.
    2. Вызвать convert_factory.Convert(recipe).

    <expected>rows — список словарей, sub_recipe раскрыт вложенно.</expected>
    """
    recipe, dough_recipe, flour = _build_composite_recipe()

    result = convert_factory().Convert(recipe)

    assert result["name"] == "Песочное печенье"
    assert result["dish"]["name"] == "Песочное печенье"
    assert len(result["rows"]) == 1
    assert result["rows"][0]["sub_recipe"]["name"] == dough_recipe.name
    assert (
        result["rows"][0]["sub_recipe"]["rows"][0]["nomenclature"]["name"]
        == flour.name
    )


def test_valid_result_convert_factory_repeated_reference():
    """
    Проверяет замену повторной ссылки дескриптором.

    1. Передать список из двух одинаковых номенклатур.
    2. Вызвать convert_factory.Convert(list).

    <expected>Первый элемент раскрыт полностью, второй — {"unique_code", "name"}.</expected>
    """
    nomenclature = _build_nomenclature()

    result = convert_factory().Convert([nomenclature, nomenclature])

    assert result[0]["group"]["name"] == "Ингредиенты"
    assert result[1] == {
        "unique_code": nomenclature.unique_code,
        "name": nomenclature.name,
    }


def test_valid_result_convert_factory_cycle():
    """
    Проверяет защиту от циклических ссылок.

    1. Создать два узла, ссылающихся друг на друга.
    2. Вызвать convert_factory.Convert(первый узел).

    <expected>Обход завершается, повторная ссылка заменена дескриптором.</expected>
    """
    first = linked_node("Первый")
    second = linked_node("Второй")
    first.child = second
    second.child = first

    result = convert_factory().Convert(first)

    assert result["name"] == "Первый"
    assert result["child"]["name"] == "Второй"
    assert result["child"]["child"] == {
        "unique_code": first.unique_code,
        "name": "Первый",
    }


def test_valid_result_convert_factory_datetime():
    """
    Проверяет конвертацию DateTime-поля через фабрику.

    1. Создать объект с DateTime-свойством.
    2. Вызвать convert_factory.Convert(object).

    <expected>Значение поля представлено ISO-строкой.</expected>
    """
    source = datetime_sample(datetime(2026, 10, 24, 19, 7, 0))

    result = convert_factory().Convert(source)

    assert result == {"moment": "2026-10-24T19:07:00"}


def test_valid_result_convert_factory_json_serializable():
    """
    Проверяет, что результат фабрики можно сериализовать в JSON.

    1. Создать составной рецепт.
    2. Преобразовать его через фабрику.
    3. Выполнить json.dumps() и json.loads().

    <expected>Результат сериализуется без дополнительных encoder.</expected>
    """
    recipe, _, _ = _build_composite_recipe()

    payload = convert_factory().Convert(recipe)
    text = json.dumps(payload, ensure_ascii=False)
    restored = json.loads(text)

    assert restored["name"] == recipe.name
    assert isinstance(restored["rows"], list)


def test_invalid_result_convert_factory_none():
    """
    Проверяет реакцию фабрики на None.

    1. Вызвать Convert(None).

    <expected>arguments_exception.</expected>
    """
    with pytest.raises(arguments_exception):
        convert_factory().Convert(None)


_JSON_DIR = Path(__file__).resolve().parent.parent / "_docs" / "json"


@pytest.mark.parametrize(
    "file_name,expected_keys",
    [
        ("basic_convertor.json", ("unique_code", "name")),
        ("datetime_convertor.json", ("value",)),
        ("reference_convertor.json", ("unique_code", "name", "group", "range")),
        ("convert_factory_receipt.json", ("unique_code", "name", "dish", "rows")),
    ],
)
def test_valid_result_json_examples(file_name, expected_keys):
    """
    Проверяет корректность JSON-примеров, приложенных к заданию.

    1. Прочитать JSON-файл из _docs/json.
    2. Проверить наличие ожидаемых ключей.

    <expected>Файл существует, читается и содержит ожидаемую структуру.</expected>
    """
    path = _JSON_DIR / file_name

    assert path.exists(), f"Не найден JSON-пример: {path}"

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert isinstance(data, dict)
    for key in expected_keys:
        assert key in data
