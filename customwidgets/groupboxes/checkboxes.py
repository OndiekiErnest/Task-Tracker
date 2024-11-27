"""QCheckBox in a named QGroupBox"""

from PyQt6.QtWidgets import QCheckBox
from .base import NamedItem


class NamedCheckbox(NamedItem):
    """QCheckBox in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QCheckBox()

        super().__init__(*args, **kwargs)
