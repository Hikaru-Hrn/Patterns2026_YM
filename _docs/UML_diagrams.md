# UML диаграммы для моделей данных, `settings_manager` и `storage_manager`

В данном документе представлены UML-диаграммы классов и последовательностей, описывающие архитектуру приложения, доменных моделей (включая технологические карты/рецепты, полуфабрикаты и упаковку), а также менеджеров настроек и хранилища данных.

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
        -range_model __range
        -float __gross_weight
        -float __net_weight
        +nomenclature() nomenclature_model
        +range() range_model
        +gross_weight() float
        +net_weight() float
        +create(nomenclature, range, gross_weight, net_weight)$ recipe_row_model
    }

    class recipe_model {
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
        +create(name: str, dish: nomenclature_model, rows: list, comments: str)$ recipe_model
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
        +add_recipe(item: recipe_model) bool
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
    entity_model <|-- recipe_model : Наследование

    abstract_manager <|-- settings_manager : Наследование
    abstract_manager <|-- storage_manager : Наследование

    storage_manager ..> settings_manager : Singleton call
    storage_manager o-- "0..*" warehouse_model : Хранит
    storage_manager o-- "0..*" range_model : Хранит
    storage_manager o-- "0..*" group_model : Хранит
    storage_manager o-- "0..*" nomenclature_model : Хранит
    storage_manager o-- "0..*" recipe_model : Хранит

    nomenclature_model --> group_model : Группа
    nomenclature_model --> range_model : Ед. изм.
    range_model --> range_model : Базовая единица

    recipe_model *-- "1..*" recipe_row_model : Состав
    recipe_model --> nomenclature_model : Выходное блюдо/полуфабрикат
    recipe_row_model --> nomenclature_model : Номенклатура
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
    - __range: range_model
    - __gross_weight: float
    - __net_weight: float
    + nomenclature: nomenclature_model
    + range: range_model
    + gross_weight: float
    + net_weight: float
    + {static} create(nom, range, gross, net): recipe_row_model
}

class recipe_model {
    - __dish: nomenclature_model
    - __rows: list
    - __comments: str
    + dish: nomenclature_model
    + comments: str
    + rows: list
    + gross_weight: float
    + net_weight: float
    + add_row(row: recipe_row_model): bool
    + remove_row(row: recipe_row_model): bool
    + {static} create(name: str, dish: nomenclature_model, rows: list, comments: str): recipe_model
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
    + add_recipe(item: recipe_model): bool
    + recipes: list
}

abstract_model <|-- entity_model
abstract_model <|-- recipe_row_model
entity_model <|-- warehouse_model
entity_model <|-- range_model
entity_model <|-- group_model
entity_model <|-- nomenclature_model
entity_model <|-- recipe_model

abstract_manager <|-- storage_manager

recipe_model *-- recipe_row_model
recipe_model --> nomenclature_model : dish
recipe_row_model --> nomenclature_model : nomenclature
recipe_row_model --> range_model : range
storage_manager o-- recipe_model
@enduml
```

---

## 2. Диаграмма последовательности: Первый старт с фабричными методами (`storage_manager.first_start`)

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Store as storage_manager (Singleton)
    participant Sett as settings_manager (Singleton)
    participant Factory as Доменные фабрики (.create)
    participant RowFactory as recipe_row_model.create
    participant RecipeFactory as recipe_model.create

    Client->>Store: first_start()
    Store->>Sett: settings_manager()
    Store->>Sett: settings.first_launch_flag?
    alt first_launch_flag == False
        Store-->>Client: False (пропуск, данные уже сформированы)
    else first_launch_flag == True
        Store->>Factory: range_model.create("грамм", 1.0)
        Store->>Factory: warehouse_model.create("Основной склад", "...")
        Store->>Factory: group_model.create("Ингредиенты")
        Store->>Factory: nomenclature_model.create("Мука", ...)
        Store->>RowFactory: recipe_row_model.create(nom_flour, unit_g, 250, 250)
        Store->>RecipeFactory: recipe_model.create("Песочное тесто", nom_dough, rows=[...])
        Store->>Store: add_range(), add_warehouse(), add_group(), add_nomenclature(), add_recipe()
        Store->>Sett: settings.first_launch_flag = False
        Store-->>Client: True (первичные данные созданы)
    end
```
