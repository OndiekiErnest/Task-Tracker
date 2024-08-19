"""PyQt6 windows and widgets"""

import logging
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QIcon
from models import CommentsModel, TopicsModel
from customwidgets.frames import Line
from customwidgets.comboboxes import TimeUnits
from customwidgets.mappers import DatabaseMapper
from customwidgets.splitters import Splitter
from customwidgets.tableviews import RecordsTable
from customwidgets.groupboxes import NamedLineEditV, DisableNotifs
from screens.record_editor import RecordsEditor
from screens.activity_setter import ActivitySetter
from constants import APP_ICON


logger = logging.getLogger(__name__)


class SettingsWindow(QScrollArea):
    """settings window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWidgetResizable(True)
        self.setFrameStyle(0)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        swidget = QWidget()
        swidget.setMaximumWidth(900)

        layout = QVBoxLayout(swidget)
        layout.setContentsMargins(6, 20, 6, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setWidget(swidget)

        # widgets
        # set activity topic, start, stop
        self.activity_adder = ActivitySetter()
        # remind after:
        remindlayout = QHBoxLayout()
        self.remind_after = NamedLineEditV("Remind after every")
        self.remind_units = TimeUnits()
        remindlayout.addWidget(self.remind_after)
        remindlayout.addWidget(self.remind_units)
        # disable notifications
        self.disable_notifications = DisableNotifs("Disable notifications")

        layout.addWidget(self.activity_adder)
        layout.addWidget(Line())
        layout.addLayout(remindlayout)
        layout.addWidget(self.disable_notifications)

    def setModel(self, model: TopicsModel):
        """set model for topics"""
        logger.info(f"Model set to '{model}'")
        self.activity_adder.setModel(model)


class DatabaseWindow(QWidget):
    """database records viewer window"""

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

        self.delete_record = QPushButton("Delete")
        self.add_record = QPushButton("New")

        self.proxy_model = QSortFilterProxyModel()
        # search topics
        self.proxy_model.setFilterKeyColumn(2)

        self.search_input = QLineEdit()
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.proxy_model.setFilterFixedString)

        self.tableview = RecordsTable()
        self.tableview.setModel(self.proxy_model)

        self.mapper = DatabaseMapper()
        # link row selection to mapper
        self.tableview.selectionModel().currentRowChanged.connect(
            self.mapper.setCurrentModelIndex
        )

        # add buttons to layout
        toplayout.addWidget(self.delete_record)
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

        self.mapper.setModel(model)
        self.mapper.addMapping(self.model_editor.id_edit.child, 0)
        self.mapper.addMapping(self.model_editor.datetime_edit.child, 1)
        self.mapper.addMapping(self.model_editor.topic_edit.child, 2)
        self.mapper.addMapping(self.model_editor.comment_edit.child, 3)
        # start at 1
        self.mapper.toFirst()

    def showhide_editor(self, show: bool):
        """toggle editor widget"""
        if show:
            self.model_editor.show()
            logger.info("Model editor shown")
        else:
            self.model_editor.hide()
            logger.info("Model editor hidden")


class MainWindow(QWidget):
    """main application window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle("TLog")
        self.setWindowIcon(QIcon(APP_ICON))

        layout = QVBoxLayout(self)

        # widgets
        self.databaseview = DatabaseWindow()

        self.settingsview = SettingsWindow()

        self.tabwidget = QTabWidget()
        layout.addWidget(self.tabwidget)

        # add views to tab widget
        self.tabwidget.addTab(self.databaseview, "Activities")
        self.tabwidget.addTab(self.settingsview, "Settings")

    def setCommentsModel(self, model: CommentsModel):
        """set database model"""
        self.databaseview.setModel(model)

    def setSettingsModel(self, model: TopicsModel):
        """set model for topics"""
        self.settingsview.setModel(model)

    def closeEvent(self, event):
        self.hide()
        event.ignore()
