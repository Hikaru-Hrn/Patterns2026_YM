
import json

from Src.Core.abstract_manager import abstract_manager
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model
from Src.Core.exception import operation_exception


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
        """Преобразует «сырые» данные JSON в settings_model.

        :return: True, если преобразование прошло успешно, иначе False.
        """
        try:
            if not isinstance(self._data, dict):
                self._is_loaded = False
                return False

            org_data = self._data.get("organization")
            if not isinstance(org_data, dict):
                self._is_loaded = False
                return False

            org = organization_model(
                name=str(org_data.get("name", "")),
                inn=str(org_data.get("inn", "")),
                bic=str(org_data.get("bic", "")),
                account=str(org_data.get("account", "")),
                owner=str(org_data.get("owner", ""))
            )

            self._settings.organization = org

            self._settings.boss_name = str(self._data.get("boss_name", ""))
            self._settings.account_name = str(self._data.get("account_name", ""))

            raw_flag = self._data.get("first_launch_flag", True)
            self._settings.first_launch_flag = bool(raw_flag)

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