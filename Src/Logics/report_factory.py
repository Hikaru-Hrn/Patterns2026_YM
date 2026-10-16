from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.text_report import text_report

"""
Реализация фабрики для построения отчетов
"""
class report_factory(abstract_report_factory):
    # Маппинг тип отчета и его реализация
    __mapping: dict[report_type_enum, abstract_report]

    def __init__(self):
        self.__mapping = {
            report_type_enum.TXT: text_report(),
        }


    def create(self, report_type: report_type_enum) -> abstract_report:
        if report_type not in self.__mapping.keys():
            raise arguments_exception(
                "report_type",
                f"Указанный тип отчета {report_type} не реализован",
            )

        return self.__mapping[report_type]