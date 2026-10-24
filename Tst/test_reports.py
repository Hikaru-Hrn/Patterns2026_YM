import pytest

from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import recipe_row_model


@pytest.fixture
def sample_data():
    """Создает тестовые сущности: единицу измерения, номенклатуру и рецепт."""
    grp = group_model.create("Ингредиенты")
    gram = range_model.create_gram()
    flour = nomenclature_model.create("Мука", "Мука пшеничная в/с", grp, gram)
    sugar = nomenclature_model.create("Сахар", "Сахар белый", grp, gram)

    dish = nomenclature_model.create("Печенье", "Печенье домашнее", grp, gram)
    r1 = recipe_row_model.create(flour, gram, 200.0, 200.0)
    r2 = recipe_row_model.create(sugar, gram, 100.0, 95.0)

    recipe = receipt_model.create(
        name="Печенье домашнее",
        dish=dish,
        rows=[r1, r2],
        comments="Классический рецепт"
    )

    return {
        "range": gram,
        "nomenclature": flour,
        "recipe": recipe,
    }


# =========================================================================
# 1. Тестирование csv_report
# =========================================================================

def test_valid_result_csv_report_build_receipt(sample_data):
    """
    Проверяет формирование CSV отчета по рецепту и наличие бинарных данных.

    1. Вызвать csv_report().build() с экземпляром receipt_model.

    <expected>Сформированы бинарные данные, декодированный текст содержит заголовок и строки с разделителем ';'.</expected>
    """
    report = csv_report()
    res = report.build(sample_data["recipe"])

    assert isinstance(res, report_result_dto)
    assert len(res.binary) > 0

    text = bytes(res.binary).decode("utf-8")
    assert "name" in text
    assert "Мука" in text
    assert "Сахар" in text


def test_valid_result_csv_report_build_nomenclature(sample_data):
    """
    Проверяет формирование CSV отчета по номенклатуре.

    1. Вызвать csv_report().build() с экземпляром nomenclature_model.

    <expected>Содержит колонки номенклатуры и корректные значения.</expected>
    """
    report = csv_report()
    res = report.build(sample_data["nomenclature"])

    text = bytes(res.binary).decode("utf-8")
    assert "name" in text
    assert "Мука" in text
    assert "Ингредиенты" in text


def test_valid_result_csv_report_build_range(sample_data):
    """
    Проверяет формирование CSV отчета по единице измерения.

    1. Вызвать csv_report().build() с экземпляром range_model.

    <expected>Содержит колонки единицы измерения и коэффициент.</expected>
    """
    report = csv_report()
    res = report.build(sample_data["range"])

    text = bytes(res.binary).decode("utf-8")
    assert "name" in text
    assert "грамм" in text
    assert "1.0" in text


# =========================================================================
# 2. Тестирование markdown_report
# =========================================================================

def test_valid_result_markdown_report_build_receipt(sample_data):
    """
    Проверяет формирование Markdown отчета по рецепту и наличие бинарных данных.

    1. Вызвать markdown_report().build() с экземпляром receipt_model.

    <expected>Сформированы бинарные данные, текст содержит разметку Markdown-таблицы.</expected>
    """
    report = markdown_report()
    res = report.build(sample_data["recipe"])

    assert isinstance(res, report_result_dto)
    assert len(res.binary) > 0

    text = bytes(res.binary).decode("utf-8")
    assert "| name |" in text
    assert "Мука" in text
    assert "Сахар" in text


def test_valid_result_markdown_report_build_nomenclature(sample_data):
    """
    Проверяет формирование Markdown отчета по номенклатуре.

    1. Вызвать markdown_report().build() с экземпляром nomenclature_model.

    <expected>Содержит таблицу с полями номенклатуры.</expected>
    """
    report = markdown_report()
    res = report.build(sample_data["nomenclature"])

    text = bytes(res.binary).decode("utf-8")
    assert "| Поле | Значение |" in text
    assert "| name | Мука |" in text
    assert "| group | Ингредиенты |" in text


def test_valid_result_markdown_report_build_range(sample_data):
    """
    Проверяет формирование Markdown отчета по единице измерения.

    1. Вызвать markdown_report().build() с экземпляром range_model.

    <expected>Содержит таблицу с параметрами единицы измерения.</expected>
    """
    report = markdown_report()
    res = report.build(sample_data["range"])

    text = bytes(res.binary).decode("utf-8")
    assert "| Поле | Значение |" in text
    assert "| name | грамм |" in text
    assert "| conversion_factor | 1.0 |" in text


# =========================================================================
# 3. Тестирование xml_report
# =========================================================================

def test_valid_result_xml_report_build_receipt(sample_data):
    """
    Проверяет формирование структурированного XML-отчета по рецепту.

    1. Вызвать xml_report().build() с экземпляром receipt_model.

    <expected>Сформирован валидный XML с тегами receipt, items, item, gross_weight, net_weight.</expected>
    """
    report = xml_report()
    res = report.build(sample_data["recipe"])

    assert isinstance(res, report_result_dto)
    assert len(res.text) > 0
    assert "<?xml version=\"1.0\" encoding=\"utf-8\"?>" in res.text
    assert "<receipt" in res.text
    assert "<gross_weight>300.0</gross_weight>" in res.text
    assert "<net_weight>295.0</net_weight>" in res.text
    assert "<name>Мука</name>" in res.text


def test_valid_result_xml_report_build_nomenclature(sample_data):
    """
    Проверяет формирование XML-отчета по номенклатуре.

    1. Вызвать xml_report().build() с экземпляром nomenclature_model.

    <expected>XML содержит тег nomenclature с полями name, full_name, group, range.</expected>
    """
    report = xml_report()
    res = report.build(sample_data["nomenclature"])

    assert "<nomenclature" in res.text
    assert "<name>Мука</name>" in res.text
    assert "<group>Ингредиенты</group>" in res.text


def test_valid_result_xml_report_build_range(sample_data):
    """
    Проверяет формирование XML-отчета по единице измерения.

    1. Вызвать xml_report().build() с экземпляром range_model.

    <expected>XML содержит тег range с коэффициентом и базовой единицей.</expected>
    """
    report = xml_report()
    res = report.build(sample_data["range"])

    assert "<range" in res.text
    assert "<name>грамм</name>" in res.text
    assert "<conversion_factor>1.0</conversion_factor>" in res.text


# =========================================================================
# 4. Тестирование html_report
# =========================================================================

def test_valid_result_html_report_build_receipt(sample_data):
    """
    Проверяет формирование HTML-отчета по рецепту.

    1. Вызвать html_report().build() с экземпляром receipt_model.

    <expected>HTML содержит структуру таблицы table, thead, tbody.</expected>
    """
    report = html_report()
    res = report.build(sample_data["recipe"])

    assert "<table" in res.text
    assert "<th>name</th>" in res.text
    assert "<td>Мука</td>" in res.text


def test_valid_result_html_report_build_nomenclature(sample_data):
    """
    Проверяет формирование HTML-отчета по номенклатуре.

    1. Вызвать html_report().build() с экземпляром nomenclature_model.

    <expected>HTML содержит таблицу с реквизитами номенклатуры.</expected>
    """
    report = html_report()
    res = report.build(sample_data["nomenclature"])

    assert "<table" in res.text
    assert "<td>Мука</td>" in res.text
    assert "<td>Ингредиенты</td>" in res.text


def test_valid_result_html_report_build_range(sample_data):
    """
    Проверяет формирование HTML-отчета по единице измерения.

    1. Вызвать html_report().build() с экземпляром range_model.

    <expected>HTML содержит таблицу со свойствами единицы измерения.</expected>
    """
    report = html_report()
    res = report.build(sample_data["range"])

    assert "<table" in res.text
    assert "<td>грамм</td>" in res.text
    assert "<td>1.0</td>" in res.text


# =========================================================================
# 5. Тестирование text_report и обработка некорректных источников
# =========================================================================

def test_valid_result_text_report_build_nomenclature_and_range(sample_data):
    """
    Проверяет формирование текстового отчета по номенклатуре и единице измерения.

    1. Вызвать text_report().build() для номенклатуры и единицы измерения.

    <expected>Текстовый отчет содержит наименования и реквизиты.</expected>
    """
    report = text_report()

    res_nom = report.build(sample_data["nomenclature"])
    assert "name: Мука" in res_nom.text
    assert "group: Ингредиенты" in res_nom.text

    res_rng = report.build(sample_data["range"])
    assert "name: грамм" in res_rng.text
    assert "conversion_factor: 1.0" in res_rng.text


@pytest.mark.parametrize("report_cls", [text_report, csv_report, markdown_report, xml_report, html_report])
def test_invalid_result_reports_build_unsupported_source(report_cls):
    """
    Проверяет реакцию отчетов на неподдерживаемый тип источника данных.

    1. Передать в build() неподходящий объект (например строку или число).

    <expected>arguments_exception</expected>
    """
    report = report_cls()
    with pytest.raises(arguments_exception):
        report.build("неподдерживаемый_источник")
