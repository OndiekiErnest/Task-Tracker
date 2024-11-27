"""QPlainTextEdit in a named QGroupBox"""

from PyQt6.QtWidgets import QPlainTextEdit
from .base import NamedItem


class NamedPlainTextEdit(NamedItem):
    """QPlainTextEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QPlainTextEdit()

        super().__init__(*args, **kwargs)
