"""widget for showing activity records"""

import logging
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from models import CommentsModel, SearchModel
from customwidgets.mappers import DatabaseMapper
from customwidgets.splitters import Splitter
from customwidgets.tableviews import RecordsTable
from screens.record_editor import RecordsEditor

logger = logging.getLogger(__name__)


class DatabaseWindow(QWidget):
    """activity comments viewer window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = QVBoxLayout(self)

        toplayout = QHBoxLayout()
        layout.addLayout(toplayout)

        self.splitter = Splitter()
        layout.addWidget(self.splitter)

        # widgets
        self.model_editor = RecordsEditor()
        self.model_editor.hide()

        self.toggle_edit = QPushButton("Edit")
        self.toggle_edit.setCheckable(True)
        # on toggled signal
        self.toggle_edit.toggled.connect(self.showhide_editor)

        self.add_record = QPushButton("New")

        self.proxy_model = SearchModel()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search activities...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.proxy_model.setFilterFixedString)

        self.tableview = RecordsTable()
        self.tableview.setModel(self.proxy_model)

        self.mapper = DatabaseMapper()

        self.model_editor.prev_btn.clicked.connect(self.editPrevious)
        self.model_editor.save_btn.clicked.connect(self.saveEdits)
        self.model_editor.next_btn.clicked.connect(self.editNext)
        self.model_editor.cancel_btn.clicked.connect(self.discardEdits)

        self.mapper.setModel(self.proxy_model)
        self.mapper.addMapping(self.model_editor.topic_edit.child, 2)
        self.mapper.addMapping(self.model_editor.comment_edit.child, 3)

        # link row selection to mapper
        self.tableview.selectionModel().currentRowChanged.connect(self.onRowSelected)
        self.mapper.toFirst()

        # add buttons to layout
        toplayout.addWidget(self.toggle_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        toplayout.addWidget(self.add_record)
        toplayout.addStretch()
        toplayout.addWidget(self.search_input)

        # add to splitter
        self.splitter.addWidget(self.tableview)
        self.splitter.addWidget(self.model_editor)

    def setModel(self, model: CommentsModel):
        """set database model"""
        logger.info(f"Model set to '{model}'")
        self.proxy_model.setSourceModel(model)
        self.tableview.hideColumn(model.fieldIndex("id"))

    def onRowSelected(self, current, old):
        """on row selection changed signal"""
        self.mapper.setCurrentModelIndex(current)
        logger.info(f"Row selected: {current.row()}")

    def editNext(self):
        """go to next record"""
        self.mapper.toNext()

    def editPrevious(self):
        """go to previous record"""
        self.mapper.toPrevious()

    def discardEdits(self):
        """discard changes"""
        self.mapper.revert()

    def saveEdits(self):
        """save changes"""
        if self.mapper.submit():
            logger.info(f"Changes on row {self.mapper.currentIndex()} saved")
        else:
            logger.error(
                f"Error on saving row {self.mapper.currentIndex()}: {self.mapper.model().lastError().text()}"
            )

    def showhide_editor(self, show: bool):
        """toggle editor widget"""
        if show:
            self.model_editor.show()
            logger.info("Model editor shown")
        else:
            self.model_editor.hide()
            logger.info("Model editor hidden")
