from html import escape

from Src.Core.abstract_model import abstract_model
from Src.Core.abstract_report import abstract_report
from Src.Core.common import common
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto


class html_report(abstract_report):
    """Реализация отчета в формате HTML со структурированным текстовым выводом."""

    @property
    def media_type(self) -> str:
        return "text/html; charset=utf-8"

    @property
    def file_extension(self) -> str:
        return "html"

    @property
    def is_attachment(self) -> bool:
        return False

    def build(self, source: abstract_model) -> report_result_dto:
        """Формирует структурированный HTML-отчет по метаданным любой сущности через common.

        :param source: Экземпляр доменной модели (наследник abstract_model).
        :return: report_result_dto со свойством text.
        """
        validator.validate(source, abstract_model)

        headers = common.get_entity_header(source)
        table_data = common.get_entity_table(source)
        title = source.__class__.__name__

        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            f"<head><meta charset=\"utf-8\"><title>Отчет: {escape(title)}</title></head>",
            "<body>",
            f"<h2>Отчет по сущности: {escape(title)}</h2>",
            "<table border=\"1\" cellpadding=\"5\" cellspacing=\"0\">",
        ]

        for h in headers:
            html_lines.append(f"  <tr><th>{escape(str(h.field))}</th><td>{escape(str(h.value))}</td></tr>")

        html_lines.append("</table>")

        if table_data and len(table_data) > 0 and len(table_data[0].columns) > 0:
            columns = table_data[0].columns
            html_lines.append("<h3>Табличная часть</h3>")
            html_lines.append("<table border=\"1\" cellpadding=\"5\" cellspacing=\"0\">")
            html_lines.append("  <thead><tr>" + "".join([f"<th>{escape(str(col))}</th>" for col in columns]) + "</tr></thead>")
            html_lines.append("  <tbody>")
            for row in table_data:
                html_lines.append("    <tr>" + "".join([f"<td>{escape(str(val))}</td>" for val in row.values]) + "</tr>")
            html_lines.append("  </tbody>")
            html_lines.append("</table>")

        html_lines.append("</body>")
        html_lines.append("</html>")

        result = report_result_dto()
        result.text = "\n".join(html_lines)
        result.format = self.media_type
        return result
