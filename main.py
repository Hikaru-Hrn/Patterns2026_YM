from pathlib import Path
from typing import Any
import uvicorn
import yaml
from fastapi import Body, FastAPI, HTTPException, Query, status

from Src.Core.exception import base_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.convert_factory import convert_factory
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager

BASE_DIR = Path(__file__).resolve().parent
OPENAPI_FILE = BASE_DIR / "openapi.yaml"
SETTINGS_FILE = (
    str(BASE_DIR / "settings.json")
    if (BASE_DIR / "settings.json").exists()
    else str(BASE_DIR / "Tst" / "settings.json")
)

app = FastAPI(
    title="API системы управления сетью ресторанов 'Ромашка'",
    description="Формирование отчетов и CRUD-операции по доменным сущностям",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)


def custom_openapi() -> dict:
    """Загружает спецификацию Swagger / OpenAPI напрямую из файла openapi.yaml."""
    if app.openapi_schema:
        return app.openapi_schema
    with open(OPENAPI_FILE, "r", encoding="utf-8") as file:
        app.openapi_schema = yaml.safe_load(file)
    return app.openapi_schema


app.openapi = custom_openapi


def _ensure_storage_loaded() -> None:
    """Гарантирует, что справочники и рецепты загружены в память.

    При первом обращении читает settings.json и формирует первичные данные
    через storage_manager. Повторные вызовы ничего не делают.
    """
    storage = storage_manager()
    if storage.is_loaded:
        return

    mgr = settings_manager()
    if not mgr.is_loaded:
        mgr.load(SETTINGS_FILE)

    mgr.settings.first_launch_flag = True
    storage.first_start(SETTINGS_FILE)


@app.get("/")
@app.post("/")
async def root():
    """Корневой эндпоинт проверки работоспособности сервиса."""
    return {"message": "Система учета сети ресторанов 'Ромашка'"}


@app.get(
    "/api/report/formats",
    summary="Получить список всех форматов для построения отчетов",
    tags=["Отчеты"],
    status_code=status.HTTP_200_OK,
)
def get_report_formats() -> list[str]:
    """Возвращает JSON-список всех поддерживаемых форматов построения отчетов."""
    return [item.name for item in report_type_enum]


@app.get(
    "/api/get_report",
    summary="Получить текстовый отчет по рецепту (устаревший эндпоинт)",
    tags=["Отчеты"],
    status_code=status.HTTP_200_OK,
)
def get_report(recipe_name: str = ""):
    """Формирует текстовый отчет по технологической карте."""
    _ensure_storage_loaded()
    storage = storage_manager()

    if len(storage.recipes) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Справочники не загружены",
        )

    if recipe_name:
        recipe = storage._find_recipe_by_name(recipe_name)
        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рецепт '{recipe_name}' не найден",
            )
    else:
        recipe = storage.recipes[0]

    report_type = report_type_enum.TXT
    try:
        factory = report_factory()
        report = factory.create(report_type)
        result = report.build(recipe)
    except base_exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )

    return {
        "recipe": recipe.name,
        "report_type": report_type.name,
        "text": result.text,
    }


@app.get(
    "/api/report/{entity_type}/{unique_code}",
    summary="Сформировать отчет в указанном формате",
    description="Формирует отчет для указанного типа сущности и кода в заданном формате.",
    tags=["Отчеты"],
    status_code=status.HTTP_200_OK,
)
def get_entity_report(
    entity_type: str,
    unique_code: str,
    format: str = Query("TXT", description="Формат отчета: CSV, Markdown, XML, TXT, HTML"),
):
    """Формирует отчет в указанном формате с полиморфным созданием ответа."""
    _ensure_storage_loaded()
    storage = storage_manager()

    try:
        entity = storage.find_entity(entity_type, unique_code)
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сущность типа '{entity_type}' с кодом '{unique_code}' не найдена",
        )

    try:
        rep_type = report_type_enum.from_string(format)
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    try:
        factory = report_factory()
        report = factory.create(rep_type)
        result = report.build(entity)
        return report.create_response(result, f"report_{entity_type}_{unique_code}")
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@app.get(
    "/api/report/default/{entity_type}/{unique_code}",
    summary="Сформировать отчет с форматом по умолчанию (create_default)",
    description="Формирует отчет для указанного типа сущности и кода, используя формат по умолчанию из настроек.",
    tags=["Отчеты"],
    status_code=status.HTTP_200_OK,
)
def get_entity_report_default(
    entity_type: str,
    unique_code: str,
):
    """Формирует отчет с использованием метода create_default() фабрики отчетов."""
    _ensure_storage_loaded()
    storage = storage_manager()

    try:
        entity = storage.find_entity(entity_type, unique_code)
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сущность типа '{entity_type}' с кодом '{unique_code}' не найдена",
        )

    try:
        factory = report_factory()
        report = factory.create_default()
        result = report.build(entity)
        return report.create_response(result, f"default_report_{entity_type}_{unique_code}")
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@app.get(
    "/api/entities/{entity_type}",
    summary="Получить список доменных сущностей указанного типа",
    tags=["Доменные сущности (CRUD)"],
    status_code=status.HTTP_200_OK,
)
def list_entities(entity_type: str):
    """Возвращает JSON-список всех сущностей выбранного типа."""
    _ensure_storage_loaded()
    storage = storage_manager()
    try:
        items = storage.get_collection(entity_type)
        return convert_factory().Convert(items)
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@app.get(
    "/api/entities/{entity_type}/{unique_code}",
    summary="Получить доменную сущность по коду или наименованию",
    tags=["Доменные сущности (CRUD)"],
    status_code=status.HTTP_200_OK,
)
def get_entity(entity_type: str, unique_code: str):
    """Возвращает одну доменную сущность в формате JSON."""
    _ensure_storage_loaded()
    storage = storage_manager()
    try:
        entity = storage.find_entity(entity_type, unique_code)
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сущность типа '{entity_type}' с кодом '{unique_code}' не найдена",
        )
    return convert_factory().Convert(entity)


@app.post(
    "/api/entities/{entity_type}",
    summary="Создать новую доменную сущность",
    tags=["Доменные сущности (CRUD)"],
    status_code=status.HTTP_201_CREATED,
)
def create_entity(entity_type: str, payload: dict[str, Any] = Body(...)):
    """Создает доменную сущность из JSON с проверкой корректности и уникальности."""
    _ensure_storage_loaded()
    storage = storage_manager()
    try:
        created = storage.create_entity(entity_type, payload)
        return convert_factory().Convert(created)
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@app.put(
    "/api/entities/{entity_type}/{unique_code}",
    summary="Изменить доменную сущность",
    tags=["Доменные сущности (CRUD)"],
    status_code=status.HTTP_200_OK,
)
@app.patch(
    "/api/entities/{entity_type}/{unique_code}",
    summary="Частично изменить доменную сущность",
    tags=["Доменные сущности (CRUD)"],
    status_code=status.HTTP_200_OK,
)
def update_entity(entity_type: str, unique_code: str, payload: dict[str, Any] = Body(...)):
    """Обновляет доменную сущность. Запрещает менять код, если сущность связана с другой."""
    _ensure_storage_loaded()
    storage = storage_manager()
    try:
        updated = storage.update_entity(entity_type, unique_code, payload)
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сущность типа '{entity_type}' с кодом '{unique_code}' не найдена",
        )
    return convert_factory().Convert(updated)


@app.delete(
    "/api/entities/{entity_type}/{unique_code}",
    summary="Удалить доменную сущность",
    tags=["Доменные сущности (CRUD)"],
    status_code=status.HTTP_200_OK,
)
def delete_entity(entity_type: str, unique_code: str):
    """Удаляет доменную сущность. Запрещает удаление, если сущность связана с другой."""
    _ensure_storage_loaded()
    storage = storage_manager()
    try:
        deleted = storage.delete_entity(entity_type, unique_code)
    except base_exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сущность типа '{entity_type}' с кодом '{unique_code}' не найдена",
        )
    return {"status": "deleted", "unique_code": unique_code}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
