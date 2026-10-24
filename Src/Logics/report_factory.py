from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.settings_manager import settings_manager
from Src.Logics.text_report import text_report
from Src.Logics.xml_report import xml_report
from Src.Models.settings_model import settings_model


class report_factory(abstract_report_factory):
    """Фабрика для построения отчетов в различных форматах."""

    __mapping: dict[report_type_enum, abstract_report]
    __settings: settings_model

    def __init__(self, settings: settings_model = None):
        """Инициализирует фабрику отчетов и инкапсулирует настройки приложения.

        :param settings: Экземпляр settings_model. Если не передан — используются
            настройки из синглтона settings_manager.
        """
        if settings is not None:
            validator.validate(settings, settings_model, "settings")
            self.__settings = settings
        else:
            self.__settings = settings_manager().settings

        self.__mapping = {
            report_type_enum.TXT: text_report(),
            report_type_enum.CSV: csv_report(),
            report_type_enum.MARKDOWN: markdown_report(),
            report_type_enum.XML: xml_report(),
            report_type_enum.HTML: html_report(),
        }

    @property
    def settings(self) -> settings_model:
        """Возвращает инкапсулированные настройки приложения."""
        return self.__settings

    def create(self, report_type: report_type_enum) -> abstract_report:
        """Создает инстанс отчета для переданного типа.

        :param report_type: Значение report_type_enum.
        :return: Экземпляр реализации abstract_report.
        :raises arguments_exception: Если передан неподдерживаемый или неверный тип.
        """
        if not isinstance(report_type, report_type_enum) or report_type not in self.__mapping:
            raise arguments_exception(
                "report_type",
                f"Указанный тип отчета {report_type} не реализован",
            )

        return self.__mapping[report_type]

    def create_default(self) -> abstract_report:
        """Создает инстанс отчета по умолчанию на основе настроек response_format.

        :return: Экземпляр реализации abstract_report, соответствующий response_format из настроек.
        """
        default_format = self.__settings.response_format
        return self.create(default_format)
