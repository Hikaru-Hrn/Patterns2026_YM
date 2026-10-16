from enum import Enum
from Src.Core.exception import arguments_exception


class report_type_enum(Enum):
    """Перечисление поддерживаемых форматов отчетов."""

    TXT = 1
    CSV = 2
    MARKDOWN = 3
    XML = 4
    HTML = 5

    @staticmethod
    def from_string(value: str) -> "report_type_enum":
        """Преобразует строковое наименование формата в значение перечисления.

        :param value: Строковое имя формата (CSV, Markdown, XML, TXT, HTML).
        :return: Значение report_type_enum.
        :raises arguments_exception: Если формат не распознан.
        """
        if not isinstance(value, str) or value.strip() == "":
            raise arguments_exception("response_format", "Формат отчета не может быть пустым")

        clean_value = value.strip().upper()
        mapping = {
            "TXT": report_type_enum.TXT,
            "CSV": report_type_enum.CSV,
            "MARKDOWN": report_type_enum.MARKDOWN,
            "MD": report_type_enum.MARKDOWN,
            "XML": report_type_enum.XML,
            "HTML": report_type_enum.HTML,
        }

        if clean_value not in mapping:
            raise arguments_exception(
                "response_format",
                f"Неподдерживаемый формат отчета: {value}. Доступные: CSV, Markdown, XML, TXT, HTML"
            )

        return mapping[clean_value]
