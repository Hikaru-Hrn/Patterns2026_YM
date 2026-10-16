import uvicorn
from fastapi import FastAPI, HTTPException, status

from Src.Core.exception import base_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager

app = FastAPI()

# Путь к файлу настроек (по умолчанию settings.json в корне проекта)
SETTINGS_FILE = "settings.json"


def _ensure_storage_loaded() -> None:
    """Гарантирует, что справочники и рецепты загружены в память.

    При первом обращении читает settings.json и формирует первичные данные
    (рецепты, номенклатуру, единицы измерения) через storage_manager.
    Повторные вызовы ничего не делают.
    """
    storage = storage_manager()
    if len(storage.recipes) > 0:
        return

    mgr = settings_manager()
    if not mgr.is_loaded:
        mgr.load(SETTINGS_FILE)

    # Форсируем первичное наполнение, чтобы данные были доступны
    # независимо от текущего значения флага первого старта.
    mgr.settings.first_launch_flag = True
    storage.first_start(SETTINGS_FILE)


@app.post("/")
async def main():
    return "Hello, world"


@app.get(
    "/api/get_report",
    summary="Получить отчет",
    description="Эндпоинт возвращает статус формирования отчета",
    tags=["Отчеты"],
    status_code=status.HTTP_200_OK,
)
def get_report(recipe_name: str = ""):
    """Формирует текстовый отчет по технологической карте.

    :param recipe_name: Наименование рецепта. Если не задано — берется первый
        доступный рецепт из хранилища.
    :return: Словарь с наименованием рецепта, типом отчета и текстом отчета.
    :raises HTTPException: 404 — рецепт не найден, 500 — данные не загружены,
        400 — доменная ошибка при формировании отчета.
    """
    # Данные должны быть загружены
    _ensure_storage_loaded()

    storage = storage_manager()
    if len(storage.recipes) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Справочники не загружены",
        )

    # Выбираем рецепт: по имени либо первый доступный
    if recipe_name:
        recipe = storage._find_recipe_by_name(recipe_name)
        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Рецепт '{recipe_name}' не найден",
            )
    else:
        recipe = storage.recipes[0]

    # Создаем отчет через фабрику и формируем его выход
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

    # Возвращаем результат формирования
    return {
        "recipe": recipe.name,
        "report_type": report_type.name,
        "text": result.text,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
