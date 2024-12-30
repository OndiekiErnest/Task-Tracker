"""custom QGroupBox classes"""

from PyQt6.QtWidgets import (
    QGroupBox,
    QPushButton,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from constants import SUBMIT_ICON
from .lineedits import NamedLineEdit
from .comboboxes import NamedCombobox


class NewProblem(QGroupBox):
    """group widget holding widgets for adding new problem"""

    def __init__(self, **kwargs):
        super().__init__("New Problem", **kwargs)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 20, 8, 8)

        self.problem_title = NamedLineEdit("Problem Title")
        self.problem_title.child.textChanged.connect(self.enableSubmitBtn)

        self.topics = NamedCombobox("Related Topic")
        self.topics.child.currentTextChanged.connect(self.enableSubmitBtn)

        self.addbtn = QPushButton("Submit")
        self.addbtn.setIcon(QIcon(SUBMIT_ICON))
        self.addbtn.setDisabled(True)

        layout.addWidget(self.problem_title)
        layout.addWidget(self.topics)
        layout.addWidget(self.addbtn, alignment=Qt.AlignmentFlag.AlignRight)

    def enableSubmitBtn(self, *args):
        """if all fields have data"""
        if all(
            (
                self.problem_title.child.text(),
                self.topics.child.currentText(),
            )
        ):
            self.addbtn.setEnabled(True)
        else:
            self.addbtn.setDisabled(True)

    def setTopics(self, topics, current=None):
        """add topics to drop-down menu"""
        self.topics.addItems(t.title for t in topics)
        if current:
            self.topics.setCurrentTopic(current.title)
