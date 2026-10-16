import pytest

from Src.Core.exception import arguments_exception
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import recipe_row_model
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

    unit_g = range_model.create_gram()
    unit_pcs = range_model.create_piece()

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
    Проверяет создание строки рецепта через конструктор и сеттеры.

    1. Создать объект recipe_row_model без параметров.
    2. Установить номенклатуру, единицу измерения, брутто и нетто через свойства.

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


def test_valid_result_recipe_row_model_create_factory(sample_components):
    """
    Проверяет создание строки рецепта через фабричный метод create.

    1. Вызвать recipe_row_model.create с параметрами сырья.

    <expected>Возвращается заполненный объект строки рецепта.</expected>
    """
    row = recipe_row_model.create(
        sample_components["nom_sugar"],
        sample_components["unit_g"],
        100.0,
        95.0
    )

    assert row.nomenclature.name == "Сахар"
    assert row.gross_weight == 100.0
    assert row.net_weight == 95.0


def test_valid_result_recipe_row_model_create_with_sub_recipe(sample_components):
    """
    Проверяет создание строки рецепта со ссылкой на вложенный рецепт (блюдо в блюде).

    1. Создать базовый рецепт полуфабриката.
    2. Создать строку рецепта, передав объект receipt_model в качестве item.

    <expected>row.sub_recipe ссылается на рецепт, row.nomenclature берется из dish.</expected>
    """
    r1 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 200.0, 200.0)
    sub_rec = receipt_model.create("Тесто", sample_components["nom_dough"], [r1])

    row = recipe_row_model.create(sub_rec)
    assert row.sub_recipe == sub_rec
    assert row.nomenclature == sample_components["nom_dough"]
    # Вес берется рекурсивно из sub_recipe
    assert row.gross_weight == 200.0
    assert row.net_weight == 200.0


@pytest.mark.parametrize("value", [-1.0, -100, -0.01])
def test_invalid_result_recipe_row_model_gross_weight_negative(sample_components, value):
    """
    Проверяет запрет установки отрицательного веса брутто в строке рецепта.

    1. Попытаться установить отрицательный вес брутто.

    <expected>arguments_exception</expected>
    """
    row = recipe_row_model()
    with pytest.raises(arguments_exception):
        row.gross_weight = value


@pytest.mark.parametrize("value", [-1.0, -50, -0.5])
def test_invalid_result_recipe_row_model_net_weight_negative(sample_components, value):
    """
    Проверяет запрет установки отрицательного веса нетто в строке рецепта.

    1. Попытаться установить отрицательный вес нетто.

    <expected>arguments_exception</expected>
    """
    row = recipe_row_model()
    with pytest.raises(arguments_exception):
        row.net_weight = value


@pytest.mark.parametrize("value", [None, "100", [], {}])
def test_invalid_result_recipe_row_model_weight_type(sample_components, value):
    """
    Проверяет валидацию некорректного типа данных для веса строки рецепта.

    1. Передать в свойства gross_weight и net_weight значения нечисловых типов.

    <expected>arguments_exception</expected>
    """
    row = recipe_row_model()
    with pytest.raises(arguments_exception):
        row.gross_weight = value
    with pytest.raises(arguments_exception):
        row.net_weight = value


# =========================================================================
# 2. Тестирование receipt_model: свойства, Брутто и Нетто (рекурсия)
# =========================================================================

def test_valid_result_receipt_model_creation_and_properties(sample_components):
    """
    Проверяет базовое создание рецепта через фабричный метод create.

    1. Создать технологическую карту через receipt_model.create.

    <expected>Имя, блюдо и комментарий соответствуют переданным значениям.</expected>
    """
    recipe = receipt_model.create(
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


def test_valid_result_receipt_model_gross_and_net_weight_calculation(sample_components):
    """
    Проверяет корректность расчета веса Брутто и Нетто путем сложения весов ингредиентов.

    1. Создать рецепт с двумя строками ингредиентов (250/240 и 100/95).
    2. Проверить вычисленные свойства gross_weight и net_weight.

    <expected>gross_weight == 350.0, net_weight == 335.0</expected>
    """
    r1 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 250.0, 240.0)
    r2 = recipe_row_model.create(sample_components["nom_sugar"], sample_components["unit_g"], 100.0, 95.0)

    recipe = receipt_model.create(
        name="Тесто",
        dish=sample_components["nom_dough"],
        rows=[r1, r2]
    )

    assert recipe.gross_weight == 350.0
    assert recipe.net_weight == 335.0


def test_valid_result_receipt_model_add_row_increases_weight(sample_components):
    """
    Проверяет динамическое увеличение веса Брутто и Нетто при добавлении нового ингредиента.

    1. Создать рецепт с одним ингредиентом (250/240).
    2. Зафиксировать начальные веса.
    3. Добавить второй ингредиент (100/95).
    4. Убедиться, что веса увеличились на величину параметров второго ингредиента.

    <expected>Веса увеличиваются строго на вес добавленной строки.</expected>
    """
    recipe = receipt_model()
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


def test_valid_result_receipt_model_remove_row_decreases_weight(sample_components):
    """
    Проверяет динамическое уменьшение веса Брутто и Нетто при исключении ингредиента из рецепта.

    1. Создать рецепт с двумя ингредиентами (суммарно 350/335).
    2. Исключить один ингредиент через remove_row.
    3. Проверить уменьшение суммарных весов.

    <expected>Строка удалена, веса уменьшились до остаточных значений.</expected>
    """
    r1 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 250.0, 240.0)
    r2 = recipe_row_model.create(sample_components["nom_sugar"], sample_components["unit_g"], 100.0, 95.0)

    recipe = receipt_model.create(name="Рецепт", dish=sample_components["nom_dough"], rows=[r1, r2])
    assert recipe.gross_weight == 350.0

    removed = recipe.remove_row(r2)
    assert removed is True
    assert len(recipe.rows) == 1
    assert recipe.gross_weight == 250.0
    assert recipe.net_weight == 240.0


def test_valid_result_receipt_model_gross_and_net_weight_recursive(sample_components):
    """
    Проверяет рекурсивный расчет веса Брутто и Нетто для составного рецепта (блюдо в блюде).

    1. Создать технологическую карту теста (полуфабрикат): Мука (250/240) + Сахар (100/95) = 350/335.
    2. Создать технологическую карту печенья в упаковке, передав в строку сам рецепт теста и тару (40/40).
    3. Убедиться, что вес вычисляется рекурсивно: 350 + 40 = 390 брутто, 335 + 40 = 375 нетто.
    4. Добавить в рецепт теста еще один ингредиент (50/50) и проверить автоматический пересчет веса составного блюда.

    <expected>Итоговые веса родительского рецепта вычисляются рекурсивно и автоматически обновляются.</expected>
    """
    r1 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 250.0, 240.0)
    r2 = recipe_row_model.create(sample_components["nom_sugar"], sample_components["unit_g"], 100.0, 95.0)
    recipe_dough = receipt_model.create("Тесто", sample_components["nom_dough"], [r1, r2])

    row_dough = recipe_row_model.create(recipe_dough)
    row_box = recipe_row_model.create(sample_components["nom_box"], sample_components["unit_pcs"], 40.0, 40.0)

    recipe_cookies = receipt_model.create(
        name="Печенье в коробке",
        dish=sample_components["nom_cookie"],
        rows=[row_dough, row_box]
    )

    # Рекурсивный расчет
    assert recipe_cookies.gross_weight == 390.0
    assert recipe_cookies.net_weight == 375.0

    # Динамический пересчет через рекурсию при модификации вложенного рецепта
    nom_extra = nomenclature_model.create("Какао", "Какао", sample_components["nom_flour"].group, sample_components["unit_g"])
    r_extra = recipe_row_model.create(nom_extra, sample_components["unit_g"], 50.0, 50.0)
    recipe_dough.add_row(r_extra)

    # Вес теста увеличился до 400/385
    assert recipe_dough.gross_weight == 400.0
    # Вес печенья в коробке рекурсивно обновился до 440/425
    assert recipe_cookies.gross_weight == 440.0
    assert recipe_cookies.net_weight == 425.0


def test_valid_result_receipt_model_add_row_duplicate_rejected(sample_components):
    """
    Проверяет отклонение добавления дублирующейся строки с той же номенклатурой.

    1. Добавить строку с Мукой.
    2. Попытаться повторно добавить строку с Мукой.

    <expected>add_row возвращает False, в рецепте остается ровно 1 строка.</expected>
    """
    recipe = receipt_model()
    recipe.name = "Рецепт"
    recipe.dish = sample_components["nom_dough"]

    r1 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 250.0, 240.0)
    r2 = recipe_row_model.create(sample_components["nom_flour"], sample_components["unit_g"], 50.0, 50.0)

    assert recipe.add_row(r1) is True
    assert recipe.add_row(r2) is False
    assert len(recipe.rows) == 1


def test_valid_result_receipt_model_add_row_self_reference_rejected(sample_components):
    """
    Проверяет защиту от добавления рецепта в самого себя (циклическая зависимость).

    1. Создать рецепт.
    2. Попытаться добавить строку со ссылкой на этот же рецепт.

    <expected>add_row возвращает False.</expected>
    """
    recipe = receipt_model()
    recipe.name = "Рецепт"
    recipe.dish = sample_components["nom_dough"]

    row_self = recipe_row_model.create(recipe)
    assert recipe.add_row(row_self) is False


def test_valid_result_receipt_model_remove_row_absent_returns_false(sample_components):
    """
    Проверяет удаление отсутствующей строки из рецепта.

    1. Попытаться удалить строку, которая не была добавлена в рецепт.

    <expected>remove_row возвращает False.</expected>
    """
    recipe = receipt_model()
    recipe.name = "Рецепт"
    recipe.dish = sample_components["nom_dough"]

    r_absent = recipe_row_model.create(sample_components["nom_sugar"], sample_components["unit_g"], 10.0, 10.0)
    assert recipe.remove_row(r_absent) is False


# =========================================================================
# 3. Тестирование фабричных методов (Factory Method) доменных моделей
# =========================================================================

def test_valid_result_domain_models_factory_methods():
    """
    Проверяет корректность работы фабричных методов во всех доменных моделях.

    1. Вызвать метод create для group_model, range_model (включая create_gram, create_kilogram,
       create_piece, create_milliliter), warehouse_model, nomenclature_model,
       recipe_row_model, receipt_model.
    2. Убедиться, что возвращаются проинициализированные экземпляры с заполненными свойствами.

    <expected>Все созданные фабриками объекты валидны и содержат уникальный код.</expected>
    """
    grp = group_model.create("Сырье")
    assert isinstance(grp, group_model)
    assert grp.name == "Сырье"
    assert grp.unique_code != ""

    rng_g = range_model.create_gram()
    assert rng_g.name == "грамм"
    assert rng_g.conversion_factor == 1.0

    rng_kg = range_model.create_kilogram(rng_g)
    assert rng_kg.name == "килограмм"
    assert rng_kg.base == rng_g
    assert rng_kg.conversion_factor == 1000.0

    rng_pcs = range_model.create_piece()
    assert rng_pcs.name == "штука"

    rng_ml = range_model.create_milliliter()
    assert rng_ml.name == "миллилитр"

    wh = warehouse_model.create("Склад цеха", "г. Москва")
    assert isinstance(wh, warehouse_model)
    assert wh.name == "Склад цеха"
    assert wh.address == "г. Москва"

    nom = nomenclature_model.create("Какао", "Какао-порошок натуральный", grp, rng_g)
    assert isinstance(nom, nomenclature_model)
    assert nom.name == "Какао"
    assert nom.group == grp
    assert nom.range == rng_g

    row = recipe_row_model.create(nom, rng_g, 50.0, 48.0)
    assert isinstance(row, recipe_row_model)
    assert row.gross_weight == 50.0

    rec = receipt_model.create("Рецепт какао", nom, [row], "Горячий напиток")
    assert isinstance(rec, receipt_model)
    assert rec.name == "Рецепт какао"
    assert rec.gross_weight == 50.0
