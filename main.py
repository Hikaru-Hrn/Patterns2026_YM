import uvicorn
from fastapi import FastAPI, HTTPException, Query, status

from Src.Core.exception import base_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager

app = FastAPI(
    title="API системы управления сетью ресторанов 'Ромашка'",
    description="Формирование отчетов по технологическим картам, номенклатуре и единицам измерения",
    version="1.0.0",
)

# Путь к файлу настроек (по умолчанию settings.json в корне проекта)
SETTINGS_FILE = "settings.json"


def _ensure_storage_loaded() -> None:
    """Гарантирует, что справочники и рецепты загружены в память.

    При первом обращении читает settings.json и формирует первичные данные
    через storage_manager. Повторные вызовы ничего не делают.
    """
    storage = storage_manager()
    if len(storage.recipes) > 0 and len(storage.nomenclatures) > 0:
        return

    mgr = settings_manager()
    if not mgr.is_loaded:
        mgr.load(SETTINGS_FILE)

    mgr.settings.first_launch_flag = True
    storage.first_start(SETTINGS_FILE)


@app.get("/")
@app.post("/")
async def root():
    return {"message": "Система учета сети ресторанов 'Ромашка'"}


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
    description="Формирует отчет для указанного типа сущности (номенклатура, единица измерения, рецепт) и кода в заданном формате.",
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
    description="Формирует отчет для указанного типа сущности и кода, используя формат по умолчанию из настроек (create_default).",
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
