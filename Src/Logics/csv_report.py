from Src.Core.abstract_model import abstract_model
from Src.Core.abstract_report import abstract_report
from Src.Core.common import common
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto


class csv_report(abstract_report):
    """Реализация отчета в формате CSV со скачиванием файла."""

    @property
    def media_type(self) -> str:
        return "text/csv; charset=utf-8"

    @property
    def file_extension(self) -> str:
        return "csv"

    @property
    def is_attachment(self) -> bool:
        return True

    def build(self, source: abstract_model) -> report_result_dto:
        """Формирует отчет в формате CSV по метаданным любой сущности через common.

        :param source: Экземпляр доменной модели (наследник abstract_model).
        :return: report_result_dto с заполненным свойством binary.
        """
        validator.validate(source, abstract_model)

        headers = common.get_entity_header(source)
        table_data = common.get_entity_table(source)

        lines = []
        if table_data and len(table_data) > 0 and len(table_data[0].columns) > 0:
            # Для агрегата формируем строки табличной части
            lines.append(";".join(table_data[0].columns))
            for row in table_data:
                lines.append(";".join(row.values))
        else:
            # Для простой сущности формируем заголовок и значения
            lines.append(";".join([h.field for h in headers]))
            lines.append(";".join([h.value for h in headers]))

        content = "\n".join(lines).strip()
        result = report_result_dto()
        result.binary = list(content.encode("utf-8"))
        result.format = self.media_type
        return result
