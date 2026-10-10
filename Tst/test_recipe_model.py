import pytest

from Src.Core.exception import arguments_exception
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.warehouse_model import warehouse_model


# =========================================================================
# Вспомогательные фикстуры
# =========================================================================

@pytest.fixture
def sample_components():
    """Создает базовый набор связанных моделей для тестирования рецептов."""
    grp_ing = group_model.create("Ингредиенты")
    grp_semi = group_model.create("Полуфабрикаты")
    grp_dish = group_model.create("Готовые блюда")
    grp_pack = group_model.create("Тара и упаковка")

    unit_g = range_model.create("грамм", 1.0)
    unit_pcs = range_model.create("штука", 1.0)

    nom_flour = nomenclature_model.create("Мука", "Мука высший сорт", grp_ing, unit_g)
    nom_sugar = nomenclature_model.create("Сахар", "Сахар песок", grp_ing, unit_g)
    nom_dough = nomenclature_model.create("Тесто", "Песочное тесто полуфабрикат", grp_semi, unit_g)
    nom_box = nomenclature_model.create("Коробка", "Коробка крафт", grp_pack, unit_pcs)
    nom_cookie = nomenclature_model.create("Печенье", "Печенье в коробке", grp_dish, unit_pcs)

    return {
        "unit_g": unit_g,
        "unit_pcs": unit_pcs,
        "nom_flour": nom_flour,
        "nom_sugar": nom_sugar,
        "nom_dough": nom_dough,
        "nom_box": nom_box,
        "nom_cookie": nom_cookie,
    }


# =========================================================================
# 1. Тестирование recipe_row_model
# =========================================================================

def test_valid_result_recipe_row_model_creation(sample_components):
    """
    <summary>Проверяет создание строки рецепта через конструктор и сеттеры.</summary>
    <description>
    1. Создать объект recipe_row_model без параметров.
    2. Установить номенклатуру, единицу измерения, брутто и нетто через свойства.
    </description>
    <expected>Все поля сохраняют переданные значения, unique_code сформирован.</expected>
    """
    row = recipe_row_model()
    row.nomenclature = sample_components["nom_flour"]
    row.range = sample_components["unit_g"]
    row.gross_weight = 250.0
    row.net_weight = 240.0

    assert row.nomenclature == sample_components["nom_flour"]
    assert row.range == sample_components["unit_g"]
    assert row.gross_weight == 250.0
    assert row.net_weight == 240.0
    assert row.unique_code != ""


def test_valid_result_recipe_row_model_factory_method(sample_components):
    """
    <summary>Проверяет создание строки рецепта через статический фабричный метод create.</summary>
    <description>
    1. Вызвать recipe_row_model.create с корректными параметрами.
    </description>
    <expected>Возвращается заполненный объект строки рецепта.</expected>
    """
    row = recipe_row_model.create(
        nomenclature=sample_components["nom_sugar"],
        range=sample_components["unit_g"],
        gross_weight=100.0,
        net_weight=95.0
    )

    assert row.nomenclature.name == "Сахар"
    assert row.gross_weight == 100.0
    assert row.net_weight == 95.0


@pytest.mark.parametrize("value", [-1.0, -100, -0.01])
def test_invalid_result_recipe_row_model_negative_gross_weight(sample_components, value):
    """
    <summary>Проверяет запрет отрицательного веса брутто в строке рецепта.</summary>
    <description>
    1. Попытаться установить отрицательный вес брутто.
    </description>
    <expected>Возбуждается arguments_exception.</expected>
    """
    row = recipe_row_model()
    with pytest.raises(arguments_exception):
        row.gross_weight = value


@pytest.mark.parametrize("value", [-1.0, -50, -0.5])
def test_invalid_result_recipe_row_model_negative_net_weight(sample_components, value):
    """
    <summary>Проверяет запрет отрицательного веса нетто в строке рецепта.</summary>
    <description>
    1. Попытаться установить отрицательный вес нетто.
    </description>
    <expected>Возбуждается arguments_exception.</expected>
    """
    row = recipe_row_model()
    with pytest.raises(arguments_exception):
        row.net_weight = value


@pytest.mark.parametrize("value", [None, "100", [], {}])
def test_invalid_result_recipe_row_model_weight_type(sample_components, value):
    """
    <summary>Проверяет валидацию типа данных для веса строки рецепта.</summary>
    <description>
    1. Передать в gross_weight и net_weight значения нечисловых типов.
    </description>
    <expected>Возбуждается arguments_exception.</expected>
    """
    row = recipe_row_model()
    with pytest.raises(arguments_exception):
        row.gross_weight = value
    with pytest.raises(arguments_exception):
        row.net_weight = value


# =========================================================================
# 2. Тестирование recipe_model: свойства, Брутто и Нетто
# =========================================================================

def test_valid_result_recipe_model_creation_and_properties(sample_components):
    """
    <summary>Проверяет базовое создание рецепта через фабричный метод create.</summary>
    <description>
    1. Создать технологическую карту через recipe_model.create.
    </description>
    <expected>Имя, блюдо и комментарий соответствуют переданным значениям.</expected>
    """
    recipe = recipe_model.create(
        name="Песочное тесто",
        dish=sample_components["nom_dough"],
        comments="Базовый замес"
    )

    assert recipe.name == "Песочное тесто"
    assert recipe.dish == sample_components["nom_dough"]
    assert recipe.comments == "Базовый замес"
    assert len(recipe.rows) == 0
    assert recipe.gross_weight == 0.0
    assert recipe.net_weight == 0.0


def test_valid_result_recipe_model_gross_and_net_weight_calculation(sample_components):
    """
    <summary>Проверяет корректность расчета веса Брутто и Нетто путем сложения весов ингредиентов.</summary>
    <description>
    1. Создать рецепт с двумя строками ингредиентов (250/240 и 100/95).
    2. Проверить вычисленные свойства gross_weight и net_weight.
    </description>
    <expected>gross_weight == 350.0, net_weight == 335.0</expected>
    """
    r1 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 250.0, 240.0)
    r2 = recipe_row_model.create(sample_components["nom_sugar"], sample_components["unit_g"], 100.0, 95.0)

    recipe = recipe_model.create(
        name="Тесто",
        dish=sample_components["nom_dough"],
        rows=[r1, r2]
    )

    assert recipe.gross_weight == 350.0
    assert recipe.net_weight == 335.0


def test_valid_result_recipe_model_add_row_increases_weight(sample_components):
    """
    <summary>Проверяет динамическое увеличение веса Брутто и Нетто при добавлении нового ингредиента.</summary>
    <description>
    1. Создать рецепт с одним ингредиентом (250/240).
    2. Зафиксировать начальные веса.
    3. Добавить второй ингредиент (100/95).
    4. Убедиться, что веса увеличились на величину параметров второго ингредиента.
    </description>
    <expected>Веса увеличиваются строго на вес добавленной строки.</expected>
    """
    recipe = recipe_model()
    recipe.name = "Рецепт"
    recipe.dish = sample_components["nom_dough"]

    r1 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 250.0, 240.0)
    assert recipe.add_row(r1) is True
    assert recipe.gross_weight == 250.0
    assert recipe.net_weight == 240.0

    r2 = recipe_row_model.create(sample_components["nom_sugar"], sample_components["unit_g"], 100.0, 95.0)
    assert recipe.add_row(r2) is True
    assert recipe.gross_weight == 350.0
    assert recipe.net_weight == 335.0


def test_valid_result_recipe_model_remove_row_decreases_weight(sample_components):
    """
    <summary>Проверяет динамическое уменьшение веса Брутто и Нетто при исключении ингредиента из рецепта.</summary>
    <description>
    1. Создать рецепт с двумя ингредиентами (суммарно 350/335).
    2. Исключить один ингредиент через remove_row.
    3. Проверить уменьшение суммарных весов.
    </description>
    <expected>Строка удалена, веса уменьшились до остаточных значений.</expected>
    """
    r1 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 250.0, 240.0)
    r2 = recipe_row_model.create(sample_components["nom_sugar"], sample_components["unit_g"], 100.0, 95.0)

    recipe = recipe_model.create(name="Рецепт", dish=sample_components["nom_dough"], rows=[r1, r2])
    assert recipe.gross_weight == 350.0

    removed = recipe.remove_row(r2)
    assert removed is True
    assert len(recipe.rows) == 1
    assert recipe.gross_weight == 250.0
    assert recipe.net_weight == 240.0


def test_valid_result_recipe_model_duplicate_row_rejected(sample_components):
    """
    <summary>Проверяет отклонение добавления дублирующейся строки с той же номенклатурой.</summary>
    <description>
    1. Добавить строку с Мукой.
    2. Попытаться повторно добавить строку с Мукой.
    </description>
    <expected>add_row возвращает False, в рецепте остается ровно 1 строка.</expected>
    """
    recipe = recipe_model()
    recipe.name = "Рецепт"
    recipe.dish = sample_components["nom_dough"]

    r1 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 250.0, 240.0)
    r2 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 50.0, 50.0)

    assert recipe.add_row(r1) is True
    assert recipe.add_row(r2) is False
    assert len(recipe.rows) == 1


def test_valid_result_recipe_model_remove_nonexistent_row_returns_false(sample_components):
    """
    <summary>Проверяет удаление отсутствующей строки из рецепта.</summary>
    <description>
    1. Попытаться удалить строку, которая не была добавлена в рецепт.
    </description>
    <expected>remove_row возвращает False.</expected>
    """
    recipe = recipe_model()
    recipe.name = "Рецепт"
    recipe.dish = sample_components["nom_dough"]

    r_absent = recipe_row_model.create(sample_components["nom_sugar"], sample_components["unit_g"], 10.0, 10.0)
    assert recipe.remove_row(r_absent) is False


def test_valid_result_recipe_with_semi_finished_and_packaging(sample_components):
    """
    <summary>Проверяет формирование рецепта, содержащего полуфабрикат и упаковочный материал.</summary>
    <description>
    1. Создать строку с полуфабрикатом 'Тесто' (560 брутто / 500 нетто).
    2. Создать строку с упаковкой 'Коробка' (40 брутто / 40 нетто).
    3. Создать технологическую карту готового блюда с упаковкой.
    </description>
    <expected>Рецепт содержит полуфабрикат и упаковку, суммарный вес брутто == 600, нетто == 540.</expected>
    """
    row_semi = recipe_row_model.create(sample_components["nom_dough"], sample_components["unit_g"], 560.0, 500.0)
    row_pack = recipe_row_model.create(sample_components["nom_box"], sample_components["unit_pcs"], 40.0, 40.0)

    recipe_boxed = recipe_model.create(
        name="Печенье в коробке",
        dish=sample_components["nom_cookie"],
        rows=[row_semi, row_pack],
        comments="Упаковка готового изделия"
    )

    noms = [r.nomenclature.name for r in recipe_boxed.rows]
    assert "Тесто" in noms
    assert "Коробка" in noms
    assert recipe_boxed.gross_weight == 600.0
    assert recipe_boxed.net_weight == 540.0


# =========================================================================
# 3. Тестирование фабричных методов (Factory Method) доменных моделей
# =========================================================================

def test_valid_result_factory_methods_all_domain_models():
    """
    <summary>Проверяет корректность работы фабричных методов create во всех доменных моделях.</summary>
    <description>
    1. Вызвать метод create для group_model, range_model, warehouse_model,
       nomenclature_model, recipe_row_model, recipe_model.
    2. Убедиться, что возвращаются проинициализированные экземпляры с заполненными свойствами.
    </description>
    <expected>Все созданные фабриками объекты валидны и содержат уникальный код.</expected>
    """
    grp = group_model.create("Сырье")
    assert isinstance(grp, group_model)
    assert grp.name == "Сырье"
    assert grp.unique_code != ""

    rng_base = range_model.create("грамм", 1.0)
    rng_kg = range_model.create("кг", 1000.0, rng_base)
    assert isinstance(rng_kg, range_model)
    assert rng_kg.name == "кг"
    assert rng_kg.base == rng_base

    wh = warehouse_model.create("Склад цеха", "г. Москва")
    assert isinstance(wh, warehouse_model)
    assert wh.name == "Склад цеха"
    assert wh.address == "г. Москва"

    nom = nomenclature_model.create("Какао", "Какао-порошок натуральный", grp, rng_base)
    assert isinstance(nom, nomenclature_model)
    assert nom.name == "Какао"
    assert nom.group == grp
    assert nom.range == rng_base

    row = recipe_row_model.create(nom, rng_base, 50.0, 48.0)
    assert isinstance(row, recipe_row_model)
    assert row.gross_weight == 50.0

    rec = recipe_model.create("Рецепт какао", nom, [row], "Горячий напиток")
    assert isinstance(rec, recipe_model)
    assert rec.name == "Рецепт какао"
    assert rec.gross_weight == 50.0
