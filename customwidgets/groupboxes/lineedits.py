"""QLineEdit in a named QGroupBox"""

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from .base import NamedItem


class NamedLineEdit(NamedItem):
    """QLineEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QLineEdit()

        super().__init__(*args, **kwargs)


class NamedLineEditV(NamedLineEdit):
    """named QLineEdit with an int validator"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        validator = QRegularExpressionValidator(self)

        validator.setRegularExpression(QRegularExpression("[0-9]+"))
        self.child.setValidator(validator)
