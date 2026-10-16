# UML диаграммы для моделей данных, `settings_manager` и `storage_manager`

В данном документе представлены UML-диаграммы классов и последовательностей, описывающие архитектуру приложения, доменных моделей (включая технологические карты/рецепты, композицию «блюдо в блюде» с рекурсивным расчетом веса, фабричные методы), а также менеджеров настроек и хранилища данных.

---

## 1. Диаграмма классов (Class Diagram)

### 1.1. Mermaid

```mermaid
classDiagram
    class abstract_model {
        <<abstract>>
        -str __unique_code
        +unique_code() str
        +__eq__(value) bool
    }

    class entity_model {
        -str __name
        -int __max_len_name
        +name() str
    }

    class group_model {
        +__init__(name: str)
        +create(name: str)$ group_model
    }

    class range_model {
        -range_model __base
        -float __conversion_factor
        +base() range_model
        +conversion_factor() float
        +create(name: str, conversion_factor: float, base: range_model)$ range_model
        +create_gram()$ range_model
        +create_kilogram(base: range_model)$ range_model
        +create_piece()$ range_model
        +create_milliliter()$ range_model
    }

    class warehouse_model {
        -str __address
        -int __max_len_address
        +address() str
        +create(name: str, address: str)$ warehouse_model
    }

    class nomenclature_model {
        -str __full_name
        -int __full_name_max_length
        -group_model __group
        -range_model __range
        +__init__() void
        +full_name() str
        +group() group_model
        +range() range_model
        +create(name: str, full_name: str, group: group_model, range: range_model)$ nomenclature_model
    }

    class recipe_row_model {
        -nomenclature_model __nomenclature
        -receipt_model __sub_recipe
        -range_model __range
        -float __gross_weight
        -float __net_weight
        +nomenclature() nomenclature_model
        +sub_recipe() receipt_model
        +recipe() receipt_model
        +range() range_model
        +gross_weight() float
        +net_weight() float
        +create(item, range, gross_weight, net_weight)$ recipe_row_model
    }

    class receipt_model {
        -nomenclature_model __dish
        -list __rows
        -str __comments
        +dish() nomenclature_model
        +comments() str
        +rows() list
        +gross_weight() float
        +net_weight() float
        +add_row(row: recipe_row_model) bool
        +remove_row(row: recipe_row_model) bool
        +create(name: str, dish: nomenclature_model, rows: list, comments: str)$ receipt_model
    }

    class abstract_manager {
        <<abstract>>
        #str _file_name
        #bool _is_loaded
        #dict _data
        +load(file_name: str) void
        +convert() bool*
        +is_loaded() bool
    }

    class settings_manager {
        -settings_manager _instance$
        -bool _initialized$
        -str __default_file_name
        -settings_model _settings
        +__new__() settings_manager
        +load(file_name: str) void
        +convert() bool
        +settings() settings_model
        +data() dict
    }

    class storage_manager {
        -storage_manager _instance$
        -bool _initialized$
        -list _groups
        -list _ranges
        -list _nomenclatures
        -list _warehouses
        -list _recipes
        +__new__() storage_manager
        +load(file_name: str) void
        +convert() bool
        +first_start(file_name: str) bool
        +add_warehouse(item: warehouse_model) bool
        +add_range(item: range_model) bool
        +add_group(item: group_model) bool
        +add_nomenclature(item: nomenclature_model) bool
        +add_recipe(item: receipt_model) bool
        -_is_unique(items: list, candidate) bool$
        +warehouses() list
        +ranges() list
        +units() list
        +groups() list
        +nomenclatures() list
        +recipes() list
    }

    abstract_model <|-- entity_model : Наследование
    abstract_model <|-- recipe_row_model : Наследование
    entity_model <|-- warehouse_model : Наследование
    entity_model <|-- range_model : Наследование
    entity_model <|-- group_model : Наследование
    entity_model <|-- nomenclature_model : Наследование
    entity_model <|-- receipt_model : Наследование

    abstract_manager <|-- settings_manager : Наследование
    abstract_manager <|-- storage_manager : Наследование

    storage_manager ..> settings_manager : Singleton call
    storage_manager o-- "0..*" warehouse_model : Хранит
    storage_manager o-- "0..*" range_model : Хранит
    storage_manager o-- "0..*" group_model : Хранит
    storage_manager o-- "0..*" nomenclature_model : Хранит
    storage_manager o-- "0..*" receipt_model : Хранит

    nomenclature_model --> group_model : Группа
    nomenclature_model --> range_model : Ед. изм.
    range_model --> range_model : Базовая единица

    receipt_model *-- "1..*" recipe_row_model : Состав
    receipt_model --> nomenclature_model : Выходное блюдо/полуфабрикат
    recipe_row_model --> nomenclature_model : Номенклатура / тара
    recipe_row_model --> "0..1" receipt_model : Вложенный рецепт (блюдо в блюде)
    recipe_row_model --> range_model : Ед. изм.
```

### 1.2. PlantUML

```plantuml
@startuml
skinparam classAttributeIconSize 0

abstract class abstract_model {
    - __unique_code: str
    + unique_code: str
    + __eq__(value): bool
}

abstract class entity_model {
    - __name: str
    + name: str
}

class group_model {
    + {static} create(name: str): group_model
}

class range_model {
    - __base: range_model
    - __conversion_factor: float
    + base: range_model
    + conversion_factor: float
    + {static} create(name: str, factor: float, base: range_model): range_model
    + {static} create_gram(): range_model
    + {static} create_kilogram(base: range_model): range_model
    + {static} create_piece(): range_model
    + {static} create_milliliter(): range_model
}

class warehouse_model {
    - __address: str
    + address: str
    + {static} create(name: str, address: str): warehouse_model
}

class nomenclature_model {
    - __full_name: str
    - __group: group_model
    - __range: range_model
    + full_name: str
    + group: group_model
    + range: range_model
    + {static} create(name: str, full_name: str, group: group_model, range: range_model): nomenclature_model
}

class recipe_row_model {
    - __nomenclature: nomenclature_model
    - __sub_recipe: receipt_model
    - __range: range_model
    - __gross_weight: float
    - __net_weight: float
    + nomenclature: nomenclature_model
    + sub_recipe: receipt_model
    + range: range_model
    + gross_weight: float
    + net_weight: float
    + {static} create(item, range, gross, net): recipe_row_model
}

class receipt_model {
    - __dish: nomenclature_model
    - __rows: list
    - __comments: str
    + dish: nomenclature_model
    + comments: str
    + rows: list
    + gross_weight: float (рекурсивный расчет)
    + net_weight: float (рекурсивный расчет)
    + add_row(row: recipe_row_model): bool
    + remove_row(row: recipe_row_model): bool
    + {static} create(name: str, dish: nomenclature_model, rows: list, comments: str): receipt_model
}

abstract class abstract_manager {
    # _is_loaded: bool
    + {abstract} convert(): bool
}

class storage_manager {
    - {static} instance: storage_manager
    + {static} __new__(): storage_manager
    + convert(): bool
    + first_start(file_name: str): bool
    + add_recipe(item: receipt_model): bool
    + recipes: list
}

abstract_model <|-- entity_model
abstract_model <|-- recipe_row_model
entity_model <|-- warehouse_model
entity_model <|-- range_model
entity_model <|-- group_model
entity_model <|-- nomenclature_model
entity_model <|-- receipt_model

abstract_manager <|-- storage_manager

receipt_model *-- recipe_row_model
receipt_model --> nomenclature_model : dish
recipe_row_model --> nomenclature_model : nomenclature
recipe_row_model --> receipt_model : sub_recipe ("блюдо в блюде")
recipe_row_model --> range_model : range
storage_manager o-- receipt_model
@enduml
```

---

## 2. Диаграмма последовательности: Первый старт («блюдо в блюде» и фабрики)

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Store as storage_manager (Singleton)
    participant Sett as settings_manager (Singleton)
    participant RangeFactory as range_model (Фабрики create_*)
    participant RowFactory as recipe_row_model.create
    participant RecipeFactory as receipt_model.create

    Client->>Store: first_start()
    Store->>Sett: settings_manager()
    Store->>Sett: settings.first_launch_flag?
    alt first_launch_flag == False
        Store-->>Client: False (пропуск, данные уже сформированы)
    else first_launch_flag == True
        Store->>RangeFactory: create_gram(), create_kilogram(), create_piece(), create_milliliter()
        Store->>RowFactory: create(nom_flour, unit_g, 250, 250) + Масло + Сахар + Яйцо
        Store->>RecipeFactory: create("Песочное тесто", nom_dough, rows=[...])
        Note over Store,RecipeFactory: Рецепт 1: Полуфабрикат (брутто 560г, нетто 550г)
        Store->>RowFactory: create(recipe_dough, unit_g) ("блюдо в блюде")
        Store->>RowFactory: create(nom_box, unit_pcs, 40, 40) (тара)
        Store->>RecipeFactory: create("Песочное печенье в упаковке", nom_cookie, rows=[row_dough, row_box])
        Note over Store,RecipeFactory: Рецепт 2: Блюдо с вложенным рецептом и упаковкой
        Store->>Store: add_range(), add_warehouse(), add_group(), add_nomenclature(), add_recipe()
        Store->>Sett: settings.first_launch_flag = False
        Store-->>Client: True (первичные данные созданы)
    end
```

---

## 3. Диаграмма последовательности: Рекурсивный расчет веса Брутто (`gross_weight`)

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant ParentRecipe as receipt_model ("Песочное печенье в упаковке")
    participant RowDough as recipe_row_model (sub_recipe)
    participant NestedRecipe as receipt_model ("Песочное тесто")
    participant RowBox as recipe_row_model (упаковка)

    Client->>ParentRecipe: get gross_weight
    ParentRecipe->>RowDough: r.sub_recipe is not None?
    Note over ParentRecipe,RowDough: Вложенный рецепт обнаружен -> рекурсивный вызов
    ParentRecipe->>NestedRecipe: get gross_weight
    NestedRecipe-->>ParentRecipe: 560.0 г (250г мука + 150г масло + 100г сахар + 60г яйцо)
    ParentRecipe->>RowBox: r.gross_weight
    RowBox-->>ParentRecipe: 40.0 г (коробка крафтовая)
    ParentRecipe-->>Client: 600.0 г (560.0 + 40.0)
```
