import pytest
from fastapi.testclient import TestClient

from main import app, _ensure_storage_loaded
from Src.Core.event_type import event_type
from Src.Logics.log_manager import log_manager
from Src.Logics.observer import observer
from Src.Logics.storage_manager import storage_manager
from Src.Models.log_entry_model import log_entry_model


@pytest.fixture(autouse=True)
def setup_log_storage():
    """Сбрасывает лог и хранилище перед каждым тестом лог API."""
    sm = storage_manager()
    sm._groups = []
    sm._ranges = []
    sm._nomenclatures = []
    sm._warehouses = []
    sm._recipes = []
    sm._transactions = []
    sm._log_entries = []
    sm._is_loaded = False
    sm._data = {}

    manager = log_manager()
    manager.set_log_path("logs/app.log")
    observer.clear()
    observer.add(manager)
    manager.clear_log()

    _ensure_storage_loaded()
    yield


@pytest.fixture
def client():
    """Тестовый клиент FastAPI."""
    return TestClient(app)


def test_valid_result_api_log_empty(client):
    """
    Проверяет получение лога без фильтров.

    1. Выполнить POST /api/log без фильтров.

    <expected>Возвращается JSON-массив записей (возможно непустой из-за загрузки данных).</expected>
    """
    response = client.post("/api/log", json={})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert all("period" in item and "subsystem" in item and "level" in item and "message" in item for item in data)


def test_valid_result_api_log_create_and_read(client):
    """
    Проверяет получение лога после CRUD-операции.

    1. Создать группу.
    2. Выполнить POST /api/log.

    <expected>В ответе есть запись с subsystem CRUD и level INFO.</expected>
    """
    client.post("/api/entities/group", json={"name": "API-log группа"})

    response = client.post("/api/log", json={})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["subsystem"] == "CRUD" and item["level"] == "INFO" for item in data)


def test_valid_result_api_log_filter_by_level(client):
    """
    Проверяет фильтрацию лога по уровню.

    1. Создать группу (INFO).
    2. Отфильтровать лог по level = DEBUG.

    <expected>В ответе только записи с уровнем DEBUG.</expected>
    """
    client.post("/api/entities/group", json={"name": "Фильтр группа"})

    response = client.post(
        "/api/log",
        json={"filters": [{"field_name": "level", "filter_type": "EQUALS", "value": "DEBUG"}]},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["level"] == "DEBUG" for item in data)


def test_valid_result_api_log_filter_by_subsystem(client):
    """
    Проверяет фильтрацию лога по подсистеме.

    1. Выполнить GET / (Web DEBUG).
    2. Отфильтровать лог по subsystem = Web.

    <expected>В ответе только записи подсистемы Web.</expected>
    """
    client.get("/")

    response = client.post(
        "/api/log",
        json={"filters": [{"field_name": "subsystem", "filter_type": "EQUALS", "value": "Web"}]},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["subsystem"] == "Web" for item in data)


def test_valid_result_api_log_sort_asc(client):
    """
    Проверяет сортировку лога по возрастанию периода.

    1. Создать две группы с небольшой задержкой.
    2. Запросить лог с order=asc.

    <expected>Первый период меньше или равен последнему.</expected>
    """
    client.post("/api/entities/group", json={"name": "Сортировка 1"})
    client.post("/api/entities/group", json={"name": "Сортировка 2"})

    response = client.post("/api/log?sort_by=period&order=asc", json={})
    assert response.status_code == 200
    data = response.json()
    periods = [item["period"] for item in data]
    assert periods == sorted(periods)


def test_valid_result_api_log_sort_desc(client):
    """
    Проверяет сортировку лога по убыванию периода.

    1. Создать две группы.
    2. Запросить лог с order=desc (по умолчанию).

    <expected>Первый период больше или равен последнему.</expected>
    """
    client.post("/api/entities/group", json={"name": "Сортировка 3"})
    client.post("/api/entities/group", json={"name": "Сортировка 4"})

    response = client.post("/api/log", json={})
    assert response.status_code == 200
    data = response.json()
    periods = [item["period"] for item in data]
    assert periods == sorted(periods, reverse=True)


def test_valid_result_api_log_report_txt(client):
    """
    Проверяет выгрузку лога в формате TXT.

    1. Создать группу.
    2. Выполнить GET /api/log/report/TXT.

    <expected>HTTP 200, content-type text/plain, в теле есть запись CRUD.</expected>
    """
    client.post("/api/entities/group", json={"name": "TXT-отчет группа"})

    response = client.get("/api/log/report/TXT")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "CRUD" in response.text


def test_valid_result_api_log_report_csv(client):
    """
    Проверяет выгрузку лога в формате CSV.

    1. Создать группу.
    2. Выполнить GET /api/log/report/CSV.

    <expected>HTTP 200, content-type text/csv, в теле есть заголовки period/subsystem/level/message.</expected>
    """
    client.post("/api/entities/group", json={"name": "CSV-отчет группа"})

    response = client.get("/api/log/report/CSV")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    text = response.content.decode("utf-8")
    assert "period" in text
    assert "subsystem" in text
    assert "level" in text
    assert "message" in text


def test_valid_result_api_log_report_markdown(client):
    """
    Проверяет выгрузку лога в формате MARKDOWN.

    1. Создать группу.
    2. Выполнить GET /api/log/report/MARKDOWN.

    <expected>HTTP 200, content-type text/markdown, в теле есть запись CRUD.</expected>
    """
    client.post("/api/entities/group", json={"name": "Markdown-отчет группа"})

    response = client.get("/api/log/report/MARKDOWN")
    assert response.status_code == 200
    assert "text/markdown" in response.headers["content-type"]
    assert "CRUD" in response.text


def test_invalid_result_api_log_report_unknown_format(client):
    """
    Проверяет обработку неизвестного формата отчета.

    1. Выполнить GET /api/log/report/XML.

    <expected>HTTP 400 Bad Request.</expected>
    """
    response = client.get("/api/log/report/XML")
    assert response.status_code == 400


def test_valid_result_api_log_error_on_delete_referenced(client):
    """
    Проверяет логирование ERROR при попытке удалить связанную сущность.

    1. Найти связанную сущность (группа 'Ингредиенты').
    2. Попытаться удалить её.
    3. Проверить лог.

    <expected>В логе есть запись уровня ERROR с причиной referenced.</expected>
    """
    from Src.Logics.entity_service import entity_service

    service = entity_service()
    grp = service.find_entity("group", "Ингредиенты")
    assert grp is not None

    manager = log_manager()
    manager.clear_log()

    response = client.delete(f"/api/entities/group/{grp.unique_code}")
    assert response.status_code == 400

    entries = [e for e in manager.entries if e.level == log_manager.LEVEL_ERROR]
    assert len(entries) >= 1
    assert any("referenced" in e.message for e in entries)
