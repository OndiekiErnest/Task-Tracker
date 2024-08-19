"""custom QGroupBox classes"""

from PyQt6.QtWidgets import (
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QPlainTextEdit,
    QDateTimeEdit,
    QTimeEdit,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator


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

        self.child = QComboBox()

        super().__init__(*args, **kwargs)

    def addItems(self, items):
        self.child.clear()
        self.child.addItems(items)

    def setCurrentTopic(self, title):
        self.child.setCurrentText(title)


class NamedSpinbox(NamedItem):
    """QSpinBox in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QSpinBox()
        # read only
        self.child.setDisabled(True)

        super().__init__(*args, **kwargs)


class NamedDatetimeEdit(NamedItem):
    """QDateTimeEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QDateTimeEdit()
        # for consistency, match the format used in the database
        self.child.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.child.setCalendarPopup(True)

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
        self.disable_sunday = QCheckBox("On Sundays")

        mainlayout.addWidget(self.disable_all)
        mainlayout.addWidget(self.disable_saturday)
        mainlayout.addWidget(self.disable_sunday)
