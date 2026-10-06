import pytest

from Src.Core.exception import (
    arguments_exception,
    max_length_exception,
    length_exception,
    validation_exception,
)
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


# ============================================================
# group_model
# ============================================================

def test_valid_result_group_model_creation():
    """
    Проверяет успешное создание группы номенклатуры
    с корректным наименованием.

    Ожидаемый результат:
    объект создаётся, его name содержит переданное значение,
    а unique_code автоматически генерируется.
    """
    group = group_model("Молочная продукция")

    assert group.name == "Молочная продукция"
    assert group.unique_code != ""


def test_valid_result_group_model_name_change():
    """
    Проверяет успешное изменение наименования существующей
    группы номенклатуры.

    Ожидаемый результат:
    после присваивания новое значение сохраняется в свойстве name.
    """
    group = group_model("Молочная продукция")

    group.name = "Мясная продукция"

    assert group.name == "Мясная продукция"


def test_invalid_result_group_model_name_empty():
    """
    Проверяет запрет установки пустого наименования группы
    номенклатуры.

    Ожидаемый результат:
    при передаче пустой строки возникает arguments_exception.
    """
    group = group_model("Молочная продукция")

    with pytest.raises(arguments_exception):
        group.name = ""


def test_invalid_result_group_model_name_long():
    """
    Проверяет ограничение длины наименования группы номенклатуры.

    Ожидаемый результат:
    при передаче строки длиной более 50 символов
    возникает max_length_exception.
    """
    group = group_model("Молочная продукция")

    with pytest.raises(max_length_exception):
        group.name = "А" * 51


@pytest.mark.parametrize("value", [None, 123, [], {}, True])
def test_invalid_result_group_model_name_type(value):
    """
    Проверяет обработку некорректных типов значения name.

    Ожидаемый результат:
    для каждого значения, не являющегося непустой строкой,
    возникает arguments_exception.
    """
    group = group_model("Молочная продукция")

    with pytest.raises(arguments_exception):
        group.name = value


# ============================================================
# range_model
# ============================================================

def test_valid_result_range_model_creation():
    """
    Проверяет создание базовой единицы измерения.

    Ожидаемый результат:
    name сохраняется, base равен None,
    conversion_factor преобразуется в float.
    """
    unit = range_model("грамм")

    assert unit.name == "грамм"
    assert unit.base is None
    assert unit.conversion_factor == 1.0


def test_valid_result_range_model_base_creation():
    """
    Проверяет создание производной единицы измерения,
    связанной с базовой единицей.

    Ожидаемый результат:
    base содержит переданную базовую единицу,
    а conversion_factor содержит коэффициент пересчёта.
    """
    gram = range_model("грамм")
    kilogram = range_model("килограмм", 1000, gram)

    assert kilogram.name == "килограмм"
    assert kilogram.base == gram
    assert kilogram.conversion_factor == 1000.0


def test_valid_result_range_model_base_change():
    """
    Проверяет изменение базовой единицы измерения.

    Ожидаемый результат:
    после присваивания свойство base содержит новый объект
    range_model.
    """
    gram = range_model("грамм")
    kilogram = range_model("килограмм", 1000, gram)
    ton = range_model("тонна", 1000, kilogram)

    kilogram.base = ton

    assert kilogram.base == ton


def test_valid_result_range_model_conversion_factor_change():
    """
    Проверяет изменение коэффициента пересчёта.

    Ожидаемый результат:
    новое числовое значение сохраняется в conversion_factor
    и представляется как float.
    """
    unit = range_model("килограмм", 1000)

    unit.conversion_factor = 500

    assert unit.conversion_factor == 500.0



@pytest.mark.parametrize("value", [0, -1, -100, -0.5])
def test_invalid_result_range_model_conversion_factor_value(value):
    """
    Проверяет запрет нулевого и отрицательного коэффициента.

    Ожидаемый результат:
    при передаче значения, меньшего либо равного нулю,
    возникает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        range_model("килограмм", value)


@pytest.mark.parametrize("value", ["грамм", 1000, [], {}])
def test_invalid_result_range_model_base_type(value):
    """
    Проверяет запрет установки объекта, который не является
    range_model, в свойство base.

    Ожидаемый результат:
    возникает arguments_exception.
    """
    unit = range_model("килограмм", 1000)

    with pytest.raises(arguments_exception):
        unit.base = value


def test_valid_result_range_model_base_none():
    """
    Проверяет возможность отсутствия базовой единицы измерения.

    Ожидаемый результат:
    значение None принимается свойством base.
    """
    unit = range_model("грамм")

    unit.base = None

    assert unit.base is None


# nomenclature_model


def test_valid_result_nomenclature_model_creation():
    """
    Проверяет создание номенклатуры с группой и единицей измерения.

    Ожидаемый результат:
    все переданные значения сохраняются в соответствующих свойствах.
    """
    group = group_model("Молочная продукция")
    unit = range_model("грамм")

    nomenclature = nomenclature_model()
    nomenclature.name = "Молоко"
    nomenclature.full_name = "Молоко пастеризованное 3.2%"
    nomenclature.group = group
    nomenclature.range = unit

    assert nomenclature.name == "Молоко"
    assert nomenclature.full_name == "Молоко пастеризованное 3.2%"
    assert nomenclature.group == group
    assert nomenclature.range == unit


def test_valid_result_nomenclature_model_without_group_and_range():
    """
    Проверяет создание номенклатуры без группы и единицы измерения.

    Ожидаемый результат:
    group и range равны None.
    """
    nomenclature = nomenclature_model()
    nomenclature.name = "Молоко"
    nomenclature.full_name = "Молоко пастеризованное"

    assert nomenclature.full_name == "Молоко пастеризованное"
    assert nomenclature.name == "Молоко"
    assert nomenclature.group is None
    assert nomenclature.range is None


def test_valid_result_nomenclature_model_full_name_change():
    """
    Проверяет изменение полного наименования номенклатуры.

    Ожидаемый результат:
    новое значение сохраняется в full_name.
    """
    nomenclature = nomenclature_model()
    nomenclature.name = "Молоко"
    nomenclature.full_name = "Старое наименование"

    nomenclature.full_name = "Новое полное наименование"

    assert nomenclature.full_name == "Новое полное наименование"


def test_valid_result_nomenclature_model_group_change():
    """
    Проверяет изменение группы номенклатуры.

    Ожидаемый результат:
    свойство group содержит новую группу.
    """
    group1 = group_model("Молочная продукция")
    group2 = group_model("Мясная продукция")

    nomenclature = nomenclature_model()
    nomenclature.name = "Молоко"
    nomenclature.group = group1

    nomenclature.group = group2

    assert nomenclature.group == group2


def test_valid_result_nomenclature_model_range_change():
    """
    Проверяет изменение единицы измерения номенклатуры.

    Ожидаемый результат:
    свойство range содержит новую единицу измерения.
    """
    gram = range_model("грамм")
    kilogram = range_model("килограмм", 1000, gram)

    nomenclature = nomenclature_model()
    nomenclature.name = "Молоко"
    nomenclature.range = gram

    nomenclature.range = kilogram

    assert nomenclature.range == kilogram


@pytest.mark.parametrize("value", [None, 123, [], {}, True])
def test_invalid_result_nomenclature_model_full_name_type(value):
    """
    Проверяет тип значения full_name.

    Ожидаемый результат:
    при передаче значения, не являющегося строкой,
    возникает arguments_exception.
    """
    nomenclature = nomenclature_model()
    nomenclature.name = "Тест"

    with pytest.raises(arguments_exception):
        nomenclature.full_name = value


def test_invalid_result_nomenclature_model_full_name_long():
    """
    Проверяет ограничение длины полного наименования.

    Ожидаемый результат:
    строка длиной более 255 символов вызывает
    max_length_exception.
    """
    nomenclature = nomenclature_model()
    nomenclature.name = "Тест"

    with pytest.raises(max_length_exception):
        nomenclature.full_name = "А" * 256


def test_valid_result_nomenclature_model_full_name_255():
    """
    Проверяет граничное допустимое значение длины full_name.

    Ожидаемый результат:
    строка длиной ровно 255 символов принимается.
    """
    nomenclature = nomenclature_model()
    nomenclature.name = "A"

    nomenclature.full_name = "А" * 255

    assert len(nomenclature.full_name) == 255


@pytest.mark.parametrize("value", ["Молочная продукция", 123, [], {}, True])
def test_invalid_result_nomenclature_model_group_type(value):
    """
    Проверяет тип значения group.

    Ожидаемый результат:
    значение, не являющееся group_model или None,
    вызывает arguments_exception.
    """
    nomenclature = nomenclature_model()
    nomenclature.name = "Test"

    with pytest.raises(arguments_exception):
        nomenclature.group = value


@pytest.mark.parametrize("value", ["грамм", 1000, [], {}, True])
def test_invalid_result_nomenclature_model_range_type(value):
    """
    Проверяет тип значения range.

    Ожидаемый результат:
    значение, не являющееся range_model или None,
    вызывает arguments_exception.
    """
    nomenclature = nomenclature_model()
    nomenclature.name = "Тест"

    with pytest.raises(arguments_exception):
        nomenclature.range = value


# ============================================================
# warehouse_model
# ============================================================

def test_valid_result_warehouse_model_creation():
    """
    Проверяет создание склада с корректным наименованием
    и адресом помещения.

    Ожидаемый результат:
    name и address содержат переданные значения,
    unique_code автоматически создан.
    """
    warehouse = warehouse_model(
        "Основной склад",
        "ул. Ленина, 10",
    )

    assert warehouse.name == "Основной склад"
    assert warehouse.address == "ул. Ленина, 10"
    assert warehouse.unique_code != ""


def test_valid_result_warehouse_model_address_change():
    """
    Проверяет изменение адреса склада.

    Ожидаемый результат:
    новое значение сохраняется в свойстве address.
    """
    warehouse = warehouse_model(
        "Основной склад",
        "ул. Ленина, 10",
    )

    warehouse.address = "ул. Пушкина, 20"

    assert warehouse.address == "ул. Пушкина, 20"


def test_valid_result_warehouse_model_address_empty():
    """
    Проверяет создание склада с пустым адресом.

    Ожидаемый результат:
    согласно текущей реализации warehouse_model пустая
    строка принимается.
    """
    warehouse = warehouse_model("Основной склад", "")

    assert warehouse.address == ""


def test_valid_result_warehouse_model_address_255():
    """
    Проверяет граничное допустимое значение длины адреса.

    Ожидаемый результат:
    адрес длиной ровно 255 символов принимается.
    """
    warehouse = warehouse_model("Основной склад")

    warehouse.address = "А" * 255

    assert len(warehouse.address) == 255


def test_invalid_result_warehouse_model_address_long():
    """
    Проверяет ограничение длины адреса склада.

    Ожидаемый результат:
    адрес длиной более 255 символов вызывает
    max_length_exception.
    """
    warehouse = warehouse_model("Основной склад")

    with pytest.raises(max_length_exception):
        warehouse.address = "А" * 256


@pytest.mark.parametrize("value", [123, [], {}, True])
def test_invalid_result_warehouse_model_address_type(value):
    """
    Проверяет обработку некорректных типов адреса.

    Ожидаемый результат:
    для значения, не являющегося строкой, возникает
    arguments_exception.
    """
    warehouse = warehouse_model("Основной склад")

    with pytest.raises(arguments_exception):
        warehouse.address = value


# ============================================================
# organization_model
# ============================================================

VALID_INN = "7707083893"
VALID_BIC = "044525225"
VALID_ACCOUNT = "40702810900000000000"


def test_valid_result_organization_model_creation():
    """
    Проверяет создание организации с корректными банковскими
    реквизитами.

    Ожидаемый результат:
    все переданные реквизиты сохраняются в соответствующих
    свойствах организации.
    """
    organization = organization_model(
        "ООО Ромашка",
        VALID_INN,
        VALID_BIC,
        VALID_ACCOUNT,
        "Иванов Иван Иванович",
    )

    assert organization.name == "ООО Ромашка"
    assert organization.inn == VALID_INN
    assert organization.bic == VALID_BIC
    assert organization.account == VALID_ACCOUNT
    assert organization.owner == "Иванов Иван Иванович"


def test_valid_result_organization_model_inn_change():
    """
    Проверяет изменение ИНН на корректное значение.

    Ожидаемый результат:
    новое значение сохраняется в свойстве inn.
    """
    organization = organization_model(
        "ООО Ромашка",
        VALID_INN,
        VALID_BIC,
        VALID_ACCOUNT,
    )

    organization.inn = VALID_INN

    assert organization.inn == VALID_INN


def test_valid_result_organization_model_bic_change():
    """
    Проверяет изменение БИК на корректное значение.

    Ожидаемый результат:
    новое значение сохраняется в свойстве bic.
    """
    organization = organization_model(
        "ООО Ромашка",
        VALID_INN,
        VALID_BIC,
        VALID_ACCOUNT,
    )

    new_bic = "123456789"
    organization.bic = new_bic

    assert organization.bic == new_bic


def test_valid_result_organization_model_account_change():
    """
    Проверяет изменение расчётного счёта на корректное значение.

    Ожидаемый результат:
    новое значение сохраняется в свойстве account.
    """
    organization = organization_model(
        "ООО Ромашка",
        VALID_INN,
        VALID_BIC,
        VALID_ACCOUNT,
    )

    organization.account = VALID_ACCOUNT

    assert organization.account == VALID_ACCOUNT


def test_valid_result_organization_model_owner_change():
    """
    Проверяет изменение владельца организации.

    Ожидаемый результат:
    новое значение сохраняется в свойстве owner.
    """
    organization = organization_model(
        "ООО Ромашка",
        VALID_INN,
        VALID_BIC,
        VALID_ACCOUNT,
    )

    organization.owner = "Петров Петр Петрович"

    assert organization.owner == "Петров Петр Петрович"


@pytest.mark.parametrize(
    "value",
    [None, 123, [], {}, True],
)
def test_invalid_result_organization_model_inn_type(value):
    """
    Проверяет тип значения ИНН.

    Ожидаемый результат:
    при передаче значения, не являющегося строкой,
    возникает arguments_exception.
    """
    organization = organization_model.__new__(organization_model)

    with pytest.raises(arguments_exception):
        organization.inn = value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "123456789",
        "12345678901",
    ],
)
def test_invalid_result_organization_model_inn_length(value):
    """
    Проверяет ограничение длины ИНН текущей реализацией модели.

    Ожидаемый результат:
    значение, длина которого отличается от 10 символов,
    вызывает length_exception.
    """
    organization = organization_model.__new__(organization_model)

    with pytest.raises(length_exception):
        organization.inn = value


def test_invalid_result_organization_model_inn_validation():
    """
    Проверяет контрольную сумму ИНН.

    Ожидаемый результат:
    десятизначный ИНН с некорректной контрольной цифрой
    вызывает validation_exception.
    """
    organization = organization_model.__new__(organization_model)

    with pytest.raises(validation_exception):
        organization.inn = "7707083894"


@pytest.mark.parametrize(
    "value",
    [None, 123, [], {}, True],
)
def test_invalid_result_organization_model_bic_type(value):
    """
    Проверяет тип значения БИК.

    Ожидаемый результат:
    при передаче значения, не являющегося строкой,
    возникает arguments_exception.
    """
    organization = organization_model.__new__(organization_model)

    with pytest.raises(arguments_exception):
        organization.bic = value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "12345678",
        "1234567890",
    ],
)
def test_invalid_result_organization_model_bic_length(value):
    """
    Проверяет ограничение длины БИК.

    Ожидаемый результат:
    значение, длина которого отличается от 9 символов,
    вызывает length_exception.
    """
    organization = organization_model.__new__(organization_model)

    with pytest.raises(length_exception):
        organization.bic = value


@pytest.mark.parametrize(
    "value",
    [None, 123, [], {}, True],
)
def test_invalid_result_organization_model_account_type(value):
    """
    Проверяет тип значения расчётного счёта.

    Ожидаемый результат:
    при передаче значения, не являющегося строкой,
    возникает arguments_exception.
    """
    organization = organization_model.__new__(organization_model)
    organization.bic = VALID_BIC

    with pytest.raises(arguments_exception):
        organization.account = value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "1234567890123456789",
        "123456789012345678901",
    ],
)
def test_invalid_result_organization_model_account_length(value):
    """
    Проверяет ограничение длины расчётного счёта.

    Ожидаемый результат:
    значение, длина которого отличается от 20 символов,
    вызывает length_exception.
    """
    organization = organization_model.__new__(organization_model)
    organization.bic = VALID_BIC

    with pytest.raises(length_exception):
        organization.account = value


def test_invalid_result_organization_model_account_validation():
    """
    Проверяет контрольную сумму расчётного счёта.

    Ожидаемый результат:
    расчётный счёт с некорректной контрольной суммой
    вызывает validation_exception.
    """
    organization = organization_model.__new__(organization_model)
    organization.bic = VALID_BIC

    with pytest.raises(validation_exception):
        organization.account = "40702810900000000001"


def test_valid_result_organization_model_owner_50():
    """
    Проверяет граничное допустимое значение длины owner.

    Ожидаемый результат:
    строка длиной ровно 50 символов принимается.
    """
    organization = organization_model.__new__(organization_model)

    organization.owner = "А" * 50

    assert len(organization.owner) == 50


def test_invalid_result_organization_model_owner_long():
    """
    Проверяет ограничение длины owner.

    Ожидаемый результат:
    строка длиной более 50 символов вызывает
    max_length_exception.
    """
    organization = organization_model.__new__(organization_model)

    with pytest.raises(max_length_exception):
        organization.owner = "А" * 51


@pytest.mark.parametrize(
    "value",
    [None, 123, [], {}, True],
)
def test_invalid_result_organization_model_owner_type(value):
    """
    Проверяет тип значения owner.

    Ожидаемый результат:
    при передаче значения, не являющегося строкой,
    возникает arguments_exception.
    """
    organization = organization_model.__new__(organization_model)

    with pytest.raises(arguments_exception):
        organization.owner = value


# ============================================================
# Наследование entity_model / abstact_model
# ============================================================

def test_valid_result_entity_models_have_unique_code():
    """
    Проверяет автоматическую генерацию уникального кода
    у объектов доменных моделей.

    Ожидаемый результат:
    два разных объекта получают разные значения unique_code.
    """
    group1 = group_model("Группа 1")
    group2 = group_model("Группа 2")

    assert group1.unique_code != ""
    assert group2.unique_code != ""
    assert group1.unique_code != group2.unique_code


def test_valid_result_entity_model_unique_code_change():
    """
    Проверяет изменение unique_code через setter базового класса.

    Ожидаемый результат:
    переданное значение очищается от пробелов по краям
    и сохраняется в unique_code.
    """
    group = group_model("Группа")

    group.unique_code = "  test-code  "

    assert group.unique_code == "test-code"


def test_valid_result_entity_model_equal_objects():
    """
    Проверяет сравнение объектов через unique_code.

    Ожидаемый результат:
    два объекта считаются равными, если их unique_code совпадает.
    """
    group1 = group_model("Группа 1")
    group2 = group_model("Группа 2")

    group2.unique_code = group1.unique_code

    assert group1 == group2