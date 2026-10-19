class entity_description_table_dto:
    """DTO для описания одной строки табличной части агрегата."""

    __columns: list[str]
    __values: list[str]

    def __init__(self) -> None:
        """Инициализирует DTO пустой строкой таблицы."""
        self.__columns = []
        self.__values = []

    @property
    def columns(self) -> list[str]:
        """Возвращает список наименований колонок."""
        return self.__columns

    @columns.setter
    def columns(self, value: list[str]) -> None:
        """Устанавливает список колонок."""
        self.__columns = value

    @property
    def values(self) -> list[str]:
        """Возвращает список значений строки."""
        return self.__values

    @values.setter
    def values(self, value: list[str]) -> None:
        """Устанавливает список значений."""
        self.__values = value
