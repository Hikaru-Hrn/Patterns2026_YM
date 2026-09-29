from Src.Models.range_model import range_model


def test_valid_result_range_model_demo_gram_and_kg():
    """
    Проверяет демонстрационный сценарий пересчёта единиц
    измерения: 1 кг = 1000 грамм.

    Ожидаемый результат:
    базовая единица 'грамм' имеет base = None и коэффициент 1,
    производная 'кг' ссылается на грамм и имеет коэффициент 1000.
    """
    base_range = range_model("грамм", 1)
    assert base_range.conversion_factor == 1
    assert base_range.base is None

    kg_range = range_model("кг", 1000, base_range)
    assert kg_range.conversion_factor == 1000
    assert kg_range.base is base_range
    assert kg_range.base.name == "грамм"

    quantity_kg = 2.5
    quantity_g = quantity_kg * kg_range.conversion_factor
    assert quantity_g == 2500