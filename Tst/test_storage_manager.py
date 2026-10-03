import pytest
from pathlib import Path

from Src.Core.exception import arguments_exception
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


def _settings_path() -> str:
    """Возвращает путь к тестовому файлу settings.json в каталоге Tst."""
    return str(Path(__file__).resolve().parent / "settings.json")


@pytest.fixture(autouse=True)
def reset_storage():
    """Сбрасывает состояние singleton-хранилища перед каждым тестом."""
    sm = storage_manager()
    sm._groups = []
    sm._ranges = []
    sm._nomenclatures = []
    sm._warehouses = []
    sm._is_loaded = False
    sm._data = {}

    settings_mgr = settings_manager()
    settings_mgr._is_loaded = False
    settings_mgr._data = {}
    yield


# =========================================================================
# 1. Проверка шаблона Singleton
# =========================================================================

def test_valid_result_storage_manager_singleton():
    """
    <summary>Проверяет работу шаблона Singleton для класса storage_manager.</summary>
    <description>
    1. Получить два экземпляра storage_manager через вызов конструктора.
    2. Убедиться, что обе переменные ссылаются на один и тот же объект в памяти.
    </description>
    <expected>sm1 is sm2</expected>
    """
    sm1 = storage_manager()
    sm2 = storage_manager()
    assert sm1 is sm2


# =========================================================================
# 2. Проверка уникальности элементов
# =========================================================================

def test_valid_result_storage_manager_unique_warehouses():
    """
    <summary>Проверяет уникальность добавления складов в хранилище.</summary>
    <description>
    1. Добавить склад 'Основной склад'.
    2. Попытаться добавить второй склад с тем же именем.
    3. Убедиться, что второй вызов возвращает False и в хранилище только 1 элемент.
    </description>
    <expected>Первый добавлен, дубликат отклонен, len(warehouses) == 1</expected>
    """
    sm = storage_manager()
    wh1 = warehouse_model(name="Основной склад", address="ул. Ленина, 1")
    wh2 = warehouse_model(name="Основной склад", address="ул. Мира, 5")

    added_first = sm.add_warehouse(wh1)
    added_second = sm.add_warehouse(wh2)

    assert added_first is True
    assert added_second is False
    assert len(sm.warehouses) == 1
    assert sm.warehouses[0].address == "ул. Ленина, 1"


def test_valid_result_storage_manager_unique_ranges():
    """
    <summary>Проверяет уникальность добавления единиц измерения.</summary>
    <description>
    1. Добавить единицу измерения 'грамм'.
    2. Попытаться добавить дубликат с тем же именем.
    </description>
    <expected>Дубликат отклонен, в списке ranges ровно 1 элемент</expected>
    """
    sm = storage_manager()
    u1 = range_model(name="грамм", conversion_factor=1.0)
    u2 = range_model(name="грамм", conversion_factor=1.0)

    assert sm.add_range(u1) is True
    assert sm.add_range(u2) is False
    assert len(sm.ranges) == 1


def test_valid_result_storage_manager_unique_groups():
    """
    <summary>Проверяет уникальность добавления групп номенклатуры.</summary>
    <description>
    1. Добавить группу номенклатуры 'Ингредиенты'.
    2. Попытаться добавить группу с тем же наименованием.
    </description>
    <expected>Дубликат отклонен, len(groups) == 1</expected>
    """
    sm = storage_manager()
    g1 = group_model(name="Ингредиенты")
    g2 = group_model(name="Ингредиенты")

    assert sm.add_group(g1) is True
    assert sm.add_group(g2) is False
    assert len(sm.groups) == 1


def test_valid_result_storage_manager_unique_nomenclatures():
    """
    <summary>Проверяет уникальность добавления номенклатурных позиций.</summary>
    <description>
    1. Создать группу и единицу измерения.
    2. Добавить номенклатуру 'Мука'.
    3. Попытаться добавить позицию с таким же наименованием 'Мука'.
    </description>
    <expected>Дубликат отклонен, len(nomenclatures) == 1</expected>
    """
    sm = storage_manager()
    grp = group_model(name="Сырье")
    unit = range_model(name="кг", conversion_factor=1.0)

    nom1 = nomenclature_model(name="Мука", full_name="Мука высший сорт", group=grp, range=unit)
    nom2 = nomenclature_model(name="Мука", full_name="Мука первый сорт", group=grp, range=unit)

    assert sm.add_nomenclature(nom1) is True
    assert sm.add_nomenclature(nom2) is False
    assert len(sm.nomenclatures) == 1


# =========================================================================
# 3. Проверка методов convert и load
# =========================================================================

def test_valid_result_storage_manager_load_success():
    """
    <summary>Проверяет загрузку и конвертацию данных через load().</summary>
    <description>
    1. Вызвать sm.load(_settings_path()).
    2. Проверить успешность конвертации и заполнение списков.
    </description>
    <expected>sm.is_loaded is True, все коллекции не пусты</expected>
    """
    sm = storage_manager()
    sm.load(_settings_path())

    assert sm.is_loaded is True
    assert len(sm.ranges) > 0
    assert len(sm.groups) > 0
    assert len(sm.warehouses) > 0
    assert len(sm.nomenclatures) > 0


def test_valid_result_storage_manager_convert_base_range_linked():
    """
    <summary>Проверяет связывание базовых единиц измерения при convert().</summary>
    <description>
    1. Загрузить настройки из JSON.
    2. Найти единицу 'килограмм' и проверить, что ее base указывает на 'грамм'.
    </description>
    <expected>kg.base is not None, kg.base.name == 'грамм'</expected>
    """
    sm = storage_manager()
    sm.load(_settings_path())

    kg = sm._find_range_by_name("килограмм")
    assert kg is not None
    assert kg.base is not None
    assert kg.base.name == "грамм"


def test_valid_result_storage_manager_convert_nomenclature_relations():
    """
    <summary>Проверяет установку связей номенклатуры с группой и единицей измерения.</summary>
    <description>
    1. Загрузить настройки.
    2. Найти номенклатуру 'Молоко'.
    3. Проверить, что ее свойства group и range являются объектами моделей.
    </description>
    <expected>nom.group.name == 'Молочная продукция', nom.range.name == 'литр'</expected>
    """
    sm = storage_manager()
    sm.load(_settings_path())

    nom = next((n for n in sm.nomenclatures if n.name == "Молоко"), None)
    assert nom is not None
    assert isinstance(nom.group, group_model)
    assert nom.group.name == "Молочная продукция"
    assert isinstance(nom.range, range_model)
    assert nom.range.name == "литр"


def test_invalid_result_storage_manager_convert_bad_data():
    """
    <summary>Проверяет поведение convert() при некорректных входных данных.</summary>
    <description>
    1. Установить _data в None или пустую строку.
    2. Вызвать convert().
    </description>
    <expected>convert() возвращает False, is_loaded == False</expected>
    """
    sm = storage_manager()
    sm._data = "not a dictionary"
    res = sm.convert()

    assert res is False
    assert sm.is_loaded is False


def test_invalid_result_storage_manager_convert_missing_group():
    """
    <summary>Проверяет обработку ситуации, когда для номенклатуры не найдена группа.</summary>
    <description>
    1. Передать структуру данных с номенклатурой, ссылающейся на несуществующую группу.
    2. Вызвать convert().
    </description>
    <expected>convert() завершается ошибкой и возвращает False</expected>
    """
    sm = storage_manager()
    sm._data = {
        "ranges": [{"name": "шт", "conversion_factor": 1.0}],
        "groups": [],
        "nomenclature": [{"name": "Товар", "group": "Неизвестная группа", "range": "шт"}]
    }
    assert sm.convert() is False


# =========================================================================
# 4. Проверка логики первого старта (first_start)
# =========================================================================

def test_valid_result_storage_manager_first_start_generates_data():
    """
    <summary>Проверяет формирование первичных данных при первом старте системы.</summary>
    <description>
    1. Загрузить настройки и установить first_launch_flag = True.
    2. Вызвать first_start(_settings_path()).
    3. Проверить заполнение всех 4 справочников данными для рецепта.
    4. Проверить автоматический сброс флага first_launch_flag в False.
    </description>
    <expected>res is True, first_launch_flag == False, данные рецепта созданы</expected>
    """
    settings_mgr = settings_manager()
    settings_mgr.load(_settings_path())
    settings_mgr.settings.first_launch_flag = True

    sm = storage_manager()
    res = sm.first_start(_settings_path())

    assert res is True
    assert sm.is_loaded is True

    # Проверяем наполнение справочников
    assert len(sm.ranges) >= 4
    assert len(sm.warehouses) >= 2
    assert len(sm.groups) >= 2
    assert len(sm.nomenclatures) >= 4

    # Проверяем наличие ключевых ингредиентов под рецепт
    nom_names = [item.name for item in sm.nomenclatures]
    assert "Мука пшеничная" in nom_names
    assert "Сливочное масло" in nom_names
    assert "Сахар" in nom_names
    assert "Яйцо куриное" in nom_names

    # Проверяем, что флаг сброшен
    assert settings_mgr.settings.first_launch_flag is False


def test_valid_result_storage_manager_first_start_disabled():
    """
    <summary>Проверяет запрет повторной генерации первичных данных при first_launch_flag = False.</summary>
    <description>
    1. Загрузить настройки и принудительно установить first_launch_flag = False.
    2. Вызвать first_start(_settings_path()).
    3. Убедиться, что первичные данные не создаются.
    </description>
    <expected>first_start() возвращает False, хранилища остаются пустыми</expected>
    """
    settings_mgr = settings_manager()
    settings_mgr.load(_settings_path())
    settings_mgr.settings.first_launch_flag = False

    sm = storage_manager()
    res = sm.first_start(_settings_path())

    assert res is False
    assert len(sm.warehouses) == 0
    assert len(sm.nomenclatures) == 0


def test_valid_result_storage_manager_first_start_recipe_linked():
    """
    <summary>Проверяет корректность связей моделей в данных первого старта.</summary>
    <description>
    1. Запустить first_start с флагом True.
    2. Найти 'Мука пшеничная' и проверить ее группу и единицу измерения.
    </description>
    <expected>Группа == 'Ингредиенты', единица == 'грамм'</expected>
    """
    settings_mgr = settings_manager()
    settings_mgr.load(_settings_path())
    settings_mgr.settings.first_launch_flag = True

    sm = storage_manager()
    sm.first_start(_settings_path())

    flour = next((n for n in sm.nomenclatures if n.name == "Мука пшеничная"), None)
    assert flour is not None
    assert flour.group.name == "Ингредиенты"
    assert flour.range.name == "грамм"
