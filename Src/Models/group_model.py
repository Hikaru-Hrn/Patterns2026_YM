from Src.Core.entity_model import entity_model

class group_model(entity_model):
    """
    Модель группы номенклатуры

    Содержит определение: наименование
    """
    def __init__(self, name: str = "") -> None:
        """Инициализирует группу"""
        super().__init__()
        self.name = name
