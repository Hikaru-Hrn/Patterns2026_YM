from Src.Core.abstract_model import abstract_model
from Src.Core.entity_model import entity_model
from Src.Core.validator import validator
from Src.Core.exception import operation_exception
from Src.Core.common import common


class storage_repository:
    """Репозиторий для хранения списка объектов и счетчика связей."""

    # Исходный набор данных. Ключ - GUID, значение - abstract_model
    __data: dict = {}
    # Счетчик ссылок. Ключ - GUID, значение - число ссылок
    __counts: dict = {}

    def registry(self, source: abstract_model):
        """Зарегистрировать доменный объект и все его вложенные ссылки."""
        validator.validate(source, abstract_model)

        # Регистрируем основной объект
        self.__data[source.unique_code] = source
        if source.unique_code in self.__counts:
            self.__counts[source.unique_code] += 1
        else:
            self.__counts[source.unique_code] = 0

        # Регистрируем вложения, увеличивая счётчики ссылок
        self._walk_nested(source, self._inc_count)

    def registry_range(self, items: list):
        """Зарегистрировать сразу несколько объектов."""
        validator.validate(items, list)
        for item in items:
            self.registry(item)

    def get(self, source: str):
        """Получить объект по уникальному коду."""
        validator.validate(source, str)

        if source in self.__data:
            return self.__data.get(source)
        raise operation_exception(f"Не найдена доменная сущность по коду : {source}!")

    def can_delete(self, source: abstract_model) -> bool:
        """Проверить возможность удаления (нет входящих ссылок)."""
        validator.validate(source, abstract_model)

        try:
            self.get(source.unique_code)
            return self.__counts[source.unique_code] == 0
        except Exception:
            return False

    def delete(self, source: abstract_model):
        """Удалить сущность из репозитория, уменьшив счётчики её исходящих ссылок."""
        validator.validate(source, abstract_model)
        if not self.can_delete(source):
            raise operation_exception(f"Невозможно удалить запись {source.unique_code}!")

        self._walk_nested(source, self._dec_count)
        self.__data.pop(source.unique_code, None)
        self.__counts.pop(source.unique_code, None)

    @property
    def data(self) -> dict:
        """Исходный набор данных."""
        return self.__data

    @property
    def counts(self) -> dict:
        """Исходный набор счетчиков."""
        return self.__counts

    def _walk_nested(self, source: abstract_model, callback, visited: set | None = None):
        """Обойти вложенные модели (поля и списки) и применить callback к каждой.

        :param source: Корневой объект, вложения которого обходятся.
        :param callback: Функция (abstract_model) -> None.
        :param visited: Множество id уже пройденных объектов (защита от циклов).
        """
        if visited is None:
            visited = set()
        if id(source) in visited:
            return
        visited.add(id(source))

        fields = common.get_fields(source, False)
        for field in fields:
            value = getattr(source, field)
            if isinstance(value, (abstract_model, entity_model)):
                callback(value)
                self._walk_nested(value, callback, visited)
            elif isinstance(value, (list, tuple, set)):
                for item in value:
                    if isinstance(item, (abstract_model, entity_model)):
                        callback(item)
                        self._walk_nested(item, callback, visited)

    def _inc_count(self, ref: abstract_model):
        """Увеличить счётчик ссылок на объект."""
        if ref.unique_code in self.__counts:
            self.__counts[ref.unique_code] += 1
        else:
            self.__counts[ref.unique_code] = 0

    def _dec_count(self, ref: abstract_model):
        """Уменьшить счётчик ссылок на объект, но не ниже нуля."""
        code = ref.unique_code
        if code in self.__counts and self.__counts[code] > 0:
            self.__counts[code] -= 1
