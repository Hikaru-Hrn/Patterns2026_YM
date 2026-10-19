from xml.sax.saxutils import escape

from Src.Core.abstract_model import abstract_model
from Src.Core.abstract_report import abstract_report
from Src.Core.common import common
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto


class xml_report(abstract_report):
    """Реализация структурированного отчета в формате XML."""

    @property
    def media_type(self) -> str:
        return "application/xml; charset=utf-8"

    @property
    def file_extension(self) -> str:
        return "xml"

    @property
    def is_attachment(self) -> bool:
        return False

    def build(self, source: abstract_model) -> report_result_dto:
        """Формирует структурированный XML-отчет по метаданным любой сущности через common.

        :param source: Экземпляр доменной модели (наследник abstract_model).
        :return: report_result_dto со свойством text.
        """
        validator.validate(source, abstract_model)

        headers = common.get_entity_header(source)
        table_data = common.get_entity_table(source)
        tag_name = source.__class__.__name__

        xml_lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f"<{tag_name}>",
        ]

        for h in headers:
            xml_lines.append(f"  <{h.field}>{escape(str(h.value))}</{h.field}>")

        if table_data and len(table_data) > 0 and len(table_data[0].columns) > 0:
            xml_lines.append("  <items>")
            for row in table_data:
                xml_lines.append("    <item>")
                for col, val in zip(row.columns, row.values):
                    xml_lines.append(f"      <{col}>{escape(str(val))}</{col}>")
                xml_lines.append("    </item>")
            xml_lines.append("  </items>")

        xml_lines.append(f"</{tag_name}>")

        result = report_result_dto()
        result.text = "\n".join(xml_lines)
        result.format = self.media_type
        return result
