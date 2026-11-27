from abc import ABC, abstractmethod


class abstract_observabile(ABC):
    """Элемент наблюдения."""

    @abstractmethod
    def handler(self, event_type: str, params: object = None) -> None:
        """Выполнить обработку события."""
        pass
