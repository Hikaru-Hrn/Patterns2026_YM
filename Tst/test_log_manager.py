import os
import tempfile

import pytest

from Src.Core.event_type import event_type
from Src.Logics.log_manager import log_manager
from Src.Logics.observer import observer
from Src.Models.log_entry_model import log_entry_model


@pytest.fixture(autouse=True)
def reset_observer():
    """Очищает список наблюдателей перед каждым тестом и восстанавливает log_manager."""
    observer.clear()
    manager = log_manager()
    observer.add(manager)
    yield
    observer.clear()


def test_valid_result_log_manager_writes_event():
    """
    Проверяет запись события в файл лога.

    1. Создать log_manager с временным файлом.
    2. Опубликовать событие.
    3. Прочитать содержимое файла.

    <expected>Файл содержит запись о событии в формате [period] | subsystem | level | message.</expected>
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp:
        log_path = temp.name

    try:
        manager = log_manager()
        manager.set_log_path(log_path)
        observer.create(event_type.crud_create(), {"entity_type": "group", "name": "Напитки"})

        with open(log_path, "r", encoding="utf-8") as file:
            content = file.read()

        assert "CRUD" in content
        assert "INFO" in content
        assert "entity_type: group" in content
        assert "name: Напитки" in content
    finally:
        os.unlink(log_path)


def test_valid_result_log_manager_creates_directory():
    """
    Проверяет автоматическое создание каталога для лога.

    1. Указать путь в несуществующем каталоге.
    2. Создать log_manager.

    <expected>Каталог и файл созданы.</expected>
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = os.path.join(temp_dir, "nested", "app.log")
        manager = log_manager()
        manager.set_log_path(log_path)

        assert os.path.isdir(os.path.dirname(log_path))
        assert str(manager.log_path) == log_path


def test_valid_result_log_manager_clear_log():
    """
    Проверяет очистку файла лога.

    1. Создать лог-файл с записью.
    2. Вызвать clear_log.

    <expected>Файл пустой, записи в памяти очищены.</expected>
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp:
        log_path = temp.name
        temp.write("old log\n")

    try:
        manager = log_manager()
        manager.set_log_path(log_path)
        manager.clear_log()

        with open(log_path, "r", encoding="utf-8") as file:
            assert file.read() == ""
        assert len(manager.entries) == 0
    finally:
        os.unlink(log_path)


def test_valid_result_log_manager_appends_to_file():
    """
    Проверяет дописывание событий в конец файла.

    1. Записать одно событие.
    2. Записать второе событие.

    <expected>В файле две строки с корректными уровнями.</expected>
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp:
        log_path = temp.name

    try:
        manager = log_manager()
        manager.set_log_path(log_path)
        observer.create(event_type.crud_create(), {"entity_type": "group"})
        observer.create(event_type.crud_delete(), {"entity_type": "range"})

        with open(log_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        assert len(lines) == 2
        assert "| CRUD | INFO |" in lines[0]
        assert "| CRUD | INFO |" in lines[1]
    finally:
        os.unlink(log_path)


def test_valid_result_log_manager_stores_entries():
    """
    Проверяет хранение записей лога в памяти в виде log_entry_model.

    1. Опубликовать событие.
    2. Получить список записей.

    <expected>Список содержит log_entry_model с заполненными полями.</expected>
    """
    manager = log_manager()
    manager.clear_log()

    observer.create(event_type.web_method_call(), {"method": "GET", "url": "/api/test"})

    entries = manager.entries
    assert len(entries) == 1
    assert isinstance(entries[0], log_entry_model)
    assert entries[0].subsystem == log_manager.SUBSYSTEM_WEB
    assert entries[0].level == log_manager.LEVEL_DEBUG
    assert "GET" in entries[0].message


def test_valid_result_log_manager_levels():
    """
    Проверяет распределение уровней по типам событий.

    <expected>CRUD-мутации = INFO, чтение = DEBUG, склад = INFO, web = DEBUG, настройки = INFO, ошибка = ERROR.</expected>
    """
    manager = log_manager()
    manager.clear_log()

    observer.create(event_type.crud_create(), {})
    observer.create(event_type.crud_read(), {})
    observer.create(event_type.storage_income(), {})
    observer.create(event_type.web_method_call(), {})
    observer.create(event_type.settings_change(), {})
    observer.create(event_type.error(), {"subsystem": log_manager.SUBSYSTEM_CRUD})

    entries = manager.entries
    assert entries[0].level == log_manager.LEVEL_INFO
    assert entries[1].level == log_manager.LEVEL_DEBUG
    assert entries[2].level == log_manager.LEVEL_INFO
    assert entries[3].level == log_manager.LEVEL_DEBUG
    assert entries[4].level == log_manager.LEVEL_INFO
    assert entries[5].level == log_manager.LEVEL_ERROR
