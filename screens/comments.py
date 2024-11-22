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
from models import CommentsModel, SearchableModel
from customwidgets.tableviews import CommentsTable
from customwidgets.buttons import InOutButton
from constants import ADDTOPIC_ICON, DELETE_ICON, SEARCH_ICON

logger = logging.getLogger(__name__)


class CommentsWindow(QWidget):
    """activity comments viewer window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = QVBoxLayout(self)

        toplayout = QHBoxLayout()
        layout.addLayout(toplayout)

        self.model = SearchableModel()

        self.delete_btn = InOutButton("Delete")
        self.delete_btn.setIcon(QIcon(DELETE_ICON))
        self.delete_btn.hide()

        self.add_topic = QPushButton("Topic")
        self.add_topic.setIcon(QIcon(ADDTOPIC_ICON))

        self.add_record = QPushButton("Notes")
        self.add_record.setIcon(QIcon(ADDTOPIC_ICON))

        self.search_input = QLineEdit()
        self.search_input.addAction(
            QIcon(SEARCH_ICON), QLineEdit.ActionPosition.LeadingPosition
        )
        self.search_input.setPlaceholderText("Search entries...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.model.setFilterFixedString)

        self.tableview = CommentsTable()
        self.tableview.setModel(self.model)

        # add buttons to layout
        toplayout.addWidget(self.add_topic, alignment=Qt.AlignmentFlag.AlignLeft)
        toplayout.addWidget(self.add_record)
        toplayout.addWidget(self.delete_btn)
        toplayout.addStretch()
        toplayout.addWidget(self.search_input)

        layout.addWidget(self.tableview)

    def sRows(self):
        return [
            self.model.mapToSource(idx)
            for idx in self.tableview.selectionModel().selectedRows()
        ]

    def setModel(self, model: CommentsModel):
        """set database model"""
        logger.info(f"Model set to '{model}'")

        self.model.setSourceModel(model)

        self.tableview.hideColumn(model.fieldIndex("id"))
        self.tableview.selectionModel().selectionChanged.connect(self.toggle_delete)

    def toggle_delete(self):
        """show or hide delete_btn"""
        if self.sRows():
            if not self.delete_btn.isVisible():
                self.delete_btn.show()
        else:
            self.delete_btn.hide()
