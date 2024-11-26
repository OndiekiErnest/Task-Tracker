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
from constants import SUBMIT_ICON


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
        else:
            self.addbtn.setDisabled(True)


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

    def setTopics(self, topics, current: list = None):
        """add topics to drop-down menu"""
        self.topics.addItems(topics)
        if current:
            title = current[0].title
            self.topics.setCurrentTopic(title)
