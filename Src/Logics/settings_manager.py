
import json

from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import operation_exception
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Models.settings_model import settings_model


class settings_manager(abstract_manager):
    """Менеджер для работы с настройками (Singleton).

    Читает JSON-файл настроек, преобразует его в settings_model
    и предоставляет доступ к «сырым» данным через свойство data.
    """

    __default_file_name = "settings.json"

    _instance = None
    _initialized: bool = False

    def __new__(cls):
        """Реализует шаблон Singleton.

        :return: Единственный экземпляр settings_manager.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
        Инициализация состояния Singleton.

        Защищена флагом _initialized, чтобы повторные вызовы settings_manager()
        не сбрасывали уже загруженные в память данные.
        """
        if self._initialized:
            return
        super().__init__()
        self._settings = settings_model()
        self._is_loaded = False
        self._data = {}
        self._initialized = True


    def load(self, file_name: str = "") -> None:
        """Загружает настройки из JSON-файла.

        :param file_name: Путь к файлу. Если пусто — используется
            значение по умолчанию (settings.json).
        """
        inner_file_name = file_name.strip() if file_name.strip() != "" else self.__default_file_name
        try:
            with open(inner_file_name, "r", encoding="utf-8") as file:
                self._data = json.load(file)
            self._is_loaded = self.convert()
        except Exception as e:
            self._is_loaded = False
            raise operation_exception(f"Ошибка при чтении файла {inner_file_name}: {e}")

    def convert(self) -> bool:
        """Преобразует «сырые» данные JSON в settings_model через deserialize_factory.

        :return: True, если преобразование прошло успешно, иначе False.
        """
        try:
            if not isinstance(self._data, dict):
                self._is_loaded = False
                return False

            restored: settings_model = deserialize_factory().Convert(self._data, settings_model)
            for field_name in abstract_covertor._get_fields(self._settings):
                attribute = getattr(type(self._settings), field_name, None)
                if isinstance(attribute, property) and attribute.fset is not None:
                    setattr(self._settings, field_name, getattr(restored, field_name))

            self._is_loaded = True
            return True
        except Exception:
            self._is_loaded = False
            return False

    @property
    def settings(self) -> settings_model:
        """Возвращает загруженную модель настроек."""
        return self._settings

    @settings.setter
    def settings(self, value: settings_model):
        """Устанавливает модель настроек.

        :param value: Новая модель настроек.
        """
        self._settings = value

    @property
    def data(self) -> dict:
        """Возвращает «сырые» данные JSON (нужно storage_manager)."""
        return self._data