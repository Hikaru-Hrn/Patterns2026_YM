from html import escape

from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class html_report(abstract_report):
    """Реализация формирования отчета в формате HTML со структурированным текстовым выводом."""

    def build(self, source) -> report_result_dto:
        """Формирует структурированный HTML-отчет.

        :param source: receipt_model, nomenclature_model или range_model.
        :return: report_result_dto со свойством text.
        """
        if isinstance(source, receipt_model):
            rows_html = ""
            for item in source.items:
                rows_html += (
                    f"    <tr>\n"
                    f"      <td>{escape(str(item.unique_code))}</td>\n"
                    f"      <td>{escape(str(item.name))}</td>\n"
                    f"      <td>{item.brutto}</td>\n"
                    f"      <td>{item.netto}</td>\n"
                    f"    </tr>\n"
                )
            content = (
                f"<!DOCTYPE html>\n<html>\n<head><meta charset=\"utf-8\"><title>Рецепт: {escape(str(source.name))}</title></head>\n<body>\n"
                f"<h2>Технологическая карта: {escape(str(source.name))}</h2>\n"
                f"<table border=\"1\" cellpadding=\"5\" cellspacing=\"0\">\n"
                f"  <thead>\n    <tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr>\n  </thead>\n"
                f"  <tbody>\n{rows_html}  </tbody>\n"
                f"  <tfoot>\n    <tr><th>ИТОГО</th><th>—</th><th>{source.gross_weight}</th><th>{source.net_weight}</th></tr>\n  </tfoot>\n"
                f"</table>\n</body>\n</html>"
            )

        elif isinstance(source, nomenclature_model):
            grp_name = source.group.name if source.group else ""
            rng_name = source.range.name if source.range else ""
            content = (
                f"<!DOCTYPE html>\n<html>\n<head><meta charset=\"utf-8\"><title>Номенклатура</title></head>\n<body>\n"
                f"<h2>Номенклатура: {escape(str(source.name))}</h2>\n"
                f"<table border=\"1\" cellpadding=\"5\" cellspacing=\"0\">\n"
                f"  <tr><th>Код</th><td>{escape(str(source.unique_code))}</td></tr>\n"
                f"  <tr><th>Наименование</th><td>{escape(str(source.name))}</td></tr>\n"
                f"  <tr><th>Полное наименование</th><td>{escape(str(source.full_name))}</td></tr>\n"
                f"  <tr><th>Группа</th><td>{escape(str(grp_name))}</td></tr>\n"
                f"  <tr><th>Единица измерения</th><td>{escape(str(rng_name))}</td></tr>\n"
                f"</table>\n</body>\n</html>"
            )

        elif isinstance(source, range_model):
            base_name = source.base.name if source.base else "Базовая"
            content = (
                f"<!DOCTYPE html>\n<html>\n<head><meta charset=\"utf-8\"><title>Единица измерения</title></head>\n<body>\n"
                f"<h2>Единица измерения: {escape(str(source.name))}</h2>\n"
                f"<table border=\"1\" cellpadding=\"5\" cellspacing=\"0\">\n"
                f"  <tr><th>Код</th><td>{escape(str(source.unique_code))}</td></tr>\n"
                f"  <tr><th>Наименование</th><td>{escape(str(source.name))}</td></tr>\n"
                f"  <tr><th>Коэффициент</th><td>{source.conversion_factor}</td></tr>\n"
                f"  <tr><th>Базовая единица</th><td>{escape(str(base_name))}</td></tr>\n"
                f"</table>\n</body>\n</html>"
            )
        else:
            raise arguments_exception(
                "source",
                f"Неподдерживаемый тип источника данных: {type(source).__name__}"
            )

        result = report_result_dto()
        result.text = content
        return result
