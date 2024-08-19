"""custom QDataWidgetMapper classes"""

from PyQt6.QtWidgets import QDataWidgetMapper
from models import CommentsModel


class DatabaseMapper(QDataWidgetMapper):
    """widget for editing database records"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSubmitPolicy(QDataWidgetMapper.SubmitPolicy.ManualSubmit)

    def setModel(self, model: CommentsModel):
        """set database model"""
        super().setModel(model)
