from Src.Core.exception import (
    arguments_exception,
    max_length_exception,
    length_exception,
    validation_exception,
)


class validator:
    """Вспомогательный класс для централизованной валидации аргументов моделей."""

    @staticmethod
    def validate(value, type_, field="field", leng=None, max_len=None, document=None):
        """Проверяет тип, непустоту и ограничения длины аргумента.

        :param value: Проверяемое значение.
        :param type_: Ожидаемый тип данных.
        :param field: Имя поля для формирования ошибки.
        :param leng: Требуемая фиксированная длина (если задана).
        :param max_len: Максимально допустимая длина (если задана).
        :param document: Название реквизита для сообщения об ошибке.
        :raises arguments_exception: Если значение None, неверного типа или пустое (когда leng is None).
        :raises length_exception: Если задана фиксированная длина leng и она не совпадает.
        :raises max_length_exception: Если длина превышает max_len.
        """
        if value is None:
            raise arguments_exception(field, "Пустой аргумент")

        if not isinstance(value, type_):
            raise arguments_exception(field, "Некорректно переданный аргумент")

        if leng is not None:
            if len(str(value).strip()) != leng:
                raise length_exception(field, leng, document or field)
        else:
            if isinstance(value, str) and value.strip() == "":
                raise arguments_exception(field, "Пустой аргумент")

        if max_len is not None and len(str(value).strip()) > max_len:
            raise max_length_exception(field, max_len)

    @staticmethod
    def digit_validate(value, field="field"):
        """Проверяет, что строка содержит только цифры."""
        if value.isdigit() is False:
            raise validation_exception(field, "Аргумент содержит числовые значения")

    @staticmethod
    def check_inn(value):
        """Проверяет контрольную сумму 10-значного ИНН юридического лица."""
        total = (2 * int(value[0]) + 4 * int(value[1]) + 10 * int(value[2]) +
                 3 * int(value[3]) + 5 * int(value[4]) + 9 * int(value[5]) +
                 4 * int(value[6]) + 6 * int(value[7]) + 8 * int(value[8]))
        result = total % 11
        if result > 9:
            result %= 10
        if result != int(value[-1]):
            raise validation_exception("inn", "Некорректный ИНН!")

    @staticmethod
    def check_account(value, bic):
        """Проверяет контрольную сумму 20-значного расчетного счета с учетом БИК."""
        last = bic[-3:]
        new_value = last + value
        cnt = 1
        total = 0
        for i in range(23):
            match cnt:
                case 1:
                    total += 7 * int(new_value[i])
                    cnt += 1
                case 2:
                    total += 1 * int(new_value[i])
                    cnt += 1
                case 3:
                    total += 3 * int(new_value[i])
                    cnt = 1
        if total % 10 != 0:
            raise validation_exception("account", "Некорректный Счет!")

    @staticmethod
    def no_lower_that_zero_validate(value, field="field"):
        """Проверяет, что числовое значение строго больше нуля."""
        if value <= 0:
            raise arguments_exception(field, "Аргумент должен быть больше нуля")