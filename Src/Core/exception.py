class base_exception(Exception):
    """Базовое исключение домена.

    Хранит имя поля, текст сообщения и (опционально) трассировку стека.
    """

    __message: str = ""
    __field: str = ""
    __stack_trace: str = ""

    def __init__(self, field: str, message: str, stack_trace: str = "") -> None:
        """Инициализирует исключение.

        :param field: Имя поля, в котором произошла ошибка.
        :param message: Текст сообщения об ошибке.
        :param stack_trace: Трассировка стека (при наличии).
        """
        self.__field = (field or "").strip()
        self.__message = (message or "").strip()
        self.__stack_trace = (stack_trace or "").strip()
        super().__init__(self.__message)

    @property
    def field(self) -> str:
        """Возвращает имя поля, в котором произошла ошибка."""
        return self.__field

    @property
    def message(self) -> str:
        """Возвращает текст сообщения об ошибке."""
        return self.__message

    @property
    def stack_trace(self) -> str:
        """Возвращает трассировку стека (при наличии)."""
        return self.__stack_trace

    def __str__(self) -> str:
        """Возвращает строковое представление исключения."""
        return (
            f"Ошибка: Некорректный аргумент!\n"
            f"Поле: {self.__field}\n"
            f"{self.__message}\n"
            f"{self.__stack_trace}"
        )


class arguments_exeption(base_exception):
    """Исключение о некорректно переданном аргументе."""

    def __init__(self, field: str, message: str, stack_trace: str = "") -> None:
        """Инициализирует исключение.

        :param field: Имя поля, в котором произошла ошибка.
        :param message: Текст сообщения об ошибке.
        :param stack_trace: Трассировка стека (при наличии).
        """
        super().__init__(field, message, stack_trace)


class max_length_exeption(base_exception):
    """Исключение о превышении максимальной длины поля."""

    def __init__(self, field: str, max_length: int, stack_trace: str = "") -> None:
        """Инициализирует исключение.

        :param field: Имя поля, в котором произошла ошибка.
        :param max_length: Максимально допустимая длина поля.
        :param stack_trace: Трассировка стека (при наличии).
        """
        message = f"Превышена максимальная длина поля ({max_length} символов)"
        super().__init__(field, message, stack_trace)


class length_exeption(base_exception):
    """Исключение о некорректной длине поля."""

    def __init__(self, field: str, length: int, document: str,
                 stack_trace: str = "") -> None:
        """Инициализирует исключение.

        :param field: Имя поля, в котором произошла ошибка.
        :param length: Ожидаемая длина поля.
        :param document: Название документа/поля для сообщения.
        :param stack_trace: Трассировка стека (при наличии).
        """
        message = f"Неккоректная длина {document}! Она должна быть {length} символов"
        super().__init__(field, message, stack_trace)


class validation_exeptoion(base_exception):
    """Исключение о непройденной валидации значения поля."""

    def __init__(self, field: str, message: str, stack_trace: str = "") -> None:
        """Инициализирует исключение.

        :param field: Имя поля, в котором произошла ошибка.
        :param message: Текст сообщения об ошибке.
        :param stack_trace: Трассировка стека (при наличии).
        """
        super().__init__(field, message, stack_trace)