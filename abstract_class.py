from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID, uuid4


class AbstractEntity(ABC):
    def __init__(self, name: str, code: Optional[str | UUID] = None) -> None:
        self._name: str = ""
        self._code: str = ""

        self.name = name  # Валидация через property setter
        self.code = code if code is not None else str(uuid4())

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Наименование должно быть строкового типа (str)")
        stripped = value.strip()
        if not stripped:
            raise ValueError("Наименование не может быть пустой строкой")
        self._name = stripped