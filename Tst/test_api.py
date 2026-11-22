import pytest
from fastapi.testclient import TestClient

from main import app, _ensure_storage_loaded
from Src.Logics.entity_service import entity_service
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Dtos.report_type_enum import report_type_enum


@pytest.fixture(autouse=True)
def setup_api_storage():
    """Сбрасывает и заново загружает данные перед каждым API тестом."""
    sm = storage_manager()
    sm._groups = []
    sm._ranges = []
    sm._nomenclatures = []
    sm._warehouses = []
    sm._recipes = []
    sm._is_loaded = False
    sm._data = {}
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


# =========================================================================
# Интеграционные тесты Swagger / OpenAPI и списка форматов отчетов
# =========================================================================


def test_valid_result_api_swagger_and_openapi_yaml(client):
    """
    Проверяет доступность Swagger UI (/docs) и спецификации OpenAPI (/openapi.json) из openapi.yaml.

    1. Выполнить GET к /docs и /openapi.json.
    2. Проверить наличие описанных маршрутов в схеме OpenAPI.

    <expected>HTTP 200, схема содержит /api/report/formats и /api/entities/{entity_type}.</expected>
    """
    docs_response = client.get("/docs")
    assert docs_response.status_code == 200

    schema_response = client.get("/openapi.json")
    assert schema_response.status_code == 200
    schema = schema_response.json()
    assert schema["openapi"] == "3.0.0"
    assert "/api/report/formats" in schema["paths"]
    assert "/api/entities/{entity_type}" in schema["paths"]
    assert "/api/entities/{entity_type}/{unique_code}" in schema["paths"]


def test_valid_result_api_get_report_formats(client):
    """
    Проверяет получение списка всех форматов для построения отчетов (GET / JSON).

    1. Выполнить GET к /api/report/formats.

    <expected>HTTP 200, JSON-массив со всеми форматами report_type_enum.</expected>
    """
    response = client.get("/api/report/formats")
    assert response.status_code == 200
    formats = response.json()
    assert isinstance(formats, list)
    assert formats == ["TXT", "CSV", "MARKDOWN", "XML", "HTML"]


# =========================================================================
# Интеграционные тесты CRUD операций для доменных сущностей
# =========================================================================


def test_valid_result_api_crud_group_full_cycle(client):
    """
    Проверяет полный цикл CRUD (Create, Read, Update, Delete) для несвязанной группы номенклатуры.

    1. Создать новую группу POST /api/entities/group.
    2. Прочитать созданную группу GET /api/entities/group/{code}.
    3. Изменить имя и unique_code несвязанной группы PUT /api/entities/group/{code}.
    4. Удалить группу DELETE /api/entities/group/{new_code}.
    5. Убедиться, что повторный GET возвращает 404.

    <expected>Все этапы CRUD выполняются успешно (201 -> 200 -> 200 -> 200 -> 404).</expected>
    """
    # 1. Create
    create_resp = client.post("/api/entities/group", json={"name": "Напитки"})
    assert create_resp.status_code == 201
    created = create_resp.json()
    code = created["unique_code"]
    assert created["name"] == "Напитки"

    # 2. Read
    get_resp = client.get(f"/api/entities/group/{code}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Напитки"

    # 3. Update (включая смену кода у несвязанной сущности)
    new_code = "custom-group-code-001"
    update_resp = client.put(
        f"/api/entities/group/{code}",
        json={"unique_code": new_code, "name": "Холодные напитки"},
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["unique_code"] == new_code
    assert updated["name"] == "Холодные напитки"

    # 4. Delete
    delete_resp = client.delete(f"/api/entities/group/{new_code}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "deleted"

    # 5. Verify deleted
    assert client.get(f"/api/entities/group/{new_code}").status_code == 404


def test_valid_result_api_crud_warehouse_full_cycle(client):
    """
    Проверяет полный цикл CRUD для склада (warehouse_model).

    1. Создать склад через POST /api/entities/warehouse.
    2. Обновить адрес склада через PATCH /api/entities/warehouse/{code}.
    3. Удалить склад через DELETE /api/entities/warehouse/{code}.

    <expected>Склад создается, обновляется и удаляется без ошибок.</expected>
    """
    create_resp = client.post(
        "/api/entities/warehouse",
        json={"name": "Резервный склад", "address": "г. Москва, ул. Новая, 10"},
    )
    assert create_resp.status_code == 201
    code = create_resp.json()["unique_code"]

    patch_resp = client.patch(
        f"/api/entities/warehouse/{code}",
        json={"address": "г. Москва, ул. Новая, 25"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["address"] == "г. Москва, ул. Новая, 25"

    del_resp = client.delete(f"/api/entities/warehouse/{code}")
    assert del_resp.status_code == 200


def test_valid_result_api_crud_nomenclature_and_range(client):
    """
    Проверяет создание, обновление и удаление связанных между собой новых сущностей в правильном порядке.

    1. Создать новую единицу измерения 'литр' с базовой единицей 'миллилитр'.
    2. Создать новую номенклатуру 'Молоко', ссылающуюся на группу 'Ингредиенты' и единицу 'литр'.
    3. Попытаться удалить 'литр', пока на него ссылается 'Молоко' (ожидается 400).
    4. Удалить 'Молоко' (200), затем удалить 'литр' (200).

    <expected>Связи разрешаются из хранилища; удаление блокируется при наличии ссылки и разрешается после её снятия.</expected>
    """
    create_range = client.post(
        "/api/entities/range",
        json={
            "name": "литр",
            "conversion_factor": 1000.0,
            "base": {"name": "миллилитр"},
        },
    )
    assert create_range.status_code == 201
    liter_code = create_range.json()["unique_code"]

    create_nom = client.post(
        "/api/entities/nomenclature",
        json={
            "name": "Молоко",
            "full_name": "Молоко пастеризованное 3.2%",
            "group": {"name": "Ингредиенты"},
            "range": {"unique_code": liter_code},
        },
    )
    assert create_nom.status_code == 201
    milk_code = create_nom.json()["unique_code"]

    # Пока 'Молоко' ссылается на 'литр', удалить 'литр' нельзя
    blocked_del = client.delete(f"/api/entities/range/{liter_code}")
    assert blocked_del.status_code == 400

    # Удаляем сначала 'Молоко', затем 'литр'
    assert client.delete(f"/api/entities/nomenclature/{milk_code}").status_code == 200
    assert client.delete(f"/api/entities/range/{liter_code}").status_code == 200


def test_invalid_result_api_delete_referenced_entities_blocked(client):
    """
    Проверяет запрет удаления доменных сущностей, связанных с другими сущностями.

    1. Попытаться удалить группу 'Ингредиенты' (используется в номенклатуре).
    2. Попытаться удалить единицу измерения 'грамм' (используется как base в 'килограмм' и в номенклатуре).
    3. Попытаться удалить номенклатуру 'Мука пшеничная' (используется в рецепте).
    4. Попытаться удалить рецепт 'Песочное тесто' (используется как sub_recipe во втором рецепте).

    <expected>Для всех 4 запросов возвращается HTTP 400 Bad Request, сущности остаются в хранилище.</expected>
    """
    service = entity_service()
    grp = service.find_entity("group", "Ингредиенты")
    gram = service.find_entity("range", "грамм")
    flour = service.find_entity("nomenclature", "Мука пшеничная")
    dough = service.find_entity("receipt", "Песочное тесто")

    assert client.delete(f"/api/entities/group/{grp.unique_code}").status_code == 400
    assert client.delete(f"/api/entities/range/{gram.unique_code}").status_code == 400
    assert client.delete(f"/api/entities/nomenclature/{flour.unique_code}").status_code == 400
    assert client.delete(f"/api/entities/receipt/{dough.unique_code}").status_code == 400


def test_invalid_result_api_update_code_of_referenced_entities_blocked(client):
    """
    Проверяет запрет изменения уникального кода (unique_code) у сущностей, связанных с другими сущностями.

    1. Попытаться изменить unique_code у группы 'Ингредиенты'.
    2. Попытаться изменить unique_code у единицы измерения 'грамм'.
    3. Попытаться изменить unique_code у номенклатуры 'Мука пшеничная'.
    4. Попытаться изменить unique_code у вложенного рецепта 'Песочное тесто'.

    <expected>HTTP 400 Bad Request во всех случаях, исходные unique_code не изменились.</expected>
    """
    service = entity_service()
    grp = service.find_entity("group", "Ингредиенты")
    gram = service.find_entity("range", "грамм")
    flour = service.find_entity("nomenclature", "Мука пшеничная")
    dough = service.find_entity("receipt", "Песочное тесто")

    assert (
        client.put(
            f"/api/entities/group/{grp.unique_code}",
            json={"unique_code": "new-grp-code"},
        ).status_code
        == 400
    )
    assert (
        client.put(
            f"/api/entities/range/{gram.unique_code}",
            json={"unique_code": "new-gram-code"},
        ).status_code
        == 400
    )
    assert (
        client.put(
            f"/api/entities/nomenclature/{flour.unique_code}",
            json={"unique_code": "new-flour-code"},
        ).status_code
        == 400
    )
    assert (
        client.put(
            f"/api/entities/receipt/{dough.unique_code}",
            json={"unique_code": "new-dough-code"},
        ).status_code
        == 400
    )


def test_invalid_result_api_crud_validation_errors(client):
    """
    Проверяет валидацию при добавлении и изменении доменных сущностей через API.

    1. Попытаться создать дубликат существующей группы 'Ингредиенты'.
    2. Попытаться создать единицу измерения с отрицательным коэффициентом пересчета.
    3. Попытаться создать номенклатуру со ссылкой на несуществующую группу.

    <expected>Во всех случаях возвращается HTTP 400 Bad Request.</expected>
    """
    # Дубликат группы
    assert client.post("/api/entities/group", json={"name": "Ингредиенты"}).status_code == 400

    # Некорректный коэффициент пересчета
    assert (
        client.post(
            "/api/entities/range",
            json={"name": "тонна", "conversion_factor": -10.0},
        ).status_code
        == 400
    )

    # Несуществующая связанная группа
    assert (
        client.post(
            "/api/entities/nomenclature",
            json={
                "name": "Какао",
                "full_name": "Какао-порошок",
                "group": {"unique_code": "unknown-group-code"},
                "range": {"name": "грамм"},
            },
        ).status_code
        == 400
    )
