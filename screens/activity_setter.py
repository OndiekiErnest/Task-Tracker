"""screen to add activity topic, start, and span"""

import logging
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QCheckBox,
    QTableView,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QModelIndex
from customwidgets.groupboxes import NamedTimeEdit, NamedLineEdit, NamedLineEditV
from customwidgets.comboboxes import TimeUnits
from models import TopicsModel
from constants import TIME_UNITS


logger = logging.getLogger(__name__)


class ActivitySetter(QWidget):
    """widget for setting new activity"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_row = None

        layout = QVBoxLayout(self)

        datetimeslayout = QHBoxLayout()
        buttonslayout = QHBoxLayout()
        buttonslayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

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

        self.duration = NamedLineEditV("Activity Duration")
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
        layout.addWidget(self.topic_text)

        datetimeslayout.addWidget(self.start_time)
        datetimeslayout.addWidget(self.duration)
        datetimeslayout.addWidget(self.duration_unit)

        layout.addLayout(datetimeslayout)

        buttonslayout.addWidget(self.addbtn)
        buttonslayout.addWidget(self.deletebtn)
        buttonslayout.addWidget(self.enabledtopic)

        layout.addLayout(buttonslayout)

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
        # total seconds
        unit = self.duration_unit.currentText()
        span = int(self.duration.child.text()) * TIME_UNITS[unit]
        return span

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
            # # get the QSqlRecord for the specified row
            # record = model.record(self.current_row)
            # # extract data from the QSqlRecord
            # data_tuple = tuple(record.value(i) for i in range(record.count()))
            # print(data_tuple)

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
        if all((topic, start, span)):
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