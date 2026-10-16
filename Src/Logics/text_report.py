from Src.Core.abstract_report import abstract_report
from Src.Core.entity_model import entity_model
from Src.Models.receipt_model import receipt_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto


"""
Реализация текстового представления отчета по рецепту
"""


class text_report(abstract_report):
    # Рецепт
    __receipt: receipt_model

    """
    Переопределенный метод формирования отчета
    """

    def build(self, source) -> report_result_dto:
        validator.validate(source, receipt_model)
        self.__receipt = source

        header = "Код | Наименование | Брутто | Нетто "
        data = ""

        for item in self.__receipt.items:
            data += f"{item.unique_code} | {item.name} | {item.brutto} | {item.netto}"

        result = report_result_dto()
        result.text = f"{header}\n{data}"

        return result
