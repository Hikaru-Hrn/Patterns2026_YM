import pytest

from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.report_factory import report_factory
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.settings_model import settings_model


@pytest.mark.parametrize(
    "report_type,expected_class",
    [
        (report_type_enum.TXT, text_report),
        (report_type_enum.CSV, csv_report),
        (report_type_enum.MARKDOWN, markdown_report),
        (report_type_enum.XML, xml_report),
        (report_type_enum.HTML, html_report),
    ],
)
def test_valid_result_report_factory_create_all_types(report_type, expected_class):
    """
    Проверяет создание отчетов для всех поддерживаемых типов report_type_enum.

    1. Вызвать factory.create() для каждого типа перечисления.

    <expected>Возвращается экземпляр соответствующего класса отчета, не None.</expected>
    """
    factory = report_factory()
    report = factory.create(report_type)

    assert report is not None
    assert isinstance(report, abstract_report)
    assert isinstance(report, expected_class)


@pytest.mark.parametrize(
    "format_enum,expected_class",
    [
        (report_type_enum.TXT, text_report),
        (report_type_enum.CSV, csv_report),
        (report_type_enum.MARKDOWN, markdown_report),
        (report_type_enum.XML, xml_report),
        (report_type_enum.HTML, html_report),
    ],
)
def test_valid_result_report_factory_create_default(format_enum, expected_class):
    """
    Проверяет работу метода create_default() в зависимости от настроек.

    1. Создать settings_model с заданным response_format.
    2. Передать настройки в report_factory.
    3. Вызвать factory.create_default().

    <expected>Создается инстанс отчета, соответствующий настройке response_format.</expected>
    """
    settings = settings_model()
    settings.response_format = format_enum

    factory = report_factory(settings=settings)
    report = factory.create_default()

    assert report is not None
    assert isinstance(report, expected_class)


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

    1. Передать в create() некорректный или неподдерживаемый аргумент.

    <expected>arguments_exception</expected>
    """
    factory = report_factory()

    with pytest.raises(arguments_exception) as exc_info:
        factory.create(bad_type)

    assert not isinstance(exc_info.value, (TypeError, KeyError, ValueError))


def test_valid_result_report_factory_build_output_empty_recipe():
    """
    Проверяет выход текстового отчета для рецепта без строк.

    1. Создать пустой рецепт.
    2. Сформировать отчет типа TXT.

    <expected>build() возвращает report_result_dto с заголовком колонок.</expected>
    """
    group = group_model.create("Готовые блюда")
    gram = range_model.create_gram()
    dish = nomenclature_model.create("Блюдо", "Пустое блюдо", group, gram)
    empty_recipe = receipt_model.create(name="Пустой рецепт", dish=dish)

    factory = report_factory()
    report = factory.create(report_type_enum.TXT)

    result = report.build(empty_recipe)

    assert isinstance(result, report_result_dto)
    assert "name: Пустой рецепт" in result.text
