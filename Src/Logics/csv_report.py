from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class csv_report(abstract_report):
    """Реализация формирования отчета в формате CSV с бинарным выводом."""

    def build(self, source) -> report_result_dto:
        """Формирует отчет в формате CSV и сохраняет результат в бинарном виде.

        :param source: receipt_model, nomenclature_model или range_model.
        :return: report_result_dto с заполненным свойством binary.
        """
        if isinstance(source, receipt_model):
            header = "Код;Наименование;Брутто;Нетто"
            lines = [header]
            for item in source.items:
                lines.append(f"{item.unique_code};{item.name};{item.brutto};{item.netto}")
            if len(source.items) > 0:
                lines.append(f"ИТОГО;-;{source.gross_weight};{source.net_weight}")
            content = "\n".join(lines)

        elif isinstance(source, nomenclature_model):
            header = "Код;Наименование;Полное наименование;Группа;Единица измерения"
            grp_name = source.group.name if source.group else ""
            rng_name = source.range.name if source.range else ""
            row = f"{source.unique_code};{source.name};{source.full_name};{grp_name};{rng_name}"
            content = f"{header}\n{row}"

        elif isinstance(source, range_model):
            header = "Код;Наименование;Коэффициент;Базовая единица"
            base_name = source.base.name if source.base else "Базовая"
            row = f"{source.unique_code};{source.name};{source.conversion_factor};{base_name}"
            content = f"{header}\n{row}"
        else:
            raise arguments_exception(
                "source",
                f"Неподдерживаемый тип источника данных: {type(source).__name__}"
            )

        result = report_result_dto()
        result.binary = list(content.encode("utf-8"))
        return result
