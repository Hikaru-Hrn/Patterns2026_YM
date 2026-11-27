import pytest

from Src.Core.abstract_observabile import abstract_observabile
from Src.Core.event_type import event_type
from Src.Logics.observer import observer


class _test_handler(abstract_observabile):
    """Тестовый наблюдатель для проверки рассылки событий."""

    def __init__(self) -> None:
        self.events: list[tuple[str, object]] = []

    def handler(self, event_type: str, params: object = None) -> None:
        self.events.append((event_type, params))


@pytest.fixture(autouse=True)
def reset_observer():
    """Очищает список наблюдателей перед каждым тестом."""
    observer.clear()
    yield
    observer.clear()


def test_valid_result_observer_add_and_create():
    """
    Проверяет добавление наблюдателя и публикацию события.

    1. Создать тестового наблюдателя.
    2. Добавить его в observer.
    3. Опубликовать событие.

    <expected>Наблюдатель получил событие с корректным типом и параметрами.</expected>
    """
    handler = _test_handler()
    observer.add(handler)

    observer.create(event_type.crud_create(), {"entity_type": "group"})

    assert len(handler.events) == 1
    assert handler.events[0][0] == event_type.crud_create()
    assert handler.events[0][1] == {"entity_type": "group"}


def test_valid_result_observer_no_handlers():
    """
    Проверяет публикацию события при отсутствии наблюдателей.

    1. Опубликовать событие без подписчиков.

    <expected>Ошибок не возникает, событие просто не обрабатывается.</expected>
    """
    observer.create(event_type.web_method_call(), {"method": "GET"})
    assert len(observer.handlers) == 0


def test_valid_result_observer_delete_handler():
    """
    Проверяет удаление наблюдателя.

    1. Добавить наблюдателя.
    2. Удалить его.
    3. Опубликовать событие.

    <expected>Наблюдатель не получил событие.</expected>
    """
    handler = _test_handler()
    observer.add(handler)
    observer.delete(handler)

    observer.create(event_type.crud_delete(), {"entity_type": "range"})

    assert len(handler.events) == 0


def test_valid_result_observer_no_duplicate_handlers():
    """
    Проверяет, что один и тот же наблюдатель не добавляется дважды.

    1. Добавить одного наблюдателя два раза.
    2. Опубликовать событие.

    <expected>Событие обработано один раз.</expected>
    """
    handler = _test_handler()
    observer.add(handler)
    observer.add(handler)

    observer.create(event_type.settings_change(), {})

    assert len(observer.handlers) == 1
    assert len(handler.events) == 1


def test_valid_result_event_type_values():
    """
    Проверяет корректность строковых констант типов событий.

    <expected>Все методы возвращают непустые строки.</expected>
    """
    assert event_type.crud_create() == "crud_create"
    assert event_type.crud_read() == "crud_read"
    assert event_type.crud_update() == "crud_update"
    assert event_type.crud_delete() == "crud_delete"
    assert event_type.storage_income() == "storage_income"
    assert event_type.storage_expense() == "storage_expense"
    assert event_type.web_method_call() == "web_method_call"
    assert event_type.settings_load() == "settings_load"
    assert event_type.settings_change() == "settings_change"
