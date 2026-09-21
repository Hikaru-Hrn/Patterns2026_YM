from abc import ABC, abstractmethod
from uuid import UUID, uuid4


class abstract_entity(ABC):
    def __init__(self) -> None:
        """
        name: Наименование сущности.
        code: Уникальный код, генерируется если не найден.
        """
        # Внутренние поля
        self._name: str = ""
        self._code: str = str(uuid4())


    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        raise TypeError: Если передана не строка.
        raise ValueError: Если передана пустая строка.
        """
        if not isinstance(value, str):
            raise TypeError("Наименование должно быть строкового типа (str)")

        stripped = value.strip()
        if not stripped:
            raise ValueError("Наименование не может быть пустой строкой")

        self._name = stripped

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str | UUID) -> None:
        """
        raise TypeError: Если передан неподдерживаемый тип.
        raise ValueError: Если строка пустая.
        """
        if isinstance(value, UUID):
            self._code = str(value)
        elif isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("Код сущности не может быть пустой строкой")
            self._code = stripped
        else:
            raise TypeError("Код должен быть строкой (str) или экземпляром UUID")

    @abstractmethod
    def validate(self) -> bool:
        """
        Абстрактный метод валидации бизнес-правил конкретной сущности.
        Обязателен для реализации во всех классах-наследниках.
        """
        pass