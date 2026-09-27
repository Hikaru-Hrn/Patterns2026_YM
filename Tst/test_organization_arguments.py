import pytest

from Src.Core.exception import (
    arguments_exception,
    length_exception,
    max_length_exception,
    validation_exception,
)
from Src.Models.organization_model import organization_model

VALID_INN = "7707083893"
VALID_BIC = "044525225"
VALID_ACCOUNT = "40702810900000000000"
VALID_OWNER = "ООО"


def _make_organization(**kwargs) -> organization_model:
    """
    Хелпер: создаёт организацию с корректными реквизитами,
    переопределяя переданные поля.

    :param kwargs: переопределяемые поля (inn, bic, account, owner).
    :return: экземпляр organization_model.
    """
    defaults = dict(
        name="ООО Ромашка",
        inn=VALID_INN,
        bic=VALID_BIC,
        account=VALID_ACCOUNT,
        owner=VALID_OWNER,
    )
    defaults.update(kwargs)
    return organization_model(**defaults)


def test_valid_result_organization_model_inn_correct():
    """
    Проверяет, что корректный ИНН принимается без исключений.

    1. Создать organization_model с корректным inn.
    2. Прочитать свойство inn.

    <expected>inn == переданному значению</expected>
    """
    org = _make_organization(inn=VALID_INN)
    assert org.inn == VALID_INN


@pytest.mark.parametrize("value", [None, 123, [], {}, True, 1.5, object()])
def test_invalid_result_organization_model_inn_type_arguments_exception(value):
    """
    Проверяет, что не-строка в inn даёт arguments_exception.

    1. Передать в inn значение не-строкового типа.
    2. Ожидается arguments_exception.

    <expected>arguments_exception</expected>
    """
    with pytest.raises(arguments_exception):
        _make_organization(inn=value)


@pytest.mark.parametrize("value", [
    "",
    "12345",
    "123456789",
    "12345678901",
    "123456789012",
    "1" * 20,
])
def test_invalid_result_organization_model_inn_length_exception(value):
    """
    Проверяет, что неверная длина ИНН даёт length_exception.

    1. Передать в inn строку длиной не 10.
    2. Ожидается length_exception.

    <expected>length_exception</expected>
    """
    with pytest.raises(length_exception):
        _make_organization(inn=value)


@pytest.mark.parametrize("value", [
    "abcdefghij",
    "770708389a",
    "a707083893",
    "7707 83893",
    "77070-3893",
    "770708389.",
])
def test_invalid_result_organization_model_inn_not_digits_validation_exception(value):
    """
    Проверяет, что ИНН из нецифровых символов даёт
    validation_exception.

    1. Передать в inn 10 символов, среди которых есть нецифры.
    2. Ожидается validation_exception.

    <expected>validation_exception</expected>
    """
    with pytest.raises(validation_exception):
        _make_organization(inn=value)


@pytest.mark.parametrize("value", [
    "7707083894",
    "7707083890",
    "1234567890",
    "0000000001",
])
def test_invalid_result_organization_model_inn_bad_checksum_validation_exception(value):
    """
    Проверяет, что ИНН из 10 цифр с неверной контрольной
    суммой даёт validation_exception.

    1. Передать 10 цифр с неверной контрольной суммой.
    2. Ожидается validation_exception.

    <expected>validation_exception</expected>
    """
    with pytest.raises(validation_exception):
        _make_organization(inn=value)


def test_valid_result_organization_model_bic_correct():
    """
    Проверяет, что корректный БИК принимается без исключений.

    1. Создать organization_model с корректным bic.
    2. Прочитать свойство bic.

    <expected>bic == переданному значению</expected>
    """
    org = _make_organization(bic=VALID_BIC)
    assert org.bic == VALID_BIC


@pytest.mark.parametrize("value", [None, 123, [], {}, True, 1.5, object()])
def test_invalid_result_organization_model_bic_type_arguments_exception(value):
    """
    Проверяет, что не-строка в bic даёт arguments_exception.

    1. Передать в bic значение не-строкового типа.
    2. Ожидается arguments_exception.

    <expected>arguments_exception</expected>
    """
    with pytest.raises(arguments_exception):
        _make_organization(bic=value)


@pytest.mark.parametrize("value", [
    "",
    "12345678",
    "1234567890",
    "12345678901",
    "1" * 20,
])
def test_invalid_result_organization_model_bic_length_exception(value):
    """
    Проверяет, что неверная длина БИК даёт length_exception.

    1. Передать в bic строку длиной не 9.
    2. Ожидается length_exception.

    <expected>length_exception</expected>
    """
    with pytest.raises(length_exception):
        _make_organization(bic=value)


@pytest.mark.parametrize("value", [
    "abcdefghi",
    "04452522a",
    "a44525225",
    "0445 2525",
    "04452-225",
])
def test_invalid_result_organization_model_bic_not_digits_validation_exception(value):
    """
    Проверяет, что БИК из нецифровых символов даёт
    validation_exception.

    1. Передать в bic 9 символов с нецифрами.
    2. Ожидается validation_exception.

    <expected>validation_exception</expected>
    """
    with pytest.raises(validation_exception):
        _make_organization(bic=value)


def test_valid_result_organization_model_account_correct():
    """
    Проверяет, что корректный счёт принимается без исключений.

    1. Создать organization_model с корректным account.
    2. Прочитать свойство account.

    <expected>account == переданному значению</expected>
    """
    org = _make_organization(account=VALID_ACCOUNT)
    assert org.account == VALID_ACCOUNT


@pytest.mark.parametrize("value", [None, 123, [], {}, True, 1.5, object()])
def test_invalid_result_organization_model_account_type_arguments_exception(value):
    """
    Проверяет, что не-строка в account даёт arguments_exception.

    1. Передать в account значение не-строкового типа.
    2. Ожидается arguments_exception.
    <expected>arguments_exception</expected>
    """
    with pytest.raises(arguments_exception):
        _make_organization(account=value)


@pytest.mark.parametrize("value", [
    "",
    "12345",
    "1" * 19,
    "1" * 21,
    "1" * 30,
])
def test_invalid_result_organization_model_account_length_exception(value):
    """
    Проверяет, что неверная длина счёта даёт length_exception.

    1. Передать в account строку длиной не 20.
    2. Ожидается length_exception.
    <expected>length_exception</expected>
    """
    with pytest.raises(length_exception):
        _make_organization(account=value)


@pytest.mark.parametrize("value", [
    "4070281090000000000a",
    "a0702810900000000000",
    "4070 810900000000000",
    "4070-810900000000000",
])
def test_invalid_result_organization_model_account_not_digits_validation_exception(value):
    """
    Проверяет, что счёт из нецифровых символов даёт
    validation_exception.

    1. Передать в account 20 символов с нецифрами.
    2. Ожидается validation_exception.
    <expected>validation_exception</expected>
    """
    with pytest.raises(validation_exception):
        _make_organization(account=value)


@pytest.mark.parametrize("value", [
    "40702810900000000001",
    "1" * 20,
    "99999999999999999999",
])
def test_invalid_result_organization_model_account_bad_checksum_validation_exception(value):
    """
    Проверяет, что счёт из 20 цифр с неверной контрольной
    суммой даёт validation_exception.

    1. Передать 20 цифр с неверной КС относительно bic.
    2. Ожидается validation_exception.

    <expected>validation_exception</expected>
    """
    with pytest.raises(validation_exception):
        _make_organization(account=value)


@pytest.mark.parametrize("value", [None, 123, [], {}, True, 1.5, object()])
def test_invalid_result_organization_model_owner_type_arguments_exception(value):
    """
    Проверяет, что не-строка в owner даёт arguments_exception.

    1. Передать в owner значение не-строкового типа.
    2. Ожидается arguments_exception.

    <expected>arguments_exception</expected>
    """
    with pytest.raises(arguments_exception):
        _make_organization(owner=value)


def test_invalid_result_organization_model_owner_max_length_exception():
    """
    Проверяет, что owner длиннее 50 символов даёт max_length_exception.

    1. Передать в owner строку длиной 51.
    2. Ожидается max_length_exception.
    <expected>max_length_exception</expected>
    """
    with pytest.raises(max_length_exception):
        _make_organization(owner="А" * 51)