from Src.Core.entity_model import entity_model

class group_model(entity_model):
    """Модель группы номенклатуры.

    Используется для категоризации сырья, товаров и готовых блюд.
    """

    def __init__(self, name: str = "") -> None:
        """Инициализирует группу номенклатуры.

        :param name: Наименование группы (до 50 символов).
        """
        super().__init__()
        self.name = name
