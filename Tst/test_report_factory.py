import pytest

from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.text_report import text_report
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model

# Правильный тип
def test_valid_result_report_factory_create_txt():
    """
    Проверяет создание отчета для поддерживаемого типа report_type_enum.TXT.

    Ожидаемый результат:
    create() возвращает экземпляр abstract_report (text_report), не None.
    """
    factory = report_factory()
    report = factory.create(report_type_enum.TXT)

    assert report is not None
    assert isinstance(report, abstract_report)
    assert isinstance(report, text_report)




# Неправильный тип
@pytest.mark.parametrize(
    "bad_type",
    [
        None,
        "TXT",
        1,
        "pdf",
        object(),
    ],
)
def test_invalid_result_report_factory_unknown_type(bad_type):
    """
    Проверяет реакцию create() на неподдерживаемый тип отчета.

    Ожидаемый результат:
    возбуждается arguments_exception (доменная ошибка), а не встроенное
    исключение (TypeError, KeyError и т.п.).
    """
    factory = report_factory()

    with pytest.raises(arguments_exception) as exc_info:
        factory.create(bad_type)

    assert not isinstance(exc_info.value, (TypeError, KeyError, ValueError))



# Выход
def test_valid_result_report_factory_build_output_empty_recipe():
    """
    Проверяет выход отчета для рецепта без строк.

    Ожидаемый результат:
    build() возвращает report_result_dto с заголовком и без данных.
    """
    group = group_model.create("Готовые блюда")
    gram = range_model.create_gram()
    dish = nomenclature_model.create("Блюдо", "Пустое блюдо", group, gram)
    empty_recipe = receipt_model.create(name="Пустой рецепт", dish=dish)

    factory = report_factory()
    report = factory.create(report_type_enum.TXT)

    result = report.build(empty_recipe)

    assert isinstance(result, report_result_dto)
    assert "Код | Наименование | Брутто | Нетто" in result.text
