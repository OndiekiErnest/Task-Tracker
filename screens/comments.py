"""widget for showing comment records"""

import logging
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from models import CommentsModel
from customwidgets.searchtables import CommentsTableview

logger = logging.getLogger(__name__)


class CommentsWindow(QWidget):
    """activity comments viewer window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = QVBoxLayout(self)

        self.table_group = CommentsTableview("Notes")

        layout.addWidget(self.table_group)

    def sRows(self):
        """return selected rows"""
        return self.table_group.sRows()

    def setModel(self, model: CommentsModel):
        """set database model"""
        logger.info(f"Model set to '{model}'")

        self.table_group.setModel(model)

        self.table_group.hideColumn(model.fieldIndex("id"))
