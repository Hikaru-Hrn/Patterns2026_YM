from typing import List

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Dtos.entity_description_header_dto import entity_description_header_dto
from Src.Dtos.entity_description_table_dto import entity_description_table_dto


class common:
    """Набор вспомогательных статических методов рефлексии метаданных моделей."""

    @staticmethod
    def get_fields(source, is_common: bool = False) -> list:
        """Получает полный список открытых свойств (@property) любой модели.

        :param source: Экземпляр доменной модели.
        :param is_common: Если True — исключает свойства-списки и словари (оставляет только скаляры).
        :return: Список имен свойств.
        :raises arguments_exception: Если source равен None.
        """
        if source is None:
            raise arguments_exception("source", "Некорректно переданы аргументы!")

        items = list(filter(lambda x: not x.startswith("_"), dir(source)))
        result = []

        for item in items:
            attribute = getattr(source.__class__, item, None)
            if isinstance(attribute, property):
                try:
                    value = getattr(source, item)
                except Exception:
                    continue

                if is_common and (isinstance(value, (dict, list))):
                    continue

                result.append(item)

        return result

    @staticmethod
    def get_entity_header(source: abstract_model) -> List[entity_description_header_dto]:
        """Формирует список заголовков и строковых значений для скалярных свойств модели.

        :param source: Экземпляр модели (наследник abstract_model).
        :return: Список DTO заголовков полей.
        :raises arguments_exception: Если source равен None.
        """
        if source is None:
            raise arguments_exception("source", "Некорректно переданы аргументы!")

        result: List[entity_description_header_dto] = []
        field_names = common.get_fields(source, is_common=True)

        for field_name in field_names:
            dto = entity_description_header_dto()
            dto.field = field_name
            try:
                value = getattr(source, field_name)
                if hasattr(value, "name") and getattr(value, "name"):
                    dto.value = str(getattr(value, "name"))
                else:
                    dto.value = str(value) if value is not None else ""
            except Exception:
                dto.value = ""

            result.append(dto)

        return result

    @staticmethod
    def get_entity_table(source: abstract_model) -> List[entity_description_table_dto]:
        """Формирует табличную часть агрегата на основе его первого непустого свойства-списка.

        :param source: Экземпляр агрегата.
        :return: Список DTO строк таблицы.
        :raises arguments_exception: Если source равен None.
        """
        if source is None:
            raise arguments_exception("source", "Некорректно переданы аргументы!")

        result: List[entity_description_table_dto] = []
        field_names = common.get_fields(source, is_common=False)
        list_field_name = next(
            (name for name in field_names if isinstance(getattr(source, name, None), list) and len(getattr(source, name)) > 0),
            None
        )
        if not list_field_name:
            return result

        items = getattr(source, list_field_name)
        for item in items:
            headers = common.get_entity_header(item)
            table_dto = entity_description_table_dto()
            table_dto.columns = [header.field for header in headers]
            table_dto.values = [header.value for header in headers]
            result.append(table_dto)

        return result
