import pytest
from pathlib import Path

from Src.Core.exception import arguments_exception
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
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
    Проверяет работу шаблона Singleton для класса storage_manager.

    1. Получить два экземпляра storage_manager через вызов конструктора.
    2. Убедиться, что обе переменные ссылаются на один и тот же объект в памяти.

    <expected>sm1 is sm2</expected>
    """
    sm1 = storage_manager()
    sm2 = storage_manager()
    assert sm1 is sm2


# =========================================================================
# 2. Проверка уникальности элементов
# =========================================================================

def test_valid_result_storage_manager_add_warehouse_unique():
    """
    Проверяет уникальность добавления складов методом add_warehouse.

    1. Добавить склад 'Основной склад'.
    2. Попытаться добавить второй склад с тем же именем.
    3. Убедиться, что второй вызов возвращает False и в хранилище только 1 элемент.

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


def test_valid_result_storage_manager_add_range_unique():
    """
    Проверяет уникальность добавления единиц измерения методом add_range.

    1. Добавить единицу измерения 'грамм'.
    2. Попытаться добавить дубликат с тем же именем.

    <expected>Дубликат отклонен, в списке ranges ровно 1 элемент</expected>
    """
    sm = storage_manager()
    u1 = range_model(name="грамм", conversion_factor=1.0)
    u2 = range_model(name="грамм", conversion_factor=1.0)

    assert sm.add_range(u1) is True
    assert sm.add_range(u2) is False
    assert len(sm.ranges) == 1


def test_valid_result_storage_manager_add_group_unique():
    """
    Проверяет уникальность добавления групп номенклатуры методом add_group.

    1. Добавить группу номенклатуры 'Ингредиенты'.
    2. Попытаться добавить группу с тем же наименованием.

    <expected>Дубликат отклонен, len(groups) == 1</expected>
    """
    sm = storage_manager()
    g1 = group_model(name="Ингредиенты")
    g2 = group_model(name="Ингредиенты")

    assert sm.add_group(g1) is True
    assert sm.add_group(g2) is False
    assert len(sm.groups) == 1


def test_valid_result_storage_manager_add_nomenclature_unique():
    """
    Проверяет уникальность добавления номенклатурных позиций методом add_nomenclature.

    1. Создать группу и единицу измерения.
    2. Создать объекты номенклатуры без параметров в конструкторе.
    3. Добавить номенклатуру 'Мука'.
    4. Попытаться добавить позицию с таким же наименованием 'Мука'.

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


def test_valid_result_storage_manager_add_recipe_unique():
    """
    Проверяет уникальность добавления технологических карт методом add_recipe.

    1. Создать технологическую карту 'Песочное тесто'.
    2. Попытаться повторно добавить рецепт с тем же наименованием.

    <expected>Дубликат отклонен, len(recipes) == 1</expected>
    """
    sm = storage_manager()
    grp = group_model.create("Полуфабрикаты")
    unit = range_model.create("грамм", 1.0)
    dish = nomenclature_model.create("Тесто", "Песочное тесто", grp, unit)

    rec1 = receipt_model.create(name="Песочное тесто", dish=dish)
    rec2 = receipt_model.create(name="Песочное тесто", dish=dish)

    assert sm.add_recipe(rec1) is True
    assert sm.add_recipe(rec2) is False
    assert len(sm.recipes) == 1


# =========================================================================
# 3. Проверка методов формирования данных (convert и load)
# =========================================================================

def test_valid_result_storage_manager_convert_success():
    """
    Проверяет прямое формирование первичных данных через convert().

    1. Вызвать метод convert() у storage_manager.
    2. Убедиться, что возвращено True и все списки заполнены.

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
    assert len(sm.recipes) >= 2


def test_valid_result_storage_manager_convert_base_range_linked():
    """
    Проверяет связывание базовых единиц измерения при convert().

    1. Сформировать данные через convert().
    2. Найти единицу 'килограмм' и проверить, что ее base указывает на 'грамм'.

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
    Проверяет установку связей номенклатуры с группой и единицей измерения.

    1. Сформировать данные через convert().
    2. Найти номенклатуру 'Мука пшеничная'.
    3. Проверить, что ее свойства group и range являются объектами моделей.

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
    Проверяет вызов load() для запуска логики первого старта.

    1. Загрузить настройки settings.json с first_launch_flag = True.
    2. Вызвать sm.load(_settings_path()).
    3. Проверить успешность формирования данных.

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
    Проверяет формирование первичных данных при первом старте системы.

    1. Загрузить настройки и установить first_launch_flag = True.
    2. Вызвать first_start(_settings_path()).
    3. Проверить заполнение всех справочников данными для рецепта.
    4. Проверить автоматический сброс флага first_launch_flag в False.

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
    Проверяет запрет повторной генерации первичных данных при first_launch_flag = False.

    1. Загрузить настройки и принудительно установить first_launch_flag = False.
    2. Вызвать first_start(_settings_path()).
    3. Убедиться, что первичные данные не создаются повторно.

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
    Проверяет корректность связей моделей в данных первого старта.

    1. Запустить first_start с флагом True.
    2. Найти 'Мука пшеничная' и проверить ее группу и единицу измерения.

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
    Проверяет генерацию технологических карт (рецептов) при первом старте.

    1. Запустить first_start с флагом True.
    2. Проверить наличие рецепта полуфабриката ('Песочное тесто')
       и рецепта готового блюда с упаковкой ('Песочное печенье в упаковке').
    3. Проверить, что готовое блюдо использует принцип 'блюдо в блюде' (включает sub_recipe).

    <expected>Оба рецепта сформированы, печенье включает вложенный рецепт теста и упаковку.</expected>
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

    rec_dough = sm._find_recipe_by_name("Песочное тесто")
    rec_cookie = sm._find_recipe_by_name("Песочное печенье в упаковке")
    assert rec_cookie is not None

    # Проверяем принцип "блюдо в блюде": строка содержит sub_recipe теста
    dough_row = next((r for r in rec_cookie.rows if r.sub_recipe is not None), None)
    assert dough_row is not None
    assert dough_row.sub_recipe == rec_dough
    assert dough_row.nomenclature.name == "Песочное тесто"

    # Проверяем наличие строки с упаковкой
    box_row = next((r for r in rec_cookie.rows if r.nomenclature.name == "Коробка крафтовая"), None)
    assert box_row is not None


def test_valid_result_storage_manager_first_start_recipes_weight_calculation():
    """
    Проверяет рекурсивное вычисление веса Брутто и Нетто для рецептов первого старта.

    1. Запустить first_start с флагом True.
    2. Проверить веса рецепта полуфабриката: Мука(250/250) + Масло(150/150) + Сахар(100/100) + Яйцо(60/50).
    3. Проверить рекурсивный расчет веса печенья: Тесто(560/550 рекурсивно) + Коробка(40/40).

    <expected>
    Тесто: брутто == 560, нетто == 550.
    Печенье в коробке (рекурсивно): брутто == 600, нетто == 590.
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
    # Рекурсивный расчет: 560 (из sub_recipe) + 40 (коробка)
    assert rec_cookie.gross_weight == 600.0
    # Рекурсивный расчет: 550 (из sub_recipe) + 40 (коробка)
    assert rec_cookie.net_weight == 590.0
