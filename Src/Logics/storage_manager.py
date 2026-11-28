from datetime import datetime
from typing import get_args

from Src.Core.abstract_manager import abstract_manager
from Src.Core.event_type import event_type
from Src.Core.validator import validator
from Src.Logics.filter_index import filter_index
from Src.Logics.observer import observer
from Src.Logics.settings_manager import settings_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.log_entry_model import log_entry_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_row_model import recipe_row_model
from Src.Models.transaction_model import transaction_model
from Src.Models.warehouse_model import warehouse_model


class storage_manager(abstract_manager):
    """Singleton-хранилище доменных справочников в оперативной памяти.

    Хранит списки: групп номенклатуры, единиц измерения, номенклатуры,
    складов, технологических карт (рецептов) и транзакций.
    Гарантирует уникальность каждого элемента по его имени или уникальному коду.
    Поддерживает быструю фильтрацию через filter_index.
    """

    _instance = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(storage_manager, cls).__new__(cls)
        return cls._instance

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
        self._transactions: list = []
        self._log_entries: list[log_entry_model] = []

        self._data: dict = {}
        self._is_loaded: bool = False
        self.__filter_index: filter_index | None = None
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
            self._invalidate_filter_index()
            return True
        return False

    def add_range(self, item: range_model) -> bool:
        """Добавляет единицу измерения, если ее еще нет в списке."""
        validator.validate(item, range_model)
        if self._is_unique(self._ranges, item):
            self._ranges.append(item)
            self._invalidate_filter_index()
            return True
        return False

    def add_group(self, item: group_model) -> bool:
        """Добавляет группу номенклатуры, исключая дубликаты."""
        validator.validate(item, group_model)
        if self._is_unique(self._groups, item):
            self._groups.append(item)
            self._invalidate_filter_index()
            return True
        return False

    def add_nomenclature(self, item: nomenclature_model) -> bool:
        """Добавляет товарную позицию с проверкой уникальности."""
        validator.validate(item, nomenclature_model)
        if self._is_unique(self._nomenclatures, item):
            self._nomenclatures.append(item)
            self._invalidate_filter_index()
            return True
        return False

    def add_recipe(self, item: receipt_model) -> bool:
        """Добавляет технологическую карту (рецепт) с проверкой уникальности."""
        validator.validate(item, receipt_model)
        if self._is_unique(self._recipes, item):
            self._recipes.append(item)
            self._invalidate_filter_index()
            return True
        return False

    def add_transaction(self, item: transaction_model) -> bool:
        """Добавляет транзакцию движения номенклатуры."""
        validator.validate(item, transaction_model)
        if self._is_unique(self._transactions, item):
            self._transactions.append(item)
            self._invalidate_filter_index()
            event = event_type.storage_income() if item.value > 0 else event_type.storage_expense()
            observer.create(
                event,
                {
                    "operation": "add_transaction",
                    "warehouse": item.warehouse.name if item.warehouse else "",
                    "nomenclature": item.nomenclature.name if item.nomenclature else "",
                    "value": item.value,
                },
            )
            return True
        return False

    def _invalidate_filter_index(self) -> None:
        """Сбрасывает кэшированный индекс фильтрации при изменении данных."""
        self.__filter_index = None

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

    # -------------------------------------------------------------------------
    # Загрузка и конвертация (полиморфизм abstract_manager)
    # -------------------------------------------------------------------------

    def load(self, file_name: str = "") -> None:
        """Инициирует формирование первичных данных при первом старте."""
        self.first_start(file_name)

    def convert(self) -> bool:
        """Формирует первичный набор доменных данных в памяти через фабричные методы.

        Создает единицы измерения, склады, группы номенклатуры, номенклатурные
        позиции, технологические карты (рецепты) и транзакции.
        Гарантирует уникальность каждого элемента.

        :return: True, если данные успешно сформированы.
        """
        try:
            # Очищаем транзакции, так как convert формирует их заново
            self._transactions = []
            self._invalidate_filter_index()

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

            # --- 6. Транзакции (движения номенклатуры для формирования ОСВ) ---
            transactions = [
                transaction_model.create(wh_main, nom_flour, unit_g, 1000.0, datetime(2026, 11, 1, 10, 0, 0)),
                transaction_model.create(wh_main, nom_flour, unit_g, -200.0, datetime(2026, 11, 5, 12, 0, 0)),
                transaction_model.create(wh_kitchen, nom_sugar, unit_g, 500.0, datetime(2026, 11, 2, 9, 0, 0)),
                transaction_model.create(wh_kitchen, nom_sugar, unit_g, -150.0, datetime(2026, 11, 6, 14, 0, 0)),
                transaction_model.create(wh_main, nom_egg, unit_pcs, 120.0, datetime(2026, 11, 3, 8, 0, 0)),
                transaction_model.create(wh_main, nom_egg, unit_pcs, -20.0, datetime(2026, 11, 7, 11, 0, 0)),
            ]
            for transaction in transactions:
                self.add_transaction(transaction)

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

        # Перед первичным формированием очищаем хранилище,
        # чтобы избежать дублирования данных при повторных запусках
        self._groups = []
        self._ranges = []
        self._nomenclatures = []
        self._warehouses = []
        self._recipes = []
        self._transactions = []
        self._invalidate_filter_index()

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
        result.pop("log_entries", None)
        return result

    def get_filter_index(self) -> filter_index:
        """Возвращает индекс доменных сущностей для быстрой фильтрации.

        Индекс строится лениво при первом обращении и инвалидируется
        при изменении любой коллекции хранилища.

        :return: Экземпляр filter_index.
        """
        if self.__filter_index is None:
            self.__filter_index = filter_index()
            self.__filter_index.build(self._get_collections_dict())
        return self.__filter_index

    def _get_collections_dict(self) -> dict[str, list]:
        """Возвращает словарь всех коллекций хранилища."""
        return {
            "groups": self._groups,
            "ranges": self._ranges,
            "nomenclatures": self._nomenclatures,
            "warehouses": self._warehouses,
            "recipes": self._recipes,
            "transactions": self._transactions,
            "log_entries": self._log_entries,
        }

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

    @property
    def transactions(self) -> list[transaction_model]:
        """Возвращает список зарегистрированных транзакций движения номенклатуры."""
        return self._transactions

    @property
    def log_entries(self) -> list[log_entry_model]:
        """Возвращает список записей лога."""
        return self._log_entries

    def add_log_entry(self, entry: log_entry_model) -> bool:
        """Добавляет запись лога в хранилище.

        :param entry: Запись лога.
        :return: True, если запись добавлена.
        """
        validator.validate(entry, log_entry_model)
        self._log_entries.append(entry)
        self._invalidate_filter_index()
        return True