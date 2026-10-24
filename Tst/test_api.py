import pytest
from fastapi.testclient import TestClient

from main import app, _ensure_storage_loaded
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Dtos.report_type_enum import report_type_enum


@pytest.fixture(autouse=True)
def setup_api_storage():
    """Гарантирует загрузку данных перед каждым API тестом."""
    _ensure_storage_loaded()
    yield


@pytest.fixture
def client():
    """Тестовый клиент FastAPI."""
    return TestClient(app)


def test_valid_result_api_root(client):
    """
    Проверяет доступность корневого эндпоинта API.

    1. Выполнить GET запрос к '/'.

    <expected>HTTP статус 200, JSON с приветственным сообщением.</expected>
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_valid_result_api_report_receipt_csv_download(client):
    """
    Проверяет скачивание файла CSV при запросе отчета по рецепту.

    1. Выполнить GET к /api/report/receipt/{recipe_name}?format=CSV.

    <expected>HTTP 200, заголовок Content-Disposition со скачиванием .csv, корректные строки данных.</expected>
    """
    storage = storage_manager()
    recipe = storage.recipes[0]

    response = client.get(f"/api/report/receipt/{recipe.name}?format=CSV")
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")
    assert ".csv" in response.headers.get("content-disposition", "")

    content = response.content.decode("utf-8")
    assert "name" in content
    assert "Мука пшеничная" in content


def test_valid_result_api_report_receipt_markdown_download(client):
    """
    Проверяет скачивание файла Markdown при запросе отчета по рецепту.

    1. Выполнить GET к /api/report/receipt/{recipe_name}?format=Markdown.

    <expected>HTTP 200, заголовок Content-Disposition со скачиванием .md, таблица Markdown.</expected>
    """
    storage = storage_manager()
    recipe = storage.recipes[0]

    response = client.get(f"/api/report/receipt/{recipe.name}?format=Markdown")
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")
    assert ".md" in response.headers.get("content-disposition", "")

    content = response.content.decode("utf-8")
    assert "| name |" in content
    assert "Мука пшеничная" in content


def test_valid_result_api_report_nomenclature_xml(client):
    """
    Проверяет получение структурированного XML-отчета по номенклатуре.

    1. Выполнить GET к /api/report/nomenclature/{nom_name}?format=XML.

    <expected>HTTP 200, media_type application/xml, тег nomenclature в теле ответа.</expected>
    """
    storage = storage_manager()
    nom = storage.nomenclatures[0]

    response = client.get(f"/api/report/nomenclature/{nom.name}?format=XML")
    assert response.status_code == 200
    assert "xml" in response.headers.get("content-type", "")
    assert f"<name>{nom.name}</name>" in response.text


def test_valid_result_api_report_range_html(client):
    """
    Проверяет получение структурированного HTML-отчета по единице измерения.

    1. Выполнить GET к /api/report/range/{unit_name}?format=HTML.

    <expected>HTTP 200, media_type text/html, разметка таблицы.</expected>
    """
    storage = storage_manager()
    unit = storage.ranges[0]

    response = client.get(f"/api/report/range/{unit.name}?format=HTML")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "")
    assert f"<td>{unit.name}</td>" in response.text


def test_valid_result_api_report_default_endpoint(client):
    """
    Проверяет работу эндпоинта отчета по умолчанию (create_default).

    1. Установить в настройках response_format = TXT.
    2. Выполнить GET к /api/report/default/nomenclature/{nom_name}.

    <expected>HTTP 200, формат ответа соответствует настройкам (text/plain).</expected>
    """
    mgr = settings_manager()
    mgr.settings.response_format = report_type_enum.TXT

    storage = storage_manager()
    nom = storage.nomenclatures[0]

    response = client.get(f"/api/report/default/nomenclature/{nom.name}")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    assert f"name: {nom.name}" in response.text


def test_invalid_result_api_report_nonexistent_entity(client):
    """
    Проверяет обработку запроса для несуществующей сущности.

    1. Запросить отчет для сущности с неизвестным кодом.

    <expected>HTTP статус 404 Not Found.</expected>
    """
    response = client.get("/api/report/nomenclature/несуществующий_код_12345")
    assert response.status_code == 404


def test_invalid_result_api_report_unsupported_format(client):
    """
    Проверяет обработку запроса с неподдерживаемым форматом отчета.

    1. Передать format=PDF_UNKNOWN.

    <expected>HTTP статус 400 Bad Request.</expected>
    """
    storage = storage_manager()
    nom = storage.nomenclatures[0]

    response = client.get(f"/api/report/nomenclature/{nom.name}?format=PDF_UNKNOWN")
    assert response.status_code == 400
