import pytest
from pathlib import Path

from Src.Core.exception import arguments_exception
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
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
    sm._recipes = []
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
    2. Создать объекты номенклатуры без параметров в конструкторе.
    3. Добавить номенклатуру 'Мука'.
    4. Попытаться добавить позицию с таким же наименованием 'Мука'.
    </description>
    <expected>Дубликат отклонен, len(nomenclatures) == 1</expected>
    """
    sm = storage_manager()
    grp = group_model(name="Сырье")
    unit = range_model(name="кг", conversion_factor=1.0)

    nom1 = nomenclature_model()
    nom1.name = "Мука"
    nom1.full_name = "Мука высший сорт"
    nom1.group = grp
    nom1.range = unit

    nom2 = nomenclature_model()
    nom2.name = "Мука"
    nom2.full_name = "Мука первый сорт"
    nom2.group = grp
    nom2.range = unit

    assert sm.add_nomenclature(nom1) is True
    assert sm.add_nomenclature(nom2) is False
    assert len(sm.nomenclatures) == 1


def test_valid_result_storage_manager_unique_recipes():
    """
    <summary>Проверяет уникальность добавления технологических карт (рецептов).</summary>
    <description>
    1. Создать рецепт 'Песочное тесто'.
    2. Попытаться повторно добавить рецепт с тем же наименованием.
    </description>
    <expected>Дубликат отклонен, len(recipes) == 1</expected>
    """
    sm = storage_manager()
    grp = group_model.create("Полуфабрикаты")
    unit = range_model.create("грамм", 1.0)
    dish = nomenclature_model.create("Тесто", "Песочное тесто", grp, unit)

    rec1 = recipe_model.create(name="Песочное тесто", dish=dish)
    rec2 = recipe_model.create(name="Песочное тесто", dish=dish)

    assert sm.add_recipe(rec1) is True
    assert sm.add_recipe(rec2) is False
    assert len(sm.recipes) == 1


# =========================================================================
# 3. Проверка методов формирования данных (convert и load)
# =========================================================================

def test_valid_result_storage_manager_convert_success():
    """
    <summary>Проверяет прямое формирование первичных данных через convert().</summary>
    <description>
    1. Вызвать метод convert() у storage_manager.
    2. Убедиться, что возвращено True и все списки заполнены.
    </description>
    <expected>convert() is True, is_loaded is True, все коллекции не пусты</expected>
    """
    sm = storage_manager()
    res = sm.convert()

    assert res is True
    assert sm.is_loaded is True
    assert len(sm.ranges) >= 4
    assert len(sm.groups) >= 2
    assert len(sm.warehouses) >= 2
    assert len(sm.nomenclatures) >= 4


def test_valid_result_storage_manager_convert_base_range_linked():
    """
    <summary>Проверяет связывание базовых единиц измерения при convert().</summary>
    <description>
    1. Сформировать данные через convert().
    2. Найти единицу 'килограмм' и проверить, что ее base указывает на 'грамм'.
    </description>
    <expected>kg.base is not None, kg.base.name == 'грамм'</expected>
    """
    sm = storage_manager()
    sm.convert()

    kg = sm._find_range_by_name("килограмм")
    assert kg is not None
    assert kg.base is not None
    assert kg.base.name == "грамм"


def test_valid_result_storage_manager_convert_nomenclature_relations():
    """
    <summary>Проверяет установку связей номенклатуры с группой и единицей измерения.</summary>
    <description>
    1. Сформировать данные через convert().
    2. Найти номенклатуру 'Мука пшеничная'.
    3. Проверить, что ее свойства group и range являются объектами моделей.
    </description>
    <expected>nom.group.name == 'Ингредиенты', nom.range.name == 'грамм'</expected>
    """
    sm = storage_manager()
    sm.convert()

    nom = next((n for n in sm.nomenclatures if n.name == "Мука пшеничная"), None)
    assert nom is not None
    assert isinstance(nom.group, group_model)
    assert nom.group.name == "Ингредиенты"
    assert isinstance(nom.range, range_model)
    assert nom.range.name == "грамм"


def test_valid_result_storage_manager_load_success():
    """
    <summary>Проверяет вызов load() для запуска логики первого старта.</summary>
    <description>
    1. Загрузить настройки settings.json с first_launch_flag = True.
    2. Вызвать sm.load(_settings_path()).
    3. Проверить успешность формирования данных.
    </description>
    <expected>sm.is_loaded is True, данные созданы</expected>
    """
    settings_mgr = settings_manager()
    settings_mgr.load(_settings_path())
    settings_mgr.settings.first_launch_flag = True

    sm = storage_manager()
    sm.load(_settings_path())

    assert sm.is_loaded is True
    assert len(sm.ranges) > 0
    assert len(sm.nomenclatures) > 0


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
    3. Убедиться, что первичные данные не создаются повторно.
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


def test_valid_result_storage_manager_first_start_generates_recipes():
    """
    <summary>Проверяет генерацию технологических карт (рецептов) при первом старте.</summary>
    <description>
    1. Запустить first_start с флагом True.
    2. Проверить наличие рецепта полуфабриката ('Песочное тесто')
       и рецепта готового блюда с упаковкой ('Песочное печенье в упаковке').
    </description>
    <expected>Оба рецепта сформированы и зарегистрированы в хранилище.</expected>
    """
    settings_mgr = settings_manager()
    settings_mgr.load(_settings_path())
    settings_mgr.settings.first_launch_flag = True

    sm = storage_manager()
    sm.first_start(_settings_path())

    assert len(sm.recipes) >= 2
    rec_names = [r.name for r in sm.recipes]
    assert "Песочное тесто" in rec_names
    assert "Песочное печенье в упаковке" in rec_names

    # Проверяем, что в рецепте готового блюда есть полуфабрикат и упаковка
    rec_cookie = sm._find_recipe_by_name("Песочное печенье в упаковке")
    assert rec_cookie is not None
    row_noms = [r.nomenclature.name for r in rec_cookie.rows]
    assert "Песочное тесто" in row_noms
    assert "Коробка крафтовая" in row_noms


def test_valid_result_storage_manager_first_start_recipes_weight_calculation():
    """
    <summary>Проверяет вычисление веса Брутто и Нетто для рецептов первого старта.</summary>
    <description>
    1. Запустить first_start с флагом True.
    2. Проверить веса рецепта полуфабриката: Мука(250/250) + Масло(150/150) + Сахар(100/100) + Яйцо(60/50).
    3. Проверить веса рецепта печенья в упаковке: Тесто(560/500) + Коробка(40/40).
    </description>
    <expected>
    Тесто: брутто == 560, нетто == 550.
    Печенье в коробке: брутто == 600, нетто == 540.
    </expected>
    """
    settings_mgr = settings_manager()
    settings_mgr.load(_settings_path())
    settings_mgr.settings.first_launch_flag = True

    sm = storage_manager()
    sm.first_start(_settings_path())

    rec_dough = sm._find_recipe_by_name("Песочное тесто")
    assert rec_dough is not None
    assert rec_dough.gross_weight == 560.0
    assert rec_dough.net_weight == 550.0

    rec_cookie = sm._find_recipe_by_name("Песочное печенье в упаковке")
    assert rec_cookie is not None
    assert rec_cookie.gross_weight == 600.0
    assert rec_cookie.net_weight == 540.0
