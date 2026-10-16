from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class markdown_report(abstract_report):
    """Реализация формирования отчета в формате Markdown с бинарным выводом."""

    def build(self, source) -> report_result_dto:
        """Формирует отчет в формате Markdown и сохраняет результат в бинарном виде.

        :param source: receipt_model, nomenclature_model или range_model.
        :return: report_result_dto с заполненным свойством binary.
        """
        if isinstance(source, receipt_model):
            header = "| Код | Наименование | Брутто | Нетто |\n| :--- | :--- | :--- | :--- |"
            lines = [header]
            for item in source.items:
                lines.append(f"| {item.unique_code} | {item.name} | {item.brutto} | {item.netto} |")
            if len(source.items) > 0:
                lines.append(f"| **ИТОГО** | — | **{source.gross_weight}** | **{source.net_weight}** |")
            content = "\n".join(lines)

        elif isinstance(source, nomenclature_model):
            grp_name = source.group.name if source.group else ""
            rng_name = source.range.name if source.range else ""
            lines = [
                "| Поле | Значение |",
                "| :--- | :--- |",
                f"| Код | {source.unique_code} |",
                f"| Наименование | {source.name} |",
                f"| Полное наименование | {source.full_name} |",
                f"| Группа | {grp_name} |",
                f"| Единица измерения | {rng_name} |",
            ]
            content = "\n".join(lines)

        elif isinstance(source, range_model):
            base_name = source.base.name if source.base else "Базовая"
            lines = [
                "| Поле | Значение |",
                "| :--- | :--- |",
                f"| Код | {source.unique_code} |",
                f"| Наименование | {source.name} |",
                f"| Коэффициент пересчета | {source.conversion_factor} |",
                f"| Базовая единица | {base_name} |",
            ]
            content = "\n".join(lines)
        else:
            raise arguments_exception(
                "source",
                f"Неподдерживаемый тип источника данных: {type(source).__name__}"
            )

        result = report_result_dto()
        result.binary = list(content.encode("utf-8"))
        return result
