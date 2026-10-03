from abc import ABC


class abstract_manager(ABC):
    """Абстрактный класс менеджеров для загрузки и конвертации прикладных данных."""

    _file_name: str = ""
    _is_loaded: bool = False
    _data: dict = {}

    def load(self, file_name: str = "") -> None:
        """Загружает данные из источника."""
        pass

    def convert(self) -> bool:
        """Преобразует загруженные сырые данные в доменные модели."""
        return False

    @property
    def is_loaded(self) -> bool:
        """Возвращает флаг готовности и успешной загрузки данных."""
        return self._is_loaded

