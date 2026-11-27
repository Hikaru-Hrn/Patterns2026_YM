class event_type:
    """Типы событий для шаблона 'Наблюдатель'."""

    @staticmethod
    def crud_create() -> str:
        """Создание доменной сущности."""
        return "crud_create"

    @staticmethod
    def crud_read() -> str:
        """Чтение доменной сущности."""
        return "crud_read"

    @staticmethod
    def crud_update() -> str:
        """Изменение доменной сущности."""
        return "crud_update"

    @staticmethod
    def crud_delete() -> str:
        """Удаление доменной сущности."""
        return "crud_delete"

    @staticmethod
    def storage_income() -> str:
        """Приход номенклатуры на склад."""
        return "storage_income"

    @staticmethod
    def storage_expense() -> str:
        """Расход номенклатуры со склада."""
        return "storage_expense"

    @staticmethod
    def web_method_call() -> str:
        """Вызов web-метода."""
        return "web_method_call"

    @staticmethod
    def settings_load() -> str:
        """Загрузка настроек из файла."""
        return "settings_load"

    @staticmethod
    def settings_change() -> str:
        """Изменение параметров настроек."""
        return "settings_change"

    @staticmethod
    def error() -> str:
        """Ошибка в подсистеме."""
        return "error"
