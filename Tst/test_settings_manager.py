import pytest

from pathlib import Path
from Src.Logics.settings_manager import settings_manager
from Src.Core.exception import arguments_exception


def _settings_path() -> str:
    """Путь к settings.json в папке Tst (рядом с тестом)."""
    return str(Path(__file__).resolve().parent / "settings.json")


# ---------- Singleton ----------

def test_valid_result_settings_manager_singleton():
    """
    Проверяет работу шаблона Singleton.

    Ожидаемый результат:
    два вызова settings_manager() возвращают один и тот же объект.
    """
    instance1 = settings_manager()
    instance2 = settings_manager()
    assert instance1 is instance2


def test_valid_result_settings_manager_same_settings():
    """
    Проверяет, что все экземпляры Singleton ссылаются на
    один и тот же settings_model.

    Ожидаемый результат:
    instance1.settings и instance2.settings — один объект.
    """
    instance1 = settings_manager()
    instance2 = settings_manager()
    assert instance1.settings is instance2.settings


# ---------- Загрузка ----------

def test_valid_result_settings_manager_load_success():
    """
    Проверяет успешную загрузку настроек из JSON.

    Ожидаемый результат:
    после load() settings не равен None.
    """
    manager = settings_manager()
    manager.load(_settings_path())
    assert manager.settings is not None


def test_valid_result_settings_manager_is_loaded_true():
    """
    Проверяет флаг is_loaded после загрузки настроек.

    Ожидаемый результат:
    is_loaded становится True, settings не равен None.
    """
    manager = settings_manager()
    manager.load(_settings_path())
    assert manager.is_loaded is True
    assert manager.settings is not None


def test_valid_result_settings_manager_organization_filled():
    """
    Проверяет, что после загрузки заполнена карточка организации.

    Ожидаемый результат:
    organization не равен None, реквизиты соответствуют JSON.
    """
    manager = settings_manager()
    manager.load(_settings_path())
    org = manager.settings.organization
    assert org is not None
    assert org.name == "ООО Ромашка"
    assert org.inn == "7707083893"
    assert org.bic == "044525225"


def test_valid_result_settings_manager_boss_and_account_name():
    """
    Проверяет, что после загрузки заполнены ФИО руководителя
    и главного бухгалтера.

    Ожидаемый результат:
    boss_name и account_name соответствуют данным из JSON.
    """
    manager = settings_manager()
    manager.load(_settings_path())
    assert manager.settings.boss_name == "Иванов И. И"
    assert manager.settings.account_name == "Семёнов А. Г."


def test_valid_result_settings_manager_data_not_empty():
    """
    Проверяет, что «сырые» данные JSON доступны через свойство data.

    Ожидаемый результат:
    data — непустой словарь, содержит ключи organization
    и first_launch_flag.
    """
    manager = settings_manager()
    manager.load(_settings_path())
    assert isinstance(manager.data, dict)
    assert "organization" in manager.data
    assert "first_launch_flag" in manager.data


def test_valid_result_settings_manager_response_format_loaded():
    """
    Проверяет, что после загрузки настроек поле response_format заполнено.

    1. Вызвать manager.load(_settings_path()).
    2. Проверить значение response_format.

    <expected>response_format == report_type_enum.MARKDOWN</expected>
    """
    from Src.Dtos.report_type_enum import report_type_enum

    manager = settings_manager()
    manager.load(_settings_path())
    assert manager.settings.response_format == report_type_enum.MARKDOWN


def test_valid_result_settings_model_response_format_string_setter():
    """
    Проверяет возможность установки response_format через строку.

    1. Установить response_format = "CSV".
    2. Проверить, что значение преобразовалось в report_type_enum.CSV.

    <expected>settings.response_format == report_type_enum.CSV</expected>
    """
    from Src.Dtos.report_type_enum import report_type_enum
    from Src.Models.settings_model import settings_model

    settings = settings_model()
    settings.response_format = "CSV"
    assert settings.response_format == report_type_enum.CSV

    settings.response_format = "html"
    assert settings.response_format == report_type_enum.HTML


def test_invalid_result_settings_model_response_format_bad_value():
    """
    Проверяет реакцию сеттера response_format на некорректное значение.

    1. Передать неподдерживаемую строку или объект другого типа.

    <expected>arguments_exception</expected>
    """
    from Src.Models.settings_model import settings_model

    settings = settings_model()
    with pytest.raises(arguments_exception):
        settings.response_format = "UNSUPPORTED_FORMAT"
    with pytest.raises(arguments_exception):
        settings.response_format = 12345


# ---------- Ошибки конвертации ----------

def test_invalid_result_settings_manager_convert_bad_data():
    """
    Проверяет реакцию convert() на некорректные данные.

    Ожидаемый результат:
    при отсутствии organization convert() возвращает False.
    """
    manager = settings_manager()
    manager._data = {"organization": None}
    assert manager.convert() is False