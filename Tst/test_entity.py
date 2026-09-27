import pytest

from Src.Core.abstract_model import abstract_model
from Src.Core.entity_model import entity_model
from Src.Core.exception import arguments_exception


class dummy_entity(abstract_model):
    """Заглушка для проверки поведения базового класса без доменной логики."""
    pass


class dummy_entity_model(entity_model):
    """Заглушка для проверки поведения entity_model без доменной логики."""
    pass


def test_valid_result_abstract_model_unique_code_not_empty():
    """
    Проверяет автоматическую генерацию уникального кода
    у объекта базовой модели.

    Ожидаемый результат:
    unique_code не является пустой строкой.
    """
    entity = dummy_entity()

    assert entity.unique_code != ""


def test_valid_result_abstract_model_unique_code_is_unique():
    """
    Проверяет уникальность автоматически сгенерированных
    кодов у разных объектов базовой модели.

    Ожидаемый результат:
    два разных объекта получают разные значения unique_code.
    """
    en1 = dummy_entity()
    en2 = dummy_entity()

    assert en1 != en2


def test_valid_result_abstract_model_equality_by_unique_code():
    """
    Проверяет сравнение объектов базовой модели по unique_code.

    Ожидаемый результат:
    объекты равны, если их unique_code совпадает.
    """
    entity1 = dummy_entity()
    entity2 = dummy_entity()

    entity1.unique_code = "fff"
    entity2.unique_code = "fff"

    assert entity1 == entity2


def test_invalid_result_entity_model_name_empty():
    """
    Проверяет запрет установки пустого наименования
    у объекта entity_model.

    Ожидаемый результат:
    при передаче пустой строки возникает arguments_exception.
    """
    entity = dummy_entity_model()

    with pytest.raises(arguments_exception):
        entity.name = ""


def test_invalid_result_entity_model_name_whitespace():
    """
    Проверяет запрет установки наименования, состоящего
    только из пробелов, у объекта entity_model.

    Ожидаемый результат:
    при передаче строки только из пробелов возникает arguments_exception.
    """
    entity = dummy_entity_model()

    with pytest.raises(arguments_exception):
        entity.name = "   "


@pytest.mark.parametrize("value", [None, 123, [], {}, True])
def test_invalid_result_entity_model_name_type(value):
    """
    Проверяет обработку некорректных типов значения name.

    Ожидаемый результат:
    для каждого значения, не являющегося непустой строкой,
    возникает arguments_exception.
    """
    entity = dummy_entity_model()

    with pytest.raises(arguments_exception):
        entity.name = value