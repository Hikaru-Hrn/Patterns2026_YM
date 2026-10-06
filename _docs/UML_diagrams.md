# UML диаграммы для `settings_manager` и `storage_manager`

В данном документе представлены UML-диаграммы классов и последовательностей, описывающие архитектуру менеджеров настроек и хранилища данных. Диаграммы оформлены в формате **Mermaid** (рендерится в GitVerse и GitHub) и продублированы в формате **PlantUML**.

---

## 1. Диаграмма классов (Class Diagram)

### 1.1. Mermaid

```mermaid
classDiagram
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
        +__new__() storage_manager
        +load(file_name: str) void
        +convert() bool
        +first_start(file_name: str) bool
        +add_warehouse(item: warehouse_model) bool
        +add_range(item: range_model) bool
        +add_group(item: group_model) bool
        +add_nomenclature(item: nomenclature_model) bool
        -_is_unique(items: list, candidate) bool$
        -_find_group_by_name(name: str) group_model
        -_find_range_by_name(name: str) range_model
        +warehouses() list
        +ranges() list
        +units() list
        +groups() list
        +nomenclatures() list
    }

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

    class settings_model {
        -organization_model __organization
        -str __boss_name
        -str __account_name
        -bool __first_launch_flag
        +organization() organization_model
        +boss_name() str
        +account_name() str
        +first_launch_flag() bool
    }

    class warehouse_model {
        -str __address
        -int __max_len_address
        +address() str
    }

    class range_model {
        -range_model __base
        -float __conversion_factor
        +base() range_model
        +conversion_factor() float
    }

    class group_model {
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
    }

    abstract_manager <|-- settings_manager : Наследование
    abstract_manager <|-- storage_manager : Наследование
    abstract_model <|-- entity_model : Наследование
    abstract_model <|-- settings_model : Наследование
    entity_model <|-- warehouse_model : Наследование
    entity_model <|-- range_model : Наследование
    entity_model <|-- group_model : Наследование
    entity_model <|-- nomenclature_model : Наследование

    settings_manager o-- settings_model : Ассоциация (хранит)
    storage_manager ..> settings_manager : Использует (Singleton)
    storage_manager o-- "0..*" warehouse_model : Агрегация
    storage_manager o-- "0..*" range_model : Агрегация
    storage_manager o-- "0..*" group_model : Агрегация
    storage_manager o-- "0..*" nomenclature_model : Агрегация
    nomenclature_model --> group_model : Ссылка
    nomenclature_model --> range_model : Ссылка
    range_model --> range_model : Базовая единица
```

### 1.2. PlantUML

```plantuml
@startuml
skinparam classAttributeIconSize 0

abstract class abstract_manager {
    # _file_name: str
    # _is_loaded: bool
    # _data: dict
    + load(file_name: str): void
    + {abstract} convert(): bool
    + is_loaded: bool
}

class settings_manager {
    - {static} instance: settings_manager
    - {static} _initialized: bool
    - _settings: settings_model
    + {static} __new__(): settings_manager
    + load(file_name: str): void
    + convert(): bool
    + settings: settings_model
    + data: dict
}

class storage_manager {
    - {static} instance: storage_manager
    - {static} _initialized: bool
    - _groups: list
    - _ranges: list
    - _nomenclatures: list
    - _warehouses: list
    + {static} __new__(): storage_manager
    + load(file_name: str): void
    + convert(): bool
    + first_start(file_name: str): bool
    + add_warehouse(item: warehouse_model): bool
    + add_range(item: range_model): bool
    + add_group(item: group_model): bool
    + add_nomenclature(item: nomenclature_model): bool
    - {static} _is_unique(items: list, candidate): bool
    + warehouses: list
    + ranges: list
    + groups: list
    + nomenclatures: list
}

abstract_manager <|-- settings_manager
abstract_manager <|-- storage_manager
storage_manager ..> settings_manager : singleton call
@enduml
```

---

## 2. Диаграмма последовательности: Загрузка настроек (`settings_manager.load`)

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant SM as settings_manager (Singleton)
    participant FS as Файловая система (JSON)
    participant Model as settings_model
    participant Org as organization_model

    Client->>SM: load("settings.json")
    SM->>FS: open("settings.json")
    FS-->>SM: JSON-словарь
    SM->>SM: convert()
    SM->>Org: organization_model(name, inn, bic, account, owner)
    Org-->>SM: org instance
    SM->>Model: settings.organization = org
    SM->>Model: settings.boss_name = boss
    SM->>Model: settings.account_name = accountant
    SM->>Model: settings.first_launch_flag = flag
    SM-->>Client: _is_loaded = True
```

---

## 3. Диаграмма последовательности: Первый старт (`storage_manager.first_start`)

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Store as storage_manager (Singleton)
    participant Sett as settings_manager (Singleton)
    participant Models as Фабрика доменных моделей

    Client->>Store: first_start()
    Store->>Sett: settings_manager()
    Store->>Sett: settings.first_launch_flag?
    alt first_launch_flag == False
        Store-->>Client: False (пропуск, данные уже сформированы)
    else first_launch_flag == True
        Store->>Models: range_model("грамм", 1.0)
        Store->>Models: range_model("килограмм", 1000.0, base=грамм)
        Store->>Models: warehouse_model("Основной склад", "...")
        Store->>Models: group_model("Ингредиенты")
        Store->>Models: nomenclature_model() + setters (Мука, ...)
        Store->>Store: add_range(), add_warehouse(), add_group(), add_nomenclature()
        Store->>Sett: settings.first_launch_flag = False
        Store-->>Client: True (первичные данные созданы)
    end
```
