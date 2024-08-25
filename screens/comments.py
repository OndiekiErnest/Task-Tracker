"""widget for showing comment records"""

import logging
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from models import CommentsModel
from customwidgets.tableviews import CommentsTable
from customwidgets.delegates import CommentsDelegate
from constants import EDIT_ICON, ADDTOPIC_ICON

logger = logging.getLogger(__name__)


class CommentsWindow(QWidget):
    """activity comments viewer window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = QVBoxLayout(self)

        toplayout = QHBoxLayout()
        layout.addLayout(toplayout)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setIcon(QIcon(EDIT_ICON))

        self.add_record = QPushButton("New")
        self.add_record.setIcon(QIcon(ADDTOPIC_ICON))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search activities...")
        self.search_input.setClearButtonEnabled(True)

        self.tableview = CommentsTable()

        # add buttons to layout
        toplayout.addWidget(self.edit_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        toplayout.addWidget(self.add_record)
        toplayout.addStretch()
        toplayout.addWidget(self.search_input)

        layout.addWidget(self.tableview)

    def setModel(self, model: CommentsModel):
        """set database model"""
        logger.info(f"Model set to '{model}'")
        self.tableview.setModel(model)
        self.tableview.hideColumn(model.fieldIndex("id"))

        self.tableview.setItemDelegate(
            CommentsDelegate(
                model.fieldIndex("timestamp"), model.fieldIndex("comment")
            ),
        )
