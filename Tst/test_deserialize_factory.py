import json
from pathlib import Path

import pytest

from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import recipe_row_model
from Src.Models.settings_model import settings_model
from Src.Models.warehouse_model import warehouse_model
from Src.Dtos.report_type_enum import report_type_enum

_JSON_PATH = Path(__file__).resolve().parent.parent / "_docs" / "json" / "storage_manager.json"
_RECEIPT_JSON_PATH = Path(__file__).resolve().parent.parent / "_docs" / "json" / "convert_factory_receipt.json"


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
        key: factory.Convert(getattr(sm, key))
        for key in sm.collection_models
    }


def _load_json() -> dict:
    """Прочитать и десериализовать JSON с исходными данными по контейнеру storage_manager."""
    with open(_JSON_PATH, "r", encoding="utf-8") as file:
        return deserialize_factory().Convert(json.load(file), storage_manager)


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
    "model_type",
    [
        group_model,
        range_model,
        nomenclature_model,
        warehouse_model,
        receipt_model,
        recipe_row_model,
        organization_model,
        settings_model,
    ],
)
def test_valid_result_deserialize_factory_create(model_type):
    """
    Проверяет создание пустой модели по переданному классу.

    1. Передать класс каждой доменной модели в create().

    <expected>Возвращается экземпляр ожидаемого класса.</expected>
    """
    assert isinstance(deserialize_factory().create(model_type), model_type)


@pytest.mark.parametrize("model_type", [None, "group_model", dict])
def test_invalid_result_deserialize_factory_create_not_a_model(model_type):
    """
    Проверяет реакцию фабрики на некласс модели.

    1. Передать в create() None, строку и dict.

    <expected>arguments_exception.</expected>
    """
    with pytest.raises(arguments_exception):
        deserialize_factory().create(model_type)


def test_invalid_result_deserialize_factory_unknown_json():
    """
    Проверяет реакцию фабрики на JSON без указания типа модели.

    1. Передать {"unknown": 1} в Convert().

    <expected>arguments_exception, так как тип модели определить нельзя.</expected>
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


class _sample_child(abstract_model):
    """Тестовая модель без доменных полей: только title."""

    def __init__(self) -> None:
        super().__init__()
        self.__title = ""

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        self.__title = value


class _sample_parent(abstract_model):
    """Тестовая модель с полем-ссылкой и списком ссылок."""

    def __init__(self) -> None:
        super().__init__()
        self.__child = None
        self.__children = []

    @property
    def child(self) -> _sample_child:
        return self.__child

    @child.setter
    def child(self, value: _sample_child) -> None:
        self.__child = value

    @property
    def children(self) -> list[_sample_child]:
        return self.__children

    @children.setter
    def children(self, value: list[_sample_child]) -> None:
        self.__children = value


def test_valid_result_deserialize_factory_uses_annotations():
    """
    Проверяет, что типы берутся из аннотаций, а не из имён полей JSON.

    1. Десериализовать модель с произвольными именами полей child и children.

    <expected>Вложенные объекты созданы как _sample_child.</expected>
    """
    source = {
        "unique_code": "sample-parent",
        "child": {"unique_code": "sample-child-1", "title": "один"},
        "children": [{"unique_code": "sample-child-2", "title": "два"}],
    }

    restored = deserialize_factory().Convert(source, _sample_parent)

    assert isinstance(restored, _sample_parent)
    assert isinstance(restored.child, _sample_child)
    assert restored.child.title == "один"
    assert isinstance(restored.children[0], _sample_child)
    assert restored.children[0].title == "два"


def test_valid_result_deserialize_factory_roundtrip_models():
    """
    Проверяет полный цикл сериализации и десериализации моделей storage_manager.

    1. Сформировать данные через storage_manager.convert().
    2. Сериализовать их через convert_factory, прогнать через JSON.
    3. Восстановить через deserialize_factory со схемой коллекций.
    4. Сравнить unique_code и типы всех коллекций.

    <expected>Коллекции совпадают по коду, количеству и типам моделей.</expected>
    """
    sm = _build_storage()
    payload = json.loads(json.dumps(_serialized_storage(sm), ensure_ascii=False))

    restored = deserialize_factory().Convert(payload, sm.collection_models)

    assert set(restored) == set(sm.collection_models)
    for key, model_type in sm.collection_models.items():
        assert all(isinstance(item, model_type) for item in restored[key])
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
    restored = deserialize_factory().Convert(payload, sm.collection_models)

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

    # Проверяем, что рекурсивный пересчет веса не потерян после десериализации
    salt = nomenclature_model.create("Соль", "Соль поваренная", flour.group, gram)
    dough.add_row(recipe_row_model.create(salt, gram, gross_weight=5.0, net_weight=5.0))
    assert cookie.gross_weight == 605.0
    assert cookie.net_weight == 595.0


def test_valid_result_deserialize_factory_receipt_json_with_empty_comments_and_short_refs():
    """
    Проверяет десериализацию convert_factory_receipt.json с пустыми comments и краткими ссылками.

    1. Прочитать _docs/json/convert_factory_receipt.json.
    2. Восстановить receipt_model через deserialize_factory.

    <expected>Рецепт, вложенный полуфабрикат и ссылки восстановлены без ошибок валидации.</expected>
    """
    with open(_RECEIPT_JSON_PATH, "r", encoding="utf-8") as file:
        restored = deserialize_factory().Convert(json.load(file), receipt_model)

    assert isinstance(restored, receipt_model)
    assert restored.comments == ""
    assert len(restored.rows) == 1
    assert restored.rows[0].sub_recipe is not None
    assert restored.rows[0].sub_recipe.dish is restored.rows[0].nomenclature
    assert restored.gross_weight == 250.0
    assert restored.net_weight == 240.0


def test_valid_result_deserialize_factory_settings_and_organization_field_order():
    """
    Проверяет десериализацию settings_model и organization_model независимо от порядка ключей JSON.

    1. Передать словарь настроек, где account идет раньше bic, а response_format задан строкой.
    2. Восстановить settings_model через deserialize_factory.

    <expected>Организация и Enum-формат восстановлены без ошибки порядка валидации bic/account.</expected>
    """
    payload = {
        "unique_code": "settings-1",
        "organization": {
            "unique_code": "org-1",
            "account": "40702810900000000000",
            "bic": "044525225",
            "inn": "7707083893",
            "name": "Ромашка",
            "owner": "",
        },
        "boss_name": "",
        "account_name": "Петрова А.А.",
        "first_launch_flag": False,
        "response_format": "CSV",
    }

    restored = deserialize_factory().Convert(payload, settings_model)

    assert isinstance(restored, settings_model)
    assert isinstance(restored.organization, organization_model)
    assert restored.organization.account == "40702810900000000000"
    assert restored.response_format == report_type_enum.CSV
    assert restored.first_launch_flag is False


def test_valid_result_deserialize_factory_json_all_collections():
    """
    Проверяет восстановление всех коллекций из приложенного JSON-файла.

    1. Прочитать _docs/json/storage_manager.json и десериализовать.

    <expected>Восстановлены все коллекции схемы без потери элементов.</expected>
    """
    restored = _load_json()
    sm = _build_storage()

    assert set(restored) == set(sm.collection_models)
    for key in sm.collection_models:
        assert len(restored[key]) == len(getattr(sm, key))


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
