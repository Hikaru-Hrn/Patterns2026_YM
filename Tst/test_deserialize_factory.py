import json
from pathlib import Path

import pytest

from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import recipe_row_model
from Src.Models.warehouse_model import warehouse_model

_JSON_PATH = Path(__file__).resolve().parent.parent / "_docs" / "json" / "storage_manager.json"


@pytest.fixture(autouse=True)
def reset_storage():
    """Сбрасывает singleton-хранилище перед каждым тестом."""
    sm = storage_manager()
    sm._groups = []
    sm._ranges = []
    sm._nomenclatures = []
    sm._warehouses = []
    sm._recipes = []
    sm._is_loaded = False
    sm._data = {}
    yield


def _build_storage() -> storage_manager:
    """Сформировать эталонные данные через storage_manager."""
    sm = storage_manager()
    assert sm.convert() is True
    return sm


def _serialized_storage(sm: storage_manager) -> dict:
    """Сериализовать коллекции storage_manager через convert_factory."""
    factory = convert_factory()
    return {
        "warehouses": factory.Convert(sm.warehouses),
        "ranges": factory.Convert(sm.ranges),
        "groups": factory.Convert(sm.groups),
        "nomenclatures": factory.Convert(sm.nomenclatures),
        "recipes": factory.Convert(sm.recipes),
    }


def _load_json() -> dict:
    """Прочитать и десериализовать JSON с исходными данными."""
    with open(_JSON_PATH, "r", encoding="utf-8") as file:
        return deserialize_factory().Convert(json.load(file))


def _row_signature(row: recipe_row_model) -> tuple:
    """Построить независимую от unique_code подпись строки рецепта."""
    sub_recipe = row.sub_recipe
    return (
        row.nomenclature.name if row.nomenclature else None,
        row.range.name if row.range else None,
        row.gross_weight,
        row.net_weight,
        sub_recipe.name if sub_recipe else None,
        tuple(_row_signature(item) for item in sub_recipe.rows) if sub_recipe else (),
    )


def _recipe_signature(recipe: receipt_model) -> tuple:
    """Построить независимую от unique_code подпись рецепта."""
    return (
        recipe.name,
        recipe.comments,
        recipe.gross_weight,
        recipe.net_weight,
        tuple(_row_signature(row) for row in recipe.rows),
    )


def test_invalid_result_abstract_deserialize_factory_cannot_instantiate():
    """
    Проверяет, что абстрактную фабрику нельзя создать напрямую.

    1. Попытаться создать экземпляр abstract_deserialize_factory.

    <expected>TypeError, так как методы фабрики абстрактные.</expected>
    """
    with pytest.raises(TypeError):
        abstract_deserialize_factory()


@pytest.mark.parametrize(
    "payload,expected_type",
    [
        ({"name": "Ингредиенты"}, group_model),
        ({"name": "грамм", "base": None, "conversion_factor": 1.0}, range_model),
        ({"name": "Мука", "full_name": "Мука пшеничная в/с"}, nomenclature_model),
        ({"name": "Основной склад", "address": "ул. Ленина, 1"}, warehouse_model),
        ({"name": "Песочное тесто", "dish": {}, "rows": []}, receipt_model),
        (
            {"nomenclature": {}, "sub_recipe": None, "range": {}, "gross_weight": 0.0},
            recipe_row_model,
        ),
    ],
)
def test_valid_result_deserialize_factory_create(payload, expected_type):
    """
    Проверяет фабричный выбор модели по структуре JSON.

    1. Передать словарь каждого типа модели в create().

    <expected>Возвращается экземпляр ожидаемого класса.</expected>
    """
    assert isinstance(deserialize_factory().create(payload), expected_type)


def test_invalid_result_deserialize_factory_unknown_json():
    """
    Проверяет реакцию фабрики на неизвестную структуру JSON.

    1. Передать {"unknown": 1} в Convert().

    <expected>arguments_exception.</expected>
    """
    with pytest.raises(arguments_exception):
        deserialize_factory().Convert({"unknown": 1})


def test_invalid_result_deserialize_factory_none():
    """
    Проверяет реакцию фабрики на None.

    1. Вызвать Convert(None).

    <expected>arguments_exception.</expected>
    """
    with pytest.raises(arguments_exception):
        deserialize_factory().Convert(None)


def test_valid_result_deserialize_factory_roundtrip_models():
    """
    Проверяет полный цикл сериализации и десериализации моделей storage_manager.

    1. Сформировать данные через storage_manager.convert().
    2. Сериализовать их через convert_factory, прогнать через JSON.
    3. Восстановить через deserialize_factory.
    4. Сравнить unique_code и типы всех коллекций.

    <expected>Коллекции совпадают по коду, количеству и типам моделей.</expected>
    """
    sm = _build_storage()
    payload = json.loads(json.dumps(_serialized_storage(sm), ensure_ascii=False))

    restored = deserialize_factory().Convert(payload)

    assert isinstance(restored["warehouses"][0], warehouse_model)
    assert isinstance(restored["ranges"][0], range_model)
    assert isinstance(restored["groups"][0], group_model)
    assert isinstance(restored["nomenclatures"][0], nomenclature_model)
    assert isinstance(restored["recipes"][0], receipt_model)

    for key in ("warehouses", "ranges", "groups", "nomenclatures", "recipes"):
        assert [item.unique_code for item in restored[key]] == [
            item.unique_code for item in getattr(sm, key)
        ]


def test_valid_result_deserialize_factory_roundtrip_relations():
    """
    Проверяет восстановление связей и вложенных рецептов после round-trip.

    1. Сериализовать и восстановить данные storage_manager.
    2. Проверить ссылки группа/единица у номенклатуры.
    3. Проверить базовую единицу у килограмма.
    4. Проверить принцип 'блюдо в блюде' и веса рецепта.

    <expected>Ссылки указывают на один объект, веса совпадают с исходными.</expected>
    """
    sm = _build_storage()
    payload = json.loads(json.dumps(_serialized_storage(sm), ensure_ascii=False))
    restored = deserialize_factory().Convert(payload)

    flour = next(item for item in restored["nomenclatures"] if item.name == "Мука пшеничная")
    gram = next(item for item in restored["ranges"] if item.name == "грамм")
    kilogram = next(item for item in restored["ranges"] if item.name == "килограмм")

    assert isinstance(flour.group, group_model)
    assert flour.group.name == "Ингредиенты"
    assert flour.range is gram
    assert kilogram.base is gram

    dough = next(item for item in restored["recipes"] if item.name == "Песочное тесто")
    cookie = next(
        item for item in restored["recipes"] if item.name == "Песочное печенье в упаковке"
    )
    sub_recipe_row = next(row for row in cookie.rows if row.sub_recipe is not None)

    assert sub_recipe_row.sub_recipe is dough
    assert cookie.gross_weight == 600.0
    assert cookie.net_weight == 590.0


def test_valid_result_deserialize_factory_json_all_collections():
    """
    Проверяет восстановление всех коллекций из приложенного JSON-файла.

    1. Прочитать _docs/json/storage_manager.json и десериализовать.

    <expected>Восстановлены 2 склада, 4 единицы, 4 группы, 7 позиций и 2 рецепта.</expected>
    """
    restored = _load_json()

    assert len(restored["warehouses"]) == 2
    assert len(restored["ranges"]) == 4
    assert len(restored["groups"]) == 4
    assert len(restored["nomenclatures"]) == 7
    assert len(restored["recipes"]) == 2


def test_valid_result_deserialize_factory_json_matches_storage_manager():
    """
    Проверяет, что загруженный JSON совпадает с моделями storage_manager.

    1. Восстановить модели из JSON-файла.
    2. Сформировать эталонные модели через storage_manager.convert().
    3. Сравнить скалярные поля и связи без уникальных кодов.

    <expected>Все справочники и рецепты совпадают по данным и весам.</expected>
    """
    loaded = _load_json()
    sm = _build_storage()

    assert sorted((item.name, item.address) for item in loaded["warehouses"]) == sorted(
        (item.name, item.address) for item in sm.warehouses
    )

    assert sorted(
        (item.name, item.conversion_factor, item.base.name if item.base else None)
        for item in loaded["ranges"]
    ) == sorted(
        (item.name, item.conversion_factor, item.base.name if item.base else None)
        for item in sm.ranges
    )

    assert sorted(item.name for item in loaded["groups"]) == sorted(
        item.name for item in sm.groups
    )

    assert sorted(
        (
            item.name,
            item.full_name,
            item.group.name if item.group else None,
            item.range.name if item.range else None,
        )
        for item in loaded["nomenclatures"]
    ) == sorted(
        (
            item.name,
            item.full_name,
            item.group.name if item.group else None,
            item.range.name if item.range else None,
        )
        for item in sm.nomenclatures
    )

    assert {item.name: _recipe_signature(item) for item in loaded["recipes"]} == {
        item.name: _recipe_signature(item) for item in sm.recipes
    }


def test_valid_result_deserialize_factory_json_shared_references():
    """
    Проверяет, что повторные ссылки в JSON восстанавливаются как один объект.

    1. Загрузить JSON-файл.
    2. Проверить уникальность объектов единиц измерения, групп и рецептов.

    <expected>Ссылки указывают на тот же экземпляр, а не на копию.</expected>
    """
    restored = _load_json()

    gram = next(item for item in restored["ranges"] if item.name == "грамм")
    kilogram = next(item for item in restored["ranges"] if item.name == "килограмм")
    flour = next(item for item in restored["nomenclatures"] if item.name == "Мука пшеничная")
    ingredients = next(item for item in restored["groups"] if item.name == "Ингредиенты")
    dough = next(item for item in restored["recipes"] if item.name == "Песочное тесто")
    cookie = next(
        item for item in restored["recipes"] if item.name == "Песочное печенье в упаковке"
    )
    sub_recipe_row = next(row for row in cookie.rows if row.sub_recipe is not None)

    assert kilogram.base is gram
    assert flour.range is gram
    assert flour.group is ingredients
    assert sub_recipe_row.sub_recipe is dough
