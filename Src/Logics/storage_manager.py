from typing import get_args

from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception, operation_exception
from Src.Core.validator import validator
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.settings_manager import settings_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import recipe_row_model
from Src.Models.warehouse_model import warehouse_model


class storage_manager(abstract_manager):
    """Singleton-хранилище доменных справочников в оперативной памяти.

    Хранит списки: групп номенклатуры, единиц измерения, номенклатуры,
    складов и технологических карт (рецептов).
    Гарантирует уникальность каждого элемента по его имени или уникальному коду.
    """

    _instance = None
    _initialized: bool = False

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(storage_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """Однократная инициализация списков хранилища."""
        if self._initialized:
            return

        super().__init__()
        # Списки для хранения доменных моделей
        self._groups: list = []
        self._ranges: list = []
        self._nomenclatures: list = []
        self._warehouses: list = []
        self._recipes: list = []

        self._data: dict = {}
        self._is_loaded: bool = False
        self._initialized = True

    # -------------------------------------------------------------------------
    # Обеспечение уникальности и методы добавления
    # -------------------------------------------------------------------------

    @staticmethod
    def _is_unique(items: list, candidate) -> bool:
        """Проверяет уникальность элемента в переданном списке.

        Сравнивает сначала по unique_code, затем по наименованию (name).
        """
        if candidate is None:
            return False

        # Проверка по unique_code (унаследованному от abstract_model)
        candidate_code = getattr(candidate, "unique_code", None)
        if candidate_code:
            if any(getattr(item, "unique_code", None) == candidate_code for item in items):
                return False

        # Проверка по наименованию
        candidate_name = getattr(candidate, "name", None)
        if candidate_name:
            if any(getattr(item, "name", None) == candidate_name for item in items):
                return False

        # Прямое сравнение объектов
        return all(item != candidate for item in items)

    def add_warehouse(self, item: warehouse_model) -> bool:
        """Добавляет склад, если склада с таким именем/кодом еще нет."""
        validator.validate(item, warehouse_model)
        if self._is_unique(self._warehouses, item):
            self._warehouses.append(item)
            return True
        return False

    def add_range(self, item: range_model) -> bool:
        """Добавляет единицу измерения, если ее еще нет в списке."""
        validator.validate(item, range_model)
        if self._is_unique(self._ranges, item):
            self._ranges.append(item)
            return True
        return False

    def add_group(self, item: group_model) -> bool:
        """Добавляет группу номенклатуры, исключая дубликаты."""
        validator.validate(item, group_model)
        if self._is_unique(self._groups, item):
            self._groups.append(item)
            return True
        return False

    def add_nomenclature(self, item: nomenclature_model) -> bool:
        """Добавляет товарную позицию с проверкой уникальности."""
        validator.validate(item, nomenclature_model)
        if self._is_unique(self._nomenclatures, item):
            self._nomenclatures.append(item)
            return True
        return False

    def add_recipe(self, item: receipt_model) -> bool:
        """Добавляет технологическую карту (рецепт) с проверкой уникальности."""
        validator.validate(item, receipt_model)
        if self._is_unique(self._recipes, item):
            self._recipes.append(item)
            return True
        return False

    # -------------------------------------------------------------------------
    # Поиск по имени для связывания моделей между собой
    # -------------------------------------------------------------------------

    def _find_group_by_name(self, name: str) -> group_model:
        """Ищет объект группы по наименованию."""
        for g in self._groups:
            if g.name == name:
                return g
        return None

    def _find_range_by_name(self, name: str) -> range_model:
        """Ищет объект единицы измерения по наименованию."""
        for r in self._ranges:
            if r.name == name:
                return r
        return None

    def _find_recipe_by_name(self, name: str) -> receipt_model:
        """Ищет объект технологической карты по наименованию."""
        for rec in self._recipes:
            if rec.name == name:
                return rec
        return None

    def _resolve_collection(self, entity_type: str) -> tuple[list, type]:
        """Определяет список хранения и класс доменной модели по строковому коду типа.

        :param entity_type: Строковый ключ типа сущности.
        :return: Кортеж (список элементов хранилища, класс модели).
        :raises arguments_exception: Если тип сущности пустой или не распознан.
        """
        if not isinstance(entity_type, str) or not entity_type.strip():
            raise arguments_exception("entity_type", "Тип сущности не может быть пустым")

        clean_type = entity_type.strip().lower()
        mapping = {
            "group": (self._groups, group_model),
            "groups": (self._groups, group_model),
            "group_model": (self._groups, group_model),
            "группа": (self._groups, group_model),
            "группа_номенклатуры": (self._groups, group_model),
            "range": (self._ranges, range_model),
            "ranges": (self._ranges, range_model),
            "range_model": (self._ranges, range_model),
            "единица_измерения": (self._ranges, range_model),
            "единица": (self._ranges, range_model),
            "unit": (self._ranges, range_model),
            "units": (self._ranges, range_model),
            "nomenclature": (self._nomenclatures, nomenclature_model),
            "nomenclatures": (self._nomenclatures, nomenclature_model),
            "nomenclature_model": (self._nomenclatures, nomenclature_model),
            "номенклатура": (self._nomenclatures, nomenclature_model),
            "warehouse": (self._warehouses, warehouse_model),
            "warehouses": (self._warehouses, warehouse_model),
            "warehouse_model": (self._warehouses, warehouse_model),
            "storage_model": (self._warehouses, warehouse_model),
            "склад": (self._warehouses, warehouse_model),
            "receipt": (self._recipes, receipt_model),
            "recipe": (self._recipes, receipt_model),
            "recipes": (self._recipes, receipt_model),
            "receipt_model": (self._recipes, receipt_model),
            "рецепт": (self._recipes, receipt_model),
            "технологическая_карта": (self._recipes, receipt_model),
        }

        if clean_type not in mapping:
            raise arguments_exception(
                "entity_type",
                f"Неподдерживаемый тип сущности '{entity_type}'. Допустимые: group, range, nomenclature, warehouse, receipt"
            )
        return mapping[clean_type]

    def get_collection(self, entity_type: str) -> list:
        """Возвращает коллекцию доменных сущностей указанного типа."""
        items, _ = self._resolve_collection(entity_type)
        return items

    def find_entity(self, entity_type: str, code: str):
        """Ищет доменную сущность по типу и коду (unique_code или name).

        :param entity_type: Тип сущности (group, range, nomenclature, warehouse, receipt).
        :param code: Уникальный код или наименование сущности.
        :return: Экземпляр сущности или None.
        :raises arguments_exception: Если тип сущности не распознан.
        """
        items, _ = self._resolve_collection(entity_type)
        clean_code = str(code).strip()

        for item in items:
            if getattr(item, "unique_code", None) == clean_code:
                return item

        for item in items:
            if getattr(item, "name", None) == clean_code:
                return item

        return None

    @staticmethod
    def _find_in_list(items: list, ref):
        """Находит существующий объект в списке по unique_code или name."""
        if ref is None:
            return None
        ref_code = getattr(ref, "unique_code", None)
        if isinstance(ref_code, str) and ref_code.strip():
            for item in items:
                if getattr(item, "unique_code", None) == ref_code.strip():
                    return item
        ref_name = getattr(ref, "name", None)
        if isinstance(ref_name, str) and ref_name.strip():
            for item in items:
                if getattr(item, "name", None) == ref_name.strip():
                    return item
        return None

    def is_entity_referenced(self, target) -> bool:
        """Проверяет, связана ли доменная сущность с любой другой доменной сущностью в хранилище.

        :param target: Проверяемый экземпляр доменной сущности.
        :return: True, если на сущность ссылается другая сущность, иначе False.
        """
        if target is None:
            return False

        code = getattr(target, "unique_code", None)

        def _matches(ref) -> bool:
            return ref is not None and (ref is target or getattr(ref, "unique_code", None) == code)

        if isinstance(target, group_model):
            return any(_matches(nom.group) for nom in self._nomenclatures)

        if isinstance(target, range_model):
            if any(_matches(r.base) for r in self._ranges if r is not target):
                return True
            if any(_matches(nom.range) for nom in self._nomenclatures):
                return True
            return any(_matches(row.range) for rec in self._recipes for row in rec.rows)

        if isinstance(target, nomenclature_model):
            if any(_matches(rec.dish) for rec in self._recipes):
                return True
            return any(_matches(row.nomenclature) for rec in self._recipes for row in rec.rows)

        if isinstance(target, receipt_model):
            return any(
                _matches(row.sub_recipe)
                for rec in self._recipes
                if rec is not target
                for row in rec.rows
            )

        return False

    def _validate_and_bind_entity(self, candidate, current_target=None) -> None:
        """Проверяет обязательные поля сущности и привязывает ссылки к объектам из хранилища."""
        candidate.name = candidate.name

        if isinstance(candidate, warehouse_model):
            candidate.address = candidate.address
            return

        if isinstance(candidate, group_model):
            return

        if isinstance(candidate, range_model):
            candidate.conversion_factor = candidate.conversion_factor
            if candidate.base is not None:
                found_base = self._find_in_list(self._ranges, candidate.base)
                if found_base is None:
                    raise operation_exception("Базовая единица измерения не найдена в хранилище")
                if found_base is current_target or found_base.unique_code == candidate.unique_code:
                    raise operation_exception("Единица измерения не может ссылаться сама на себя")
                candidate.base = found_base
            return

        if isinstance(candidate, nomenclature_model):
            candidate.full_name = candidate.full_name
            if candidate.group is None:
                raise arguments_exception("group", "Не указана группа номенклатуры")
            found_group = self._find_in_list(self._groups, candidate.group)
            if found_group is None:
                raise operation_exception("Связанная группа номенклатуры не найдена в хранилище")
            candidate.group = found_group

            if candidate.range is None:
                raise arguments_exception("range", "Не указана единица измерения номенклатуры")
            found_range = self._find_in_list(self._ranges, candidate.range)
            if found_range is None:
                raise operation_exception("Связанная единица измерения не найдена в хранилище")
            candidate.range = found_range
            return

        if isinstance(candidate, receipt_model):
            if candidate.dish is None:
                raise arguments_exception("dish", "Не указано выходное блюдо рецепта")
            found_dish = self._find_in_list(self._nomenclatures, candidate.dish)
            if found_dish is None:
                raise operation_exception("Выходная номенклатура рецепта не найдена в хранилище")
            candidate.dish = found_dish

            bound_rows = []
            for row in candidate.rows:
                if row.sub_recipe is not None:
                    found_sub = self._find_in_list(self._recipes, row.sub_recipe)
                    if found_sub is None:
                        raise operation_exception("Вложенный рецепт строки не найден в хранилище")
                    if found_sub is current_target or found_sub.unique_code == candidate.unique_code:
                        raise operation_exception("Рецепт не может включать сам себя")
                    row.sub_recipe = found_sub
                elif row.nomenclature is not None:
                    found_nom = self._find_in_list(self._nomenclatures, row.nomenclature)
                    if found_nom is None:
                        raise operation_exception("Номенклатура строки рецепта не найдена в хранилище")
                    row.nomenclature = found_nom
                else:
                    raise arguments_exception("row", "Строка рецепта должна содержать номенклатуру или вложенный рецепт")

                if row.range is not None:
                    found_row_range = self._find_in_list(self._ranges, row.range)
                    if found_row_range is None:
                        raise operation_exception("Единица измерения строки рецепта не найдена в хранилище")
                    row.range = found_row_range
                elif row.sub_recipe is not None and row.sub_recipe.dish is not None:
                    row.range = row.sub_recipe.dish.range
                else:
                    raise arguments_exception("range", "Не указана единица измерения строки рецепта")

                bound_rows.append(row)
            candidate.rows = bound_rows

    def create_entity(self, entity_type: str, payload: dict):
        """Создает и добавляет новую доменную сущность из JSON-словаря с проверкой корректности."""
        items, model_cls = self._resolve_collection(entity_type)
        if not isinstance(payload, dict) or len(payload) == 0:
            raise arguments_exception("payload", "Тело запроса должно быть непустым JSON-объектом")

        candidate = deserialize_factory().Convert(payload, model_cls)
        self._validate_and_bind_entity(candidate)

        if not self._is_unique(items, candidate):
            raise operation_exception("Сущность с таким кодом или наименованием уже существует")

        items.append(candidate)
        return candidate

    def update_entity(self, entity_type: str, code: str, payload: dict):
        """Обновляет существующую доменную сущность с проверкой связей и уникальности."""
        items, model_cls = self._resolve_collection(entity_type)
        if not isinstance(payload, dict) or len(payload) == 0:
            raise arguments_exception("payload", "Тело запроса должно быть непустым JSON-объектом")

        target = self.find_entity(entity_type, code)
        if target is None:
            return None

        new_code = payload.get("unique_code")
        if new_code is not None:
            if not isinstance(new_code, str) or not new_code.strip():
                raise arguments_exception("unique_code", "Уникальный код не может быть пустым")
            new_code = new_code.strip()
            if new_code != target.unique_code:
                if self.is_entity_referenced(target):
                    raise operation_exception(
                        "Запрещено менять код сущности, так как она связана с другой доменной сущностью"
                    )
                if any(getattr(item, "unique_code", None) == new_code for item in items if item is not target):
                    raise operation_exception(f"Сущность с кодом '{new_code}' уже существует")

        merged = {**convert_factory().Convert(target), **payload}
        merged["unique_code"] = new_code if new_code is not None else target.unique_code

        candidate = deserialize_factory().Convert(merged, model_cls)
        self._validate_and_bind_entity(candidate, current_target=target)

        if any(getattr(item, "name", None) == candidate.name for item in items if item is not target):
            raise operation_exception(f"Сущность с наименованием '{candidate.name}' уже существует")

        target.unique_code = candidate.unique_code
        target.name = candidate.name

        if isinstance(target, warehouse_model):
            target.address = candidate.address
        elif isinstance(target, range_model):
            target.conversion_factor = candidate.conversion_factor
            target.base = candidate.base
        elif isinstance(target, nomenclature_model):
            target.full_name = candidate.full_name
            target.group = candidate.group
            target.range = candidate.range
        elif isinstance(target, receipt_model):
            target.dish = candidate.dish
            target.rows = candidate.rows
            if candidate.comments:
                target.comments = candidate.comments

        return target

    def delete_entity(self, entity_type: str, code: str) -> bool:
        """Удаляет доменную сущность по коду или имени, если она не связана с другими сущностями."""
        items, _ = self._resolve_collection(entity_type)
        target = self.find_entity(entity_type, code)
        if target is None:
            return False

        if self.is_entity_referenced(target):
            raise operation_exception(
                "Запрещено удалять сущность, так как она связана с другой доменной сущностью"
            )

        items.remove(target)
        return True

    # -------------------------------------------------------------------------
    # Загрузка и конвертация (полиморфизм abstract_manager)
    # -------------------------------------------------------------------------

    def load(self, file_name: str = "") -> None:
        """Инициирует формирование первичных данных при первом старте."""
        self.first_start(file_name)

    def convert(self) -> bool:
        """Формирует первичный набор доменных данных в памяти через фабричные методы.

        Создает единицы измерения, склады, группы номенклатуры, номенклатурные
        позиции и технологические карты (рецепты) с полуфабрикатами и упаковкой.
        Гарантирует уникальность каждого элемента.

        :return: True, если данные успешно сформированы.
        """
        try:
            # --- 1. Единицы измерения (через фабричные методы create_*) ---
            unit_g = range_model.create_gram()
            unit_kg = range_model.create_kilogram(unit_g)
            unit_pcs = range_model.create_piece()
            unit_ml = range_model.create_milliliter()

            self.add_range(unit_g)
            self.add_range(unit_kg)
            self.add_range(unit_pcs)
            self.add_range(unit_ml)

            # --- 2. Склады (через фабричный метод create) ---
            wh_main = warehouse_model.create("Основной склад", "г. Москва, ул. Складская, 1")
            wh_kitchen = warehouse_model.create("Кухня/Производство", "г. Москва, Цех 2")
            self.add_warehouse(wh_main)
            self.add_warehouse(wh_kitchen)

            # --- 3. Группы номенклатуры (через фабричный метод create) ---
            grp_ingredients = group_model.create("Ингредиенты")
            grp_semi = group_model.create("Полуфабрикаты")
            grp_dishes = group_model.create("Готовые блюда")
            grp_packaging = group_model.create("Тара и упаковка")

            self.add_group(grp_ingredients)
            self.add_group(grp_semi)
            self.add_group(grp_dishes)
            self.add_group(grp_packaging)

            # --- 4. Номенклатура (через фабричный метод create) ---
            # Сырьевые ингредиенты
            nom_flour = nomenclature_model.create(
                "Мука пшеничная",
                "Мука пшеничная высший сорт",
                grp_ingredients,
                unit_g
            )
            nom_butter = nomenclature_model.create(
                "Сливочное масло",
                "Сливочное масло 82.5%",
                grp_ingredients,
                unit_g
            )
            nom_sugar = nomenclature_model.create(
                "Сахар",
                "Сахар белый кристаллический",
                grp_ingredients,
                unit_g
            )
            nom_egg = nomenclature_model.create(
                "Яйцо куриное",
                "Яйцо куриное категории С0",
                grp_ingredients,
                unit_pcs
            )

            # Полуфабрикат
            nom_dough = nomenclature_model.create(
                "Песочное тесто",
                "Песочное тесто (полуфабрикат кулинарный)",
                grp_semi,
                unit_g
            )

            # Тара и упаковка
            nom_box = nomenclature_model.create(
                "Коробка крафтовая",
                "Коробка крафтовая для кондитерских изделий",
                grp_packaging,
                unit_pcs
            )

            # Готовая продукция
            nom_cookies_packaged = nomenclature_model.create(
                "Песочное печенье",
                "Песочное печенье в крафтовой упаковке",
                grp_dishes,
                unit_pcs
            )

            self.add_nomenclature(nom_flour)
            self.add_nomenclature(nom_butter)
            self.add_nomenclature(nom_sugar)
            self.add_nomenclature(nom_egg)
            self.add_nomenclature(nom_dough)
            self.add_nomenclature(nom_box)
            self.add_nomenclature(nom_cookies_packaged)

            # --- 5. Технологические карты / Рецепты (через фабричный метод create) ---
            # Рецепт 1: Полуфабрикат «Песочное тесто»
            recipe_dough = receipt_model.create(
                name="Песочное тесто",
                dish=nom_dough,
                rows=[
                    recipe_row_model.create(nom_flour, unit_g, gross_weight=250.0, net_weight=250.0),
                    recipe_row_model.create(nom_butter, unit_g, gross_weight=150.0, net_weight=150.0),
                    recipe_row_model.create(nom_sugar, unit_g, gross_weight=100.0, net_weight=100.0),
                    recipe_row_model.create(nom_egg, unit_pcs, gross_weight=60.0, net_weight=50.0),
                ],
                comments="Приготовление пластичного песочного теста"
            )
            self.add_recipe(recipe_dough)

            # Рецепт 2: Готовое блюдо с полуфабрикатом и упаковкой (принцип 'блюдо в блюде')
            recipe_cookies = receipt_model.create(
                name="Песочное печенье в упаковке",
                dish=nom_cookies_packaged,
                rows=[
                    recipe_row_model.create(recipe_dough, unit_g),
                    recipe_row_model.create(nom_box, unit_pcs, gross_weight=40.0, net_weight=40.0),
                ],
                comments="Выпекание печенья из полуфабриката теста и упаковка в крафтовую коробку"
            )
            self.add_recipe(recipe_cookies)

            self._is_loaded = True
            return True
        except Exception:
            self._is_loaded = False
            return False

    # -------------------------------------------------------------------------
    # Логика: Первый старт системы (генерация данных под рецепт)
    # -------------------------------------------------------------------------

    def first_start(self, file_name: str = "") -> bool:
        """Формирует первичный набор справочников при первом старте.

        Проверяет флаг first_launch_flag в settings_manager.
        Если True:
        - Формирует первичные данные (вызывает convert());
        - Переключает флаг first_launch_flag в False.
        Если False:
        - Повторное формирование блокируется, возвращает False.

        :param file_name: Путь к файлу настроек (опционально).
        :return: True, если первичные данные успешно сформированы.
        """
        mgr = settings_manager()
        if not mgr.is_loaded:
            mgr.load(file_name)

        # Если первый старт отключен — ничего не делаем
        if not mgr.settings.first_launch_flag:
            return False

        res = self.convert()
        if res:
            mgr.settings.first_launch_flag = False
        return res

    # -------------------------------------------------------------------------
    # Свойства доступа (геттеры)
    # -------------------------------------------------------------------------

    @property
    def collection_models(self) -> dict:
        """Возвращает схему коллекций: имя свойства -> класс модели по аннотациям геттеров."""
        result = {}
        for name, attribute in type(self).__dict__.items():
            if isinstance(attribute, property) and attribute.fget is not None:
                args = get_args(attribute.fget.__annotations__.get("return"))
                if args:
                    result[name] = args[0]
        return result

    @property
    def warehouses(self) -> list[warehouse_model]:
        """Возвращает список зарегистрированных складов."""
        return self._warehouses

    @property
    def ranges(self) -> list[range_model]:
        """Возвращает список зарегистрированных единиц измерения."""
        return self._ranges

    @property
    def units(self) -> list:
        """Возвращает список зарегистрированных единиц измерения (синоним ranges)."""
        return self._ranges

    @property
    def groups(self) -> list[group_model]:
        """Возвращает список зарегистрированных групп номенклатуры."""
        return self._groups

    @property
    def nomenclatures(self) -> list[nomenclature_model]:
        """Возвращает список зарегистрированных позиций номенклатуры."""
        return self._nomenclatures

    @property
    def recipes(self) -> list[receipt_model]:
        """Возвращает список зарегистрированных технологических карт (рецептов)."""
        return self._recipes