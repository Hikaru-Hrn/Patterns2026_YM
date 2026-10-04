from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception, operation_exception
from Src.Core.validator import validator
from Src.Logics.settings_manager import settings_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


class storage_manager(abstract_manager):
    """Singleton-хранилище доменных справочников в оперативной памяти.

    Хранит списки: групп номенклатуры, единиц измерения, номенклатуры и складов.
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

    # -------------------------------------------------------------------------
    # Загрузка и конвертация (полиморфизм abstract_manager)
    # -------------------------------------------------------------------------

    def load(self, file_name: str = "") -> None:
        """Инициирует формирование первичных данных при первом старте."""
        self.first_start(file_name)

    def convert(self) -> bool:
        """Формирует первичный набор доменных данных в памяти (реализация абстрактного метода).

        Создает единицы измерения, склады, группы номенклатуры и номенклатурные позиции под рецепт.
        Гарантирует уникальность каждого элемента.

        :return: True, если данные успешно сформированы.
        """
        try:
            # --- Единицы измерения ---
            unit_g = range_model("грамм", 1.0)
            unit_kg = range_model("килограмм", 1000.0, unit_g)
            unit_pcs = range_model("штука", 1.0)
            unit_ml = range_model("миллилитр", 1.0)

            self.add_range(unit_g)
            self.add_range(unit_kg)
            self.add_range(unit_pcs)
            self.add_range(unit_ml)

            # --- Склады ---
            wh_main = warehouse_model("Основной склад", "г. Москва, ул. Складская, 1")
            wh_kitchen = warehouse_model("Кухня/Производство", "г. Москва, Цех 2")
            self.add_warehouse(wh_main)
            self.add_warehouse(wh_kitchen)

            # --- Группы ---
            grp_ingredients = group_model("Ингредиенты")
            grp_dishes = group_model("Готовые блюда")
            self.add_group(grp_ingredients)
            self.add_group(grp_dishes)

            # --- Номенклатура (создание через свойства без логики в конструкторе) ---
            nom_flour = nomenclature_model()
            nom_flour.name = "Мука пшеничная"
            nom_flour.full_name = "Мука пшеничная высший сорт"
            nom_flour.group = grp_ingredients
            nom_flour.range = unit_g
            self.add_nomenclature(nom_flour)

            nom_butter = nomenclature_model()
            nom_butter.name = "Сливочное масло"
            nom_butter.full_name = "Сливочное масло 82.5%"
            nom_butter.group = grp_ingredients
            nom_butter.range = unit_g
            self.add_nomenclature(nom_butter)

            nom_sugar = nomenclature_model()
            nom_sugar.name = "Сахар"
            nom_sugar.full_name = "Сахар белый кристаллический"
            nom_sugar.group = grp_ingredients
            nom_sugar.range = unit_g
            self.add_nomenclature(nom_sugar)

            nom_egg = nomenclature_model()
            nom_egg.name = "Яйцо куриное"
            nom_egg.full_name = "Яйцо куриное категории С0"
            nom_egg.group = grp_ingredients
            nom_egg.range = unit_pcs
            self.add_nomenclature(nom_egg)

            nom_cookie = nomenclature_model()
            nom_cookie.name = "Песочное печенье"
            nom_cookie.full_name = "Песочное печенье классическое"
            nom_cookie.group = grp_dishes
            nom_cookie.range = unit_pcs
            self.add_nomenclature(nom_cookie)

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
    def warehouses(self) -> list:
        """Возвращает список зарегистрированных складов."""
        return self._warehouses

    @property
    def ranges(self) -> list:
        """Возвращает список зарегистрированных единиц измерения."""
        return self._ranges

    @property
    def units(self) -> list:
        """Возвращает список зарегистрированных единиц измерения (синоним ranges)."""
        return self._ranges

    @property
    def groups(self) -> list:
        """Возвращает список зарегистрированных групп номенклатуры."""
        return self._groups

    @property
    def nomenclatures(self) -> list:
        """Возвращает список зарегистрированных позиций номенклатуры."""
        return self._nomenclatures