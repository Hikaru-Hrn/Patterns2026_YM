import pytest

from Src.Core.exception import (
    base_exception,
    arguments_exception,
    length_exception,
    max_length_exception,
    validation_exception,
)
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model



VALID_INN = "7707083893"
VALID_BIC = "044525225"
VALID_ACCOUNT = "40702810900000000000"


def _make_organization(**kwargs) -> organization_model:
    """Хелпер: организация с корректными реквизитами."""
    defaults = dict(
        name="ООО Ромашка",
        inn=VALID_INN,
        bic=VALID_BIC,
        account=VALID_ACCOUNT,
        owner="ООО",
    )
    defaults.update(kwargs)
    return organization_model(**defaults)



def test_valid_result_all_domain_exceptions_inherit_base_exception():
    """
    Проверяет, что каждый внутренний класс исключений
    унаследован от base_exception.

    Ожидаемый результат:
    все перечисленные классы являются наследниками base_exception.
    """
    for cls in (
        arguments_exception,
        length_exception,
        max_length_exception,
        validation_exception,
    ):
        assert issubclass(cls, base_exception)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: _make_organization(inn="123"),
        lambda: _make_organization(inn="abcdefghij"),
        lambda: _make_organization(bic="abcdefghi"),
        lambda: _make_organization(account="abcdefghij" * 2),
        lambda: _make_organization(owner=None),
        lambda: range_model("грамм", None),
        lambda: range_model("грамм", 0),
        lambda: warehouse_model("Склад", None),
        lambda: warehouse_model("Склад", 123),
        lambda: group_model(None),
        lambda: nomenclature_model(name="Товар", full_name=None),
    ],
)
def test_invalid_result_no_builtin_exceptions(factory):
    """
    Проверяет, что при валидации не возбуждаются встроенные
    исключения (ValueError, TypeError, AttributeError,
    IndexError, KeyError).

    Ожидаемый результат:
    возбуждается только base_exception и его наследники.
    """
    with pytest.raises(base_exception) as exc_info:
        factory()

    assert not isinstance(
        exc_info.value,
        (ValueError, TypeError, AttributeError, IndexError, KeyError),
    )



def test_valid_result_catch_all_domain_errors_via_base_exception():
    """
    Проверяет, что все доменные ошибки можно поймать одним
    except base_exception — это и есть суть требования п.11.

    Ожидаемый результат:
    все ошибки являются наследниками base_exception.
    """
    bad_cases = [
        # organization_model
        lambda: _make_organization(inn=None),
        lambda: _make_organization(inn="123"),
        lambda: _make_organization(inn="abcdefghij"),
        lambda: _make_organization(inn="7707083894"),
        lambda: _make_organization(bic=None),
        lambda: _make_organization(bic="123"),
        lambda: _make_organization(bic="abcdefghi"),
        lambda: _make_organization(account=None),
        lambda: _make_organization(account="123"),
        lambda: _make_organization(account="40702810900000000001"),
        lambda: _make_organization(owner=None),
        lambda: _make_organization(owner="А" * 51),
        # range_model
        lambda: range_model("грамм", None),
        lambda: range_model("грамм", 0),
        lambda: range_model("a" * 51, 1),
        # warehouse_model
        lambda: warehouse_model("Склад", None),
        lambda: warehouse_model("Склад", "a" * 256),
        # group_model
        lambda: group_model(None),
        lambda: group_model("a" * 51),
        # nomenclature_model
        lambda: nomenclature_model(name="Товар", full_name=None),
        lambda: nomenclature_model(name="a" * 51),
        lambda: nomenclature_model(name="Товар", group="Молочные"),
        lambda: nomenclature_model(name="Товар", range="кг"),
    ]

    for factory in bad_cases:
        with pytest.raises(base_exception):
            factory()



def test_valid_result_exception_has_field_and_message():
    """
    Проверяет, что внутренние исключения несут заполненные
    атрибуты field и message.

    Ожидаемый результат:
    field и message не являются пустыми строками.
    """
    with pytest.raises(arguments_exception) as exc_info:
        _make_organization(inn=None)

    assert exc_info.value.field == "inn"
    assert exc_info.value.message != ""