"""QLineEdit in a named QGroupBox"""

from PyQt6.QtWidgets import QLineEdit
from .base import NamedItem


class NamedLineEdit(NamedItem):
    """QLineEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QLineEdit()

        super().__init__(*args, **kwargs)
