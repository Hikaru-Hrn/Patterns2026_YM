from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model


class text_report(abstract_report):
    """Реализация текстового представления отчета."""

    def build(self, source) -> report_result_dto:
        """Формирует текстовый отчет по переданной доменной сущности.

        :param source: receipt_model, nomenclature_model или range_model.
        :return: report_result_dto с заполненным текстовым представлением.
        """
        if isinstance(source, receipt_model):
            header = "Код | Наименование | Брутто | Нетто "
            data = ""
            for item in source.items:
                data += f"{item.unique_code} | {item.name} | {item.brutto} | {item.netto}\n"
            content = f"{header}\n{data.rstrip()}"
            if len(source.items) > 0:
                content += f"\nИтого брутто: {source.gross_weight} | Итого нетто: {source.net_weight}"

        elif isinstance(source, nomenclature_model):
            grp_name = source.group.name if source.group else ""
            rng_name = source.range.name if source.range else ""
            content = (
                f"Код: {source.unique_code}\n"
                f"Наименование: {source.name}\n"
                f"Полное наименование: {source.full_name}\n"
                f"Группа: {grp_name}\n"
                f"Единица измерения: {rng_name}"
            )

        elif isinstance(source, range_model):
            base_name = source.base.name if source.base else "Базовая"
            content = (
                f"Код: {source.unique_code}\n"
                f"Наименование: {source.name}\n"
                f"Коэффициент пересчета: {source.conversion_factor}\n"
                f"Базовая единица: {base_name}"
            )
        else:
            raise arguments_exception(
                "source",
                f"Неподдерживаемый тип источника данных: {type(source).__name__}"
            )

        result = report_result_dto()
        result.text = content
        return result
