"""QTimeEdit in a named QGroupBox"""

from PyQt6.QtWidgets import QTimeEdit
from .base import NamedItem


class NamedTimeEdit(NamedItem):
    """QTimeEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QTimeEdit()
        # 24 hour system
        self.child.setDisplayFormat("HH:mm")

        super().__init__(*args, **kwargs)
