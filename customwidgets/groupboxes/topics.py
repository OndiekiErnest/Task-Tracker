"""topic adder widget"""

from PyQt6.QtWidgets import (
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from customwidgets.checkboxes import NotificationCheckBox
from constants import SUBMIT_ICON
from .lineedits import NamedLineEdit
from .timeedits import NamedTimeEdit


class NewTopic(QGroupBox):
    """group widget holding widgets for adding new topic"""

    def __init__(self, **kwargs):
        super().__init__("New Topic", **kwargs)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 20, 8, 8)

        datetimeslayout = QHBoxLayout()

        self.topic_title = NamedLineEdit("Topic Title")
        self.topic_title.child.textChanged.connect(self.toggleSubmitBtn)

        self.start_time = NamedTimeEdit("Start Time")
        self.start_time.child.timeChanged.connect(self.toggleSubmitBtn)

        self.end_time = NamedTimeEdit("End Time")
        self.end_time.child.timeChanged.connect(self.toggleSubmitBtn)

        # set if notifications should be enabled
        self.notifs = NotificationCheckBox("Show notifications")
        self.notifs.setChecked(True)

        self.addbtn = QPushButton("Submit")
        self.addbtn.setIcon(QIcon(SUBMIT_ICON))
        self.addbtn.setDisabled(True)

        datetimeslayout.addWidget(self.start_time)
        datetimeslayout.addWidget(self.end_time)

        layout.addWidget(self.topic_title)
        layout.addLayout(datetimeslayout)
        layout.addWidget(self.notifs)
        layout.addWidget(self.addbtn, alignment=Qt.AlignmentFlag.AlignRight)

    def toggleSubmitBtn(self):
        """enable if all fields have data"""
        topic, start, ends = (
            self.topic_title.child.text(),
            self.start_time.child.time().toString(),
            self.end_time.child.time().toString(),
        )
        if all((topic, start, ends)) and (start != ends):
            self.addbtn.setEnabled(True)
        else:
            self.addbtn.setDisabled(True)
