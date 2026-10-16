from xml.sax.saxutils import escape

from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class xml_report(abstract_report):
    """Реализация формирования отчета в формате XML со структурированным текстовым выводом."""

    def build(self, source) -> report_result_dto:
        """Формирует структурированный XML-отчет.

        :param source: receipt_model, nomenclature_model или range_model.
        :return: report_result_dto со свойством text.
        """
        if isinstance(source, receipt_model):
            items_xml = ""
            for item in source.items:
                items_xml += (
                    f"    <item code=\"{escape(str(item.unique_code))}\">\n"
                    f"      <name>{escape(str(item.name))}</name>\n"
                    f"      <gross_weight>{item.brutto}</gross_weight>\n"
                    f"      <net_weight>{item.netto}</net_weight>\n"
                    f"    </item>\n"
                )
            content = (
                f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                f"<receipt code=\"{escape(str(source.unique_code))}\" name=\"{escape(str(source.name))}\">\n"
                f"  <gross_weight>{source.gross_weight}</gross_weight>\n"
                f"  <net_weight>{source.net_weight}</net_weight>\n"
                f"  <items>\n{items_xml}  </items>\n"
                f"</receipt>"
            )

        elif isinstance(source, nomenclature_model):
            grp_name = source.group.name if source.group else ""
            rng_name = source.range.name if source.range else ""
            content = (
                f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                f"<nomenclature code=\"{escape(str(source.unique_code))}\">\n"
                f"  <name>{escape(str(source.name))}</name>\n"
                f"  <full_name>{escape(str(source.full_name))}</full_name>\n"
                f"  <group>{escape(str(grp_name))}</group>\n"
                f"  <range>{escape(str(rng_name))}</range>\n"
                f"</nomenclature>"
            )

        elif isinstance(source, range_model):
            base_name = source.base.name if source.base else "Базовая"
            content = (
                f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                f"<range code=\"{escape(str(source.unique_code))}\">\n"
                f"  <name>{escape(str(source.name))}</name>\n"
                f"  <conversion_factor>{source.conversion_factor}</conversion_factor>\n"
                f"  <base>{escape(str(base_name))}</base>\n"
                f"</range>"
            )
        else:
            raise arguments_exception(
                "source",
                f"Неподдерживаемый тип источника данных: {type(source).__name__}"
            )

        result = report_result_dto()
        result.text = content
        return result
