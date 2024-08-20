"""custom QGroupBox classes"""

import logging
from PyQt6.QtWidgets import (
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QPlainTextEdit,
    QTimeEdit,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from customwidgets.comboboxes import TopicsCombobox
from datastructures.settings import settings


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
        # for consistency, match the format used in the database
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
