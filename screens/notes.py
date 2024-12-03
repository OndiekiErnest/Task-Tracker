"""widget for showing note records"""

import logging
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from models import NotesModel
from customwidgets.searchtables import NotesTableview

logger = logging.getLogger(__name__)


class NotesWindow(QWidget):
    """activity notes viewer window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = QVBoxLayout(self)

        self.table_group = NotesTableview("Notes")

        layout.addWidget(self.table_group)

    def sRows(self):
        """return selected rows"""
        return self.table_group.sRows()

    def setModel(self, model: NotesModel):
        """set database model"""
        logger.info(f"Model set to '{model}'")

        self.table_group.setModel(model)

        self.table_group.hideColumn(model.fieldIndex("id"))
