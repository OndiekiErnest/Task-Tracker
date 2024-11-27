"""topic adder widget"""

import logging
from PyQt6.QtWidgets import (
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from customwidgets.comboboxes import TimeUnits
from constants import SUBMIT_ICON
from .lineedits import NamedLineEdit, NamedLineEditV
from .timeedits import NamedTimeEdit


logger = logging.getLogger(__name__)


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
        layout.addWidget(self.addbtn, alignment=Qt.AlignmentFlag.AlignRight)

    def enableSubmitBtn(self):
        """if all fields have data"""
        topic, start, span = (
            self.topic_title.child.text(),
            self.start_time.child.time().toString(),
            self.duration.child.text(),
        )
        if all((topic, start, span)) and int(span):  # span != 0
            self.addbtn.setEnabled(True)
            logger.info("New topic is ready to be submitted")
        else:
            self.addbtn.setDisabled(True)
