from Src.Core.abstract_observabile import abstract_observabile
from Src.Core.validator import validator


class observer:
    """Реализация шаблона 'Наблюдатель'."""

    # Список наблюдателей
    handlers: list[abstract_observabile] = []

    @staticmethod
    def add(source: abstract_observabile) -> None:
        """Добавить под наблюдение."""
        validator.validate(source, abstract_observabile)

        for handler in observer.handlers:
            if handler is source:
                return

        observer.handlers.append(source)

    @staticmethod
    def delete(source: abstract_observabile) -> None:
        """Удалить из-под наблюдения."""
        validator.validate(source, abstract_observabile)

        for handler in list(observer.handlers):
            if handler is source:
                observer.handlers.remove(handler)
                return

    @staticmethod
    def create(event_type: str, params: object = None) -> None:
        """Вызвать событие."""
        for handler in observer.handlers:
            if handler is not None:
                handler.handler(event_type, params)

    @staticmethod
    def clear() -> None:
        """Очистить список наблюдателей."""
        observer.handlers.clear()
