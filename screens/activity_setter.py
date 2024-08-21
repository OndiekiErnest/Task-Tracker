"""screen to add activity topic, start, and span"""

import logging
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QCheckBox,
    QTableView,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QModelIndex, QTime
from customwidgets.groupboxes import NamedTimeEdit, NamedLineEdit, NamedLineEditV
from customwidgets.comboboxes import TimeUnits
from models import TopicsModel
from constants import TIME_UNITS


logger = logging.getLogger(__name__)


class ActivitySetter(QGroupBox):
    """widget for setting new activity"""

    def __init__(self, **kwargs):
        super().__init__("Activities", **kwargs)

        self.current_row = None

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        toplayout = QHBoxLayout()
        toplayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        toplayout.setSpacing(30)
        layout.addLayout(toplayout)

        datetimeslayout = QHBoxLayout()

        newactivity_group = QGroupBox("Add New Activity")
        grouplayout = QVBoxLayout(newactivity_group)

        self.rtable = QTableView()
        self.rtable.setAlternatingRowColors(True)
        self.rtable.setSortingEnabled(True)
        self.rtable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.rtable.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.rtable.setWordWrap(True)

        self.topic_text = NamedLineEdit("Activity Topic")
        self.topic_text.child.textChanged.connect(self.enableSubmitBtn)

        self.start_time = NamedTimeEdit("Activity Start Time")

        self.duration = NamedLineEditV("Activity Span")
        self.duration.child.textChanged.connect(self.enableSubmitBtn)
        self.duration_unit = TimeUnits()

        self.addbtn = QPushButton("Submit")
        self.addbtn.setDisabled(True)
        self.deletebtn = QPushButton("Delete")
        self.deletebtn.setDisabled(True)

        self.enabledtopic = QCheckBox("Enable Notifications")
        self.enabledtopic.setDisabled(True)
        self.enabledtopic.clicked.connect(self.enableDisableNotifs)

        layout.addWidget(self.rtable)
        grouplayout.addWidget(self.topic_text)

        datetimeslayout.addWidget(self.start_time)
        datetimeslayout.addWidget(self.duration)
        datetimeslayout.addWidget(self.duration_unit)

        grouplayout.addLayout(datetimeslayout)

        grouplayout.addWidget(self.addbtn, alignment=Qt.AlignmentFlag.AlignLeft)

        toplayout.addWidget(self.deletebtn)
        toplayout.addWidget(self.enabledtopic)

        layout.addWidget(newactivity_group)

    def clearInputs(self):
        """clear input fields"""
        self.topic_text.child.clear()

    def disableDnCheck(self):
        """disable delete and checkbox"""
        self.deletebtn.setDisabled(True)
        self.enabledtopic.setDisabled(True)

    def getTopic(self):
        return self.topic_text.child.text()

    def getStart(self):
        # "HH:mm"
        return self.start_time.child.time().toString()

    def getSpan(self):
        """span in minutes"""
        unit = self.duration_unit.currentText()
        span = int(self.duration.child.text()) * TIME_UNITS[unit]
        return span

    def addSpan(self):
        """add span to current set time"""
        unit = self.duration_unit.currentText()
        # span in mins
        span = int(self.duration.child.text()) * TIME_UNITS[unit]

        time = self.start_time.child.time().addSecs(span * 60)
        self.start_time.child.setTime(time)

    def sRows(self):
        """return selected rows"""
        return self.rtable.selectionModel().selectedRows()

    def enableDisableNotifs(self):
        """disable/enable topic from sending notifications"""
        # TODO: make this handle multiple selections
        if self.current_row is not None:
            col = 5
            model = self.rtable.model()
            # negate the old record
            checked = not bool(model.data(model.index(self.current_row, col)))
            if model.setData(model.index(self.current_row, col), int(checked)):
                if model.submitAll():
                    model.select()
                    logger.info(f"Topic was enabled: {checked}")
                else:
                    logger.error(
                        f"Topic dis/enable submitAll: {model.lastError().text()}"
                    )
            else:
                logger.error(f"Topic dis/enable setData: {model.lastError().text()}")

    def setCheckState(self, index: QModelIndex):
        """check or uncheck topic based on database data"""
        # TODO: make this handle multiple selections
        col = 5
        row = index.row()
        model = index.model()

        enabled = model.data(model.index(row, col))
        self.enabledtopic.setChecked(bool(enabled))

    def enableSubmitBtn(self):
        """if all fields have data"""
        topic, start, span = (
            self.getTopic(),
            self.getStart(),
            self.duration.child.text(),
        )
        if all((topic, start, span)) and int(span):  # span != 0
            self.addbtn.setEnabled(True)
        else:
            self.addbtn.setDisabled(True)

    def enableBtns(self):
        if indexes := self.rtable.selectionModel().selectedRows():
            self.current_row = indexes[0].row()
            self.deletebtn.setEnabled(True)
            self.enabledtopic.setEnabled(True)
        else:
            self.current_row = None
            self.disableDnCheck()

    def setModel(self, model: TopicsModel):
        """set model to use"""
        self.rtable.setModel(model)

        self.rtable.hideColumn(model.fieldIndex("id"))
        self.rtable.hideColumn(model.fieldIndex("timestamp"))
        self.rtable.hideColumn(model.fieldIndex("enabled"))

        self.rtable.selectionModel().selectionChanged.connect(self.enableBtns)
        self.rtable.selectionModel().currentRowChanged.connect(self.setCheckState)
