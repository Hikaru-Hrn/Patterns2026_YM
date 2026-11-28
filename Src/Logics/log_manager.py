from datetime import datetime
from pathlib import Path

from Src.Core.abstract_observabile import abstract_observabile
from Src.Core.event_type import event_type
from Src.Core.exception import arguments_exception
from Src.Logics.observer import observer
from Src.Models.log_entry_model import log_entry_model


class log_manager(abstract_observabile):
    """Менеджер логирования на основе шаблона 'Наблюдатель'."""

    _instance = None
    _initialized: bool = False

    # Подсистемы
    SUBSYSTEM_CRUD = "CRUD"
    SUBSYSTEM_STORAGE = "Storage"
    SUBSYSTEM_WEB = "Web"
    SUBSYSTEM_SETTINGS = "Settings"

    # Уровни
    LEVEL_ERROR = "ERROR"
    LEVEL_INFO = "INFO"
    LEVEL_DEBUG = "DEBUG"

    # Путь к файлу лога по умолчанию
    __default_log_path: Path = Path(__file__).resolve().parent.parent.parent / "logs" / "app.log"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(log_manager, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_path: Path | str = None):
        """Инициализирует менеджер логирования и подписывает его на события."""
        if self._initialized:
            return

        super().__init__()
        self.__log_path = self.__resolve_log_path(log_path)
        self.__entries: list[log_entry_model] = []
        self.__ensure_directory()
        self.__load_from_file()
        observer.add(self)
        self._initialized = True

    @staticmethod
    def __resolve_log_path(log_path: Path | str | None) -> Path:
        """Определяет путь к файлу лога.

        :param log_path: Пользовательский путь или None.
        :return: Абсолютный путь к файлу лога.
        """
        if log_path is None:
            return log_manager.__default_log_path
        return Path(log_path).resolve()

    def __ensure_directory(self) -> None:
        """Создает каталог для файла лога, если он отсутствует."""
        self.__log_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def log_path(self) -> Path:
        """Возвращает путь к файлу лога."""
        return self.__log_path

    def set_log_path(self, log_path: Path | str) -> None:
        """Изменяет путь к файлу лога.

        :param log_path: Новый путь к файлу лога.
        """
        self.__log_path = self.__resolve_log_path(log_path)
        self.__ensure_directory()

    @property
    def entries(self) -> list[log_entry_model]:
        """Возвращает список записей лога в памяти."""
        return list(self.__entries)

    def handler(self, event_type_value: str, params: object = None) -> None:
        """Обрабатывает полученное событие, записывая его в лог.

        :param event_type_value: Тип события.
        :param params: Дополнительные параметры события.
        """
        subsystem, level, message = self.__classify_event(event_type_value, params)
        self.log(subsystem, level, message)

    def log(self, subsystem: str, level: str, message: str) -> log_entry_model:
        """Добавляет запись в лог.

        :param subsystem: Название подсистемы.
        :param level: Уровень сообщения.
        :param message: Текст сообщения.
        :return: Созданная запись лога.
        """
        entry = log_entry_model.create(datetime.now(), subsystem, level, message)
        self.__entries.append(entry)
        self.__write(entry)
        try:
            from Src.Logics.storage_manager import storage_manager

            storage_manager().add_log_entry(entry)
        except Exception:
            pass
        return entry

    def log_error(self, subsystem: str, message: str) -> log_entry_model:
        """Добавляет ошибку в лог.

        :param subsystem: Название подсистемы.
        :param message: Текст сообщения.
        :return: Созданная запись лога.
        """
        return self.log(subsystem, self.LEVEL_ERROR, message)

    def log_info(self, subsystem: str, message: str) -> log_entry_model:
        """Добавляет информационное сообщение в лог.

        :param subsystem: Название подсистемы.
        :param message: Текст сообщения.
        :return: Созданная запись лога.
        """
        return self.log(subsystem, self.LEVEL_INFO, message)

    def log_debug(self, subsystem: str, message: str) -> log_entry_model:
        """Добавляет отладочное сообщение в лог.

        :param subsystem: Название подсистемы.
        :param message: Текст сообщения.
        :return: Созданная запись лога.
        """
        return self.log(subsystem, self.LEVEL_DEBUG, message)

    def __classify_event(self, event_type_value: str, params: object) -> tuple[str, str, str]:
        """Определяет подсистему, уровень и сообщение по типу события.

        :param event_type_value: Тип события.
        :param params: Параметры события.
        :return: Кортеж (subsystem, level, message).
        """
        message = self.__format_params(params)

        if event_type_value in (
            event_type.crud_create(),
            event_type.crud_update(),
            event_type.crud_delete(),
        ):
            return self.SUBSYSTEM_CRUD, self.LEVEL_INFO, message

        if event_type_value == event_type.crud_read():
            return self.SUBSYSTEM_CRUD, self.LEVEL_DEBUG, message

        if event_type_value in (event_type.storage_income(), event_type.storage_expense()):
            return self.SUBSYSTEM_STORAGE, self.LEVEL_INFO, message

        if event_type_value == event_type.web_method_call():
            return self.SUBSYSTEM_WEB, self.LEVEL_DEBUG, message

        if event_type_value in (event_type.settings_load(), event_type.settings_change()):
            return self.SUBSYSTEM_SETTINGS, self.LEVEL_INFO, message

        if event_type_value == event_type.error():
            subsystem = params.get("subsystem") if isinstance(params, dict) else self.SUBSYSTEM_CRUD
            return subsystem, self.LEVEL_ERROR, message

        return self.SUBSYSTEM_CRUD, self.LEVEL_DEBUG, message

    @staticmethod
    def __format_params(params: object) -> str:
        """Преобразует параметры события в строку.

        :param params: Параметры события.
        :return: Строковое представление параметров.
        """
        if params is None:
            return ""
        if isinstance(params, dict):
            return "; ".join(f"{key}: {value}" for key, value in params.items())
        return str(params)

    def __write(self, entry: log_entry_model) -> None:
        """Записывает одну запись в файл лога.

        :param entry: Запись лога.
        """
        line = self.__format_line(entry)
        try:
            with open(self.__log_path, "a", encoding="utf-8") as file:
                file.write(line + "\n")
        except Exception:
            pass

    @staticmethod
    def __format_line(entry: log_entry_model) -> str:
        """Форматирует запись лога для записи в файл.

        :param entry: Запись лога.
        :return: Строка в формате [period] | subsystem | level | message.
        """
        period = entry.period.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{period}] | {entry.subsystem} | {entry.level} | {entry.message}"

    def __load_from_file(self) -> None:
        """Подгружает существующие записи из файла лога в память и хранилище."""
        if not self.__log_path.exists():
            return

        try:
            with open(self.__log_path, "r", encoding="utf-8") as file:
                for line in file:
                    entry = self.__parse_line(line)
                    if entry is not None:
                        self.__entries.append(entry)
                        try:
                            from Src.Logics.storage_manager import storage_manager

                            storage_manager().add_log_entry(entry)
                        except Exception:
                            pass
        except Exception:
            pass

    @staticmethod
    def __parse_line(line: str) -> log_entry_model | None:
        """Парсит одну строку файла лога в модель.

        :param line: Строка из файла лога.
        :return: log_entry_model или None, если строка не распознана.
        """
        parts = line.strip().split(" | ", 3)
        if len(parts) != 4:
            return None

        period_str, subsystem, level, message = parts
        period_str = period_str.strip("[]")

        try:
            period = datetime.strptime(period_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

        try:
            return log_entry_model.create(period, subsystem, level, message)
        except arguments_exception:
            return None

    def clear_log(self) -> None:
        """Очищает файл лога и записи в памяти и хранилище."""
        self.__entries.clear()
        try:
            from Src.Logics.storage_manager import storage_manager

            storage_manager()._log_entries.clear()
            storage_manager()._invalidate_filter_index()
        except Exception:
            pass
        try:
            self.__log_path.write_text("", encoding="utf-8")
        except Exception:
            pass
