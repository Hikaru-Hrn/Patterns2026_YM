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
        """Загружает данные из settings_manager и выполняет конвертацию."""
        mgr = settings_manager()
        if not mgr.is_loaded:
            mgr.load(file_name)

        self._data = mgr.data
        self._is_loaded = self.convert()

    def convert(self) -> bool:
        """Преобразует словарь self._data в экземпляры доменных моделей."""
        try:
            if not isinstance(self._data, dict):
                return False

            # 1. Загрузка единиц измерения и установка базовых связей
            ranges_data = self._data.get("ranges", [])
            range_dict = {}
            for item in ranges_data:
                r = range_model(
                    name=item["name"],
                    conversion_factor=item.get("conversion_factor", item.get("conversation_factor", 1.0)),
                    base=None
                )
                if self.add_range(r):
                    range_dict[r.name] = r

            # Вторым проходом связываем базовые единицы
            for item in ranges_data:
                base_name = item.get("base")
                if base_name and item["name"] in range_dict and base_name in range_dict:
                    range_dict[item["name"]].base = range_dict[base_name]

            # 2. Загрузка групп номенклатуры
            for item in self._data.get("groups", []):
                self.add_group(group_model(name=item["name"]))

            # 3. Загрузка складов
            for item in self._data.get("warehouses", self._data.get("warehouse", [])):
                self.add_warehouse(warehouse_model(name=item["name"], address=item.get("address", "")))

            # 4. Загрузка номенклатуры с поиском связанных объектов
            for item in self._data.get("nomenclature", self._data.get("nomenclatures", [])):
                gr = self._find_group_by_name(item.get("group", ""))
                rn = self._find_range_by_name(item.get("range", ""))

                if gr is None or rn is None:
                    raise arguments_exception("nomenclature", f"Не найдена группа или единица для '{item.get('name')}'")

                nom = nomenclature_model(
                    name=item["name"],
                    full_name=item.get("full_name", item["name"]),
                    group=gr,
                    range=rn
                )
                self.add_nomenclature(nom)

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

        Если в настройках first_launch_flag == True:
        - Создаются единицы измерения (грамм, килограмм, штука, миллилитр);
        - Создаются склады (Основной склад, Кухня);
        - Создаются группы (Ингредиенты, Готовые блюда);
        - Создается базовая номенклатура для технологической карты рецепта;
        - Флаг first_launch_flag переключается в False.
        """
        mgr = settings_manager()
        if not mgr.is_loaded:
            mgr.load(file_name)

        # Если первый старт отключен — ничего не делаем
        if not mgr.settings.first_launch_flag:
            return False

        # --- Единицы измерения ---
        unit_g = range_model(name="грамм", conversion_factor=1.0, base=None)
        unit_kg = range_model(name="килограмм", conversion_factor=1000.0, base=unit_g)
        unit_pcs = range_model(name="штука", conversion_factor=1.0, base=None)
        unit_ml = range_model(name="миллилитр", conversion_factor=1.0, base=None)

        self.add_range(unit_g)
        self.add_range(unit_kg)
        self.add_range(unit_pcs)
        self.add_range(unit_ml)

        # --- Склады ---
        wh_main = warehouse_model(name="Основной склад", address="г. Москва, ул. Складская, 1")
        wh_kitchen = warehouse_model(name="Кухня/Производство", address="г. Москва, Цех 2")
        self.add_warehouse(wh_main)
        self.add_warehouse(wh_kitchen)

        # --- Группы ---
        grp_ingredients = group_model(name="Ингредиенты")
        grp_dishes = group_model(name="Готовые блюда")
        self.add_group(grp_ingredients)
        self.add_group(grp_dishes)

        # --- Номенклатура для рецепта печенья ---
        self.add_nomenclature(nomenclature_model(
            name="Мука пшеничная",
            full_name="Мука пшеничная высший сорт",
            group=grp_ingredients,
            range=unit_g
        ))
        self.add_nomenclature(nomenclature_model(
            name="Сливочное масло",
            full_name="Сливочное масло 82.5%",
            group=grp_ingredients,
            range=unit_g
        ))
        self.add_nomenclature(nomenclature_model(
            name="Сахар",
            full_name="Сахар белый кристаллический",
            group=grp_ingredients,
            range=unit_g
        ))
        self.add_nomenclature(nomenclature_model(
            name="Яйцо куриное",
            full_name="Яйцо куриное категории С0",
            group=grp_ingredients,
            range=unit_pcs
        ))
        self.add_nomenclature(nomenclature_model(
            name="Песочное печенье",
            full_name="Песочное печенье классическое",
            group=grp_dishes,
            range=unit_pcs
        ))

        # Сбрасываем флаг первого запуска
        mgr.settings.first_launch_flag = False
        self._is_loaded = True
        return True

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