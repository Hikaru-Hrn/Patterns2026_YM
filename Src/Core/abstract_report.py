from abc import ABC, abstractmethod
from urllib.parse import quote
from fastapi import Response

from Src.Core.abstract_model import abstract_model
from Src.Dtos.report_result_dto import report_result_dto


class abstract_report(ABC):
    """Абстрактный класс для формирования отчетов."""

    @abstractmethod
    def build(self, source: abstract_model) -> report_result_dto:
        """Сформировать отчет по переданной доменной сущности.

        :param source: Экземпляр abstract_model.
        :return: Заполненный report_result_dto.
        """
        pass

    @property
    @abstractmethod
    def media_type(self) -> str:
        """Возвращает MIME-тип для HTTP-ответа."""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Возвращает расширение файла отчета (без точки)."""
        pass

    @property
    def is_attachment(self) -> bool:
        """Флаг необходимости скачивания отчета в виде файла в API."""
        return False

    def create_response(self, result: report_result_dto, filename_prefix: str = "report") -> Response:
        """Полиморфно формирует HTTP-ответ FastAPI на основе типа и конфигурации отчета.

        :param result: Результат построения отчета (report_result_dto).
        :param filename_prefix: Префикс имени скачиваемого файла (при наличии).
        :return: Экземпляр Response FastAPI.
        """
        if self.is_attachment:
            ext = self.file_extension
            content_bytes = bytes(result.binary) if result.binary else result.text.encode("utf-8")
            encoded_filename = quote(f"{filename_prefix}.{ext}")
            disposition = f'attachment; filename="report.{ext}"; filename*=utf-8\'\'{encoded_filename}'
            return Response(
                content=content_bytes,
                media_type=self.media_type,
                headers={"Content-Disposition": disposition},
            )

        return Response(
            content=result.text,
            media_type=self.media_type,
        )
