from Src.Core.abstract_model import abstract_model
from Src.Core.abstract_report import abstract_report
from Src.Core.common import common
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto


class text_report(abstract_report):
    """Реализация текстового представления отчета по любой доменной сущности."""

    @property
    def media_type(self) -> str:
        return "text/plain; charset=utf-8"

    @property
    def file_extension(self) -> str:
        return "txt"

    @property
    def is_attachment(self) -> bool:
        return False

    def build(self, source: abstract_model) -> report_result_dto:
        """Формирует текстовый отчет по метаданным переданной сущности через common.

        :param source: Экземпляр доменной модели (наследник abstract_model).
        :return: report_result_dto с заполненным свойством text.
        """
        validator.validate(source, abstract_model)

        lines = []
        headers = common.get_entity_header(source)
        table_data = common.get_entity_table(source)

        if table_data and len(table_data) > 0 and len(table_data[0].columns) > 0:
            lines.append("Заголовок")
            for h in headers:
                lines.append(f"{h.field}: {h.value}")
            lines.append("")
            lines.append("Табличная часть")
            header_line = " | ".join([col.replace("_", " ").capitalize() for col in table_data[0].columns])
            lines.append(header_line)
            lines.append("-" * len(header_line))
            for row in table_data:
                lines.append(" | ".join(row.values))
        else:
            for h in headers:
                lines.append(f"{h.field}: {h.value}")

        result_text = "\n".join(lines).strip()
        result = report_result_dto()
        result.text = result_text
        result.format = self.media_type
        return result
