"""screen to add topic title, start, and span"""

import logging
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QCheckBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from customwidgets.groupboxes import NamedTimeEdit, NamedLineEdit, NamedLineEditV
from customwidgets.comboboxes import TimeUnits
from customwidgets.tableviews import TopicsTable
from customwidgets.delegates import TopicsDelegate
from models import TopicsModel
from constants import TIME_UNITS, SUBMIT_ICON, DELETE_ICON


logger = logging.getLogger(__name__)


class TopicSetter(QGroupBox):
    """widget for setting new topic"""

    def __init__(self, **kwargs):
        super().__init__("Topics", **kwargs)

        self.selected_rows = []

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(8, 20, 8, 8)

        btnslayout = QHBoxLayout()
        btnslayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btnslayout.setSpacing(30)

        datetimeslayout = QHBoxLayout()

        newtopic_group = QGroupBox("Add New Topic")
        grouplayout = QVBoxLayout(newtopic_group)
        grouplayout.setSpacing(10)
        grouplayout.setContentsMargins(8, 20, 8, 8)

        self.rtable = TopicsTable()

        self.topic_text = NamedLineEdit("Topic Title")
        self.topic_text.child.textChanged.connect(self.enableSubmitBtn)

        self.start_time = NamedTimeEdit("Topic Start Time")

        self.duration = NamedLineEditV("Topic Span")
        self.duration.child.textChanged.connect(self.enableSubmitBtn)
        self.duration_unit = TimeUnits()

        self.addbtn = QPushButton("Submit")
        self.addbtn.setIcon(QIcon(SUBMIT_ICON))
        self.addbtn.setDisabled(True)

        self.deletebtn = QPushButton("Delete")
        self.deletebtn.setIcon(QIcon(DELETE_ICON))
        self.deletebtn.setDisabled(True)

        self.enabledtopic = QCheckBox("Enable Notifications")
        self.enabledtopic.setDisabled(True)
        self.enabledtopic.clicked.connect(self.enableDisableNotifs)

        grouplayout.addWidget(self.topic_text)

        datetimeslayout.addWidget(self.start_time)
        datetimeslayout.addWidget(self.duration)
        datetimeslayout.addWidget(self.duration_unit)

        grouplayout.addLayout(datetimeslayout)

        grouplayout.addWidget(self.addbtn, alignment=Qt.AlignmentFlag.AlignLeft)

        btnslayout.addWidget(self.deletebtn)
        btnslayout.addWidget(self.enabledtopic)

        layout.addWidget(newtopic_group)
        layout.addWidget(self.rtable)
        layout.addLayout(btnslayout)

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
        """span in unit"""
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
        return self.selected_rows

    def enableDisableNotifs(self):
        """disable/enable topic from sending notifications"""
        if self.selected_rows:
            checked = self.enabledtopic.isChecked()
            model = self.rtable.model()
            for index in self.selected_rows:
                col = model.fieldIndex("enabled")
                logger.info(f"Index for 'enabled': {col}")
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
            model.select()

    def setCheckState(self):
        """check or uncheck topic based on database data"""
        states = [
            idx.model().record(idx.row()).value("enabled") for idx in self.selected_rows
        ]

        enabled = all(states)

        self.enabledtopic.setChecked(enabled)

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
