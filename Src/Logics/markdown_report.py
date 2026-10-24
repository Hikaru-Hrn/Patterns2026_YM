from Src.Core.abstract_model import abstract_model
from Src.Core.abstract_report import abstract_report
from Src.Core.common import common
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto


class markdown_report(abstract_report):
    """Реализация отчета в формате Markdown со скачиванием файла."""

    @property
    def media_type(self) -> str:
        return "text/markdown; charset=utf-8"

    @property
    def file_extension(self) -> str:
        return "md"

    @property
    def is_attachment(self) -> bool:
        return True

    def build(self, source: abstract_model) -> report_result_dto:
        """Формирует отчет в формате Markdown по метаданным любой сущности через common.

        :param source: Экземпляр доменной модели (наследник abstract_model).
        :return: report_result_dto с заполненным свойством binary.
        """
        validator.validate(source, abstract_model)

        headers = common.get_entity_header(source)
        table_data = common.get_entity_table(source)

        lines = []
        if table_data and len(table_data) > 0 and len(table_data[0].columns) > 0:
            columns = table_data[0].columns
            lines.append("| " + " | ".join(columns) + " |")
            lines.append("| " + " | ".join([":---"] * len(columns)) + " |")
            for row in table_data:
                lines.append("| " + " | ".join(row.values) + " |")
        else:
            lines.append("| Поле | Значение |")
            lines.append("| :--- | :--- |")
            for h in headers:
                lines.append(f"| {h.field} | {h.value} |")

        content = "\n".join(lines).strip()
        result = report_result_dto()
        result.binary = list(content.encode("utf-8"))
        result.format = self.media_type
        return result
