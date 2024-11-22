"""custom QGroupBox classes"""

import logging
from PyQt6.QtWidgets import (
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QPlainTextEdit,
    QTimeEdit,
    QCheckBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from datastructures.settings import settings
from customwidgets.comboboxes import TopicsCombobox, TimeUnits
from customwidgets.tableviews import TopicsTable
from customwidgets.delegates import TopicsDelegate
from models import TopicsModel
from constants import SUBMIT_ICON, DELETE_ICON


logger = logging.getLogger(__name__)


class NamedItem(QGroupBox):
    """base named widget; shouldn't be instantiated"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainlayout = QVBoxLayout(self)

        self.mainlayout.addWidget(self.child)


class NamedLineEdit(NamedItem):
    """QLineEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QLineEdit()

        super().__init__(*args, **kwargs)


class NamedCombobox(NamedItem):
    """QComboBox in a QGroupBox"""

    def __init__(self, *args, **kwargs):

        self.child = TopicsCombobox()

        super().__init__(*args, **kwargs)

    def addItems(self, topics):
        self.child.clear()
        self.child.addItems((t.title for t in topics))

    def setCurrentTopic(self, title):
        self.child.setCurrentText(title)


class NamedSpinbox(NamedItem):
    """QSpinBox in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QSpinBox()
        # read only
        self.child.setDisabled(True)

        super().__init__(*args, **kwargs)


class NamedTimeEdit(NamedItem):
    """QTimeEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QTimeEdit()
        # 24 hour system
        self.child.setDisplayFormat("HH:mm")

        super().__init__(*args, **kwargs)


class NamedPlainTextEdit(NamedItem):
    """QPlainTextEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QPlainTextEdit()

        super().__init__(*args, **kwargs)


class NamedCheckbox(NamedItem):
    """QCheckBox in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QCheckBox()

        super().__init__(*args, **kwargs)


class NamedLineEditV(NamedLineEdit):
    """named QLineEdit with an int validator"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        validator = QRegularExpressionValidator(self)

        validator.setRegularExpression(QRegularExpression("[0-9]+"))
        self.child.setValidator(validator)


class DisableNotifs(QGroupBox):
    """group of checkboxes for disabling notifications"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mainlayout = QHBoxLayout(self)
        # widgets
        self.disable_all = QCheckBox("Until restart")

        self.disable_saturday = QCheckBox("On Saturdays")
        self.disable_saturday.setChecked(settings["disable_saturday"])
        self.disable_saturday.toggled.connect(self.onCheckSat)

        self.disable_sunday = QCheckBox("On Sundays")
        self.disable_sunday.setChecked(settings["disable_sunday"])
        self.disable_sunday.toggled.connect(self.onCheckSun)

        mainlayout.addWidget(self.disable_all)
        mainlayout.addWidget(self.disable_saturday)
        mainlayout.addWidget(self.disable_sunday)

    def onCheckSat(self, disabled: bool):
        settings["disable_saturday"] = disabled
        logger.info(f"Saturday disabled: {disabled}")

    def onCheckSun(self, disabled: bool):
        settings["disable_sunday"] = disabled
        logger.info(f"Sunday disabled: {disabled}")


class NewTopic(QGroupBox):
    """group widget holding widgets for adding new topic"""

    def __init__(self, **kwargs):
        super().__init__("New Topic", **kwargs)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 20, 8, 8)

        datetimeslayout = QHBoxLayout()

        self.topic_title = NamedLineEdit("Topic Title")
        self.topic_title.child.textChanged.connect(self.enableSubmitBtn)

        self.start_time = NamedTimeEdit("Daily Start Time")

        self.duration = NamedLineEditV("Topic Span")
        self.duration.child.textChanged.connect(self.enableSubmitBtn)

        self.duration_unit = TimeUnits()

        self.addbtn = QPushButton("Submit")
        self.addbtn.setIcon(QIcon(SUBMIT_ICON))
        self.addbtn.setDisabled(True)

        datetimeslayout.addWidget(self.start_time)
        datetimeslayout.addWidget(self.duration)
        datetimeslayout.addWidget(self.duration_unit)

        layout.addWidget(self.topic_title)
        layout.addLayout(datetimeslayout)
        layout.addWidget(self.addbtn, alignment=Qt.AlignmentFlag.AlignLeft)

    def enableSubmitBtn(self):
        """if all fields have data"""
        topic, start, span = (
            self.topic_title.child.text(),
            self.start_time.child.time().toString(),
            self.duration.child.text(),
        )
        if all((topic, start, span)) and int(span):  # span != 0
            self.addbtn.setEnabled(True)
        else:
            self.addbtn.setDisabled(True)


class TopicOptions(QGroupBox):
    """topics viewer and settings widget"""

    def __init__(self, **kwargs):
        super().__init__("Topics", **kwargs)

        self.selected_rows = []

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(8, 20, 8, 8)

        btnslayout = QHBoxLayout()
        btnslayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btnslayout.setSpacing(30)

        self.rtable = TopicsTable()

        self.deletebtn = QPushButton("Delete")
        self.deletebtn.setIcon(QIcon(DELETE_ICON))
        self.deletebtn.setDisabled(True)

        self.enabledtopic = QCheckBox("Enable Notifications")
        self.enabledtopic.setDisabled(True)
        self.enabledtopic.clicked.connect(self.enableDisableNotifs)

        btnslayout.addWidget(self.deletebtn)
        btnslayout.addWidget(self.enabledtopic)

        layout.addLayout(btnslayout)
        layout.addWidget(self.rtable)

    def disableDnCheck(self):
        """disable delete and checkbox"""
        self.deletebtn.setDisabled(True)
        self.enabledtopic.setDisabled(True)

    def sRows(self):
        """return selected rows"""
        return self.selected_rows

    def enableDisableNotifs(self):
        """disable/enable topic from sending notifications"""
        if self.selected_rows:
            checked = self.enabledtopic.isChecked()
            model = self.rtable.model()
            for index in self.selected_rows:
                col = model.fieldIndex("enabled")
                row = index.row()
                if model.setData(model.index(row, col), int(checked)):
                    if model.submitAll():
                        logger.info(f"Topic was enabled: {checked}")
                    else:
                        logger.error(
                            f"Topic error dis/enable submitAll: {model.lastError().text()}"
                        )
                else:
                    logger.error(
                        f"Topic error dis/enable setData: {model.lastError().text()}"
                    )
            # model.select()

    def setCheckState(self):
        """check or uncheck topic based on database data"""
        states = [
            idx.model().record(idx.row()).value("enabled") for idx in self.selected_rows
        ]

        enabled = all(states)

        self.enabledtopic.setChecked(enabled)

    def enableBtns(self):
        if indexes := self.rtable.selectionModel().selectedRows():
            self.selected_rows = indexes
            self.deletebtn.setEnabled(True)
            self.enabledtopic.setEnabled(True)
        else:
            self.selected_rows = []
            self.disableDnCheck()

    def setModel(self, model: TopicsModel):
        """set model to use"""
        self.rtable.setModel(model)

        self.rtable.hideColumn(model.fieldIndex("id"))
        self.rtable.hideColumn(model.fieldIndex("timestamp"))
        self.rtable.hideColumn(model.fieldIndex("enabled"))

        self.rtable.setItemDelegate(
            TopicsDelegate(parent=self.rtable),
        )

        self.rtable.selectionModel().selectionChanged.connect(self.enableBtns)
        self.rtable.selectionModel().selectionChanged.connect(self.setCheckState)
