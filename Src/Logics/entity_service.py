from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception, operation_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.entity_reference_helper import entity_reference_helper
from Src.Logics.storage_manager import storage_manager


class entity_service:
    """Сервисный слой CRUD-операций над доменными сущностями.

    Хранилище (`storage_manager`) отвечает только за хранение коллекций;
    вся бизнес-логика поиска, создания, изменения и удаления сущностей
    сосредоточена здесь.
    """

    def _resolve_collection(self, entity_type: str) -> tuple[list, type]:
        """Динамически определяет коллекцию и класс модели по аннотациям collection_models.

        :param entity_type: Имя свойства коллекции, имя класса модели или его префикс без _model.
        :return: Кортеж (список элементов хранилища, класс модели).
        :raises arguments_exception: Если тип сущности пустой или не распознан.
        """
        if not isinstance(entity_type, str) or not entity_type.strip():
            raise arguments_exception("entity_type", "Тип сущности не может быть пустым")

        clean_type = entity_type.strip().lower()
        for prop_name, model_cls in storage_manager().collection_models.items():
            cls_name = model_cls.__name__.lower()
            short_cls = cls_name.removesuffix("_model")
            singular_prop = prop_name.lower().rstrip("s")
            if clean_type in (prop_name.lower(), singular_prop, cls_name, short_cls):
                return getattr(storage_manager(), prop_name), model_cls

        raise arguments_exception(
            "entity_type",
            f"Неподдерживаемый тип сущности '{entity_type}'"
        )

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
    def _find_in_list(
        items: list[abstract_model], ref: abstract_model | dict | None
    ) -> abstract_model | None:
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

    def _is_referenced(self, target: abstract_model) -> bool:
        """Проверяет, ссылается ли любая другая доменная сущность хранилища на target."""
        collections = {
            prop_name: getattr(storage_manager(), prop_name)
            for prop_name in storage_manager().collection_models
        }
        return entity_reference_helper.is_referenced(target, collections)

    def _validate_and_bind_entity(self, candidate: abstract_model, current_target=None) -> None:
        """Рефлексивно проверяет поля сущности и привязывает ссылки к объектам из хранилища."""
        collections_by_type = {
            model_cls: getattr(storage_manager(), prop_name)
            for prop_name, model_cls in storage_manager().collection_models.items()
        }

        def _bind_model(obj: abstract_model, is_root: bool = False) -> None:
            for field_name in abstract_covertor._get_fields(obj):
                if field_name in ("unique_code", "name"):
                    continue

                attribute = getattr(type(obj), field_name, None)
                if not isinstance(attribute, property) or attribute.fset is None:
                    continue

                value = getattr(obj, field_name, None)
                if value is None or value == "":
                    continue

                annotation = attribute.fget.__annotations__.get("return")
                target_type = deserialize_factory._deserialize_factory__resolve_type(annotation)
                elem_type = deserialize_factory._deserialize_factory__resolve_type(
                    deserialize_factory._deserialize_factory__element_type(annotation)
                )

                if target_type in collections_by_type:
                    found = self._find_in_list(collections_by_type[target_type], value)
                    if found is None:
                        raise operation_exception(
                            f"Связанная сущность для поля '{field_name}' не найдена в хранилище"
                        )
                    if is_root and (
                        found is current_target or found.unique_code == candidate.unique_code
                    ):
                        raise operation_exception(
                            f"Сущность не может ссылаться сама на себя в поле '{field_name}'"
                        )
                    setattr(obj, field_name, found)
                elif isinstance(value, list) and isinstance(elem_type, type) and issubclass(elem_type, abstract_model):
                    for item in value:
                        if isinstance(item, abstract_model):
                            _bind_model(item, is_root=False)

        _bind_model(candidate, is_root=True)

    def create_entity(self, entity_type: str, payload: dict):
        """Создает и добавляет новую доменную сущность из JSON-словаря с проверкой корректности."""
        items, model_cls = self._resolve_collection(entity_type)
        if not isinstance(payload, dict) or len(payload) == 0:
            raise arguments_exception("payload", "Тело запроса должно быть непустым JSON-объектом")

        candidate = deserialize_factory().Convert(payload, model_cls)
        self._validate_and_bind_entity(candidate)

        if not storage_manager()._is_unique(items, candidate):
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
                if self._is_referenced(target):
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

        for field_name in abstract_covertor._get_fields(target):
            attribute = getattr(type(target), field_name, None)
            if not isinstance(attribute, property) or attribute.fset is None:
                continue
            value = getattr(candidate, field_name, None)
            try:
                if getattr(target, field_name) == value:
                    continue
            except Exception:
                pass
            setattr(target, field_name, value)

        return target

    def delete_entity(self, entity_type: str, code: str) -> bool:
        """Удаляет доменную сущность по коду или имени, если она не связана с другими сущностями."""
        items, _ = self._resolve_collection(entity_type)
        target = self.find_entity(entity_type, code)
        if target is None:
            return False

        if self._is_referenced(target):
            raise operation_exception(
                "Запрещено удалять сущность, так как она связана с другой доменной сущностью"
            )

        items.remove(target)
        return True
