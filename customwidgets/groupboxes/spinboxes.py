"""QSpinBox in a named QGroupBox"""

from PyQt6.QtWidgets import QSpinBox
from .base import NamedItem


class NamedSpinbox(NamedItem):
    """QSpinBox in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QSpinBox()
        # read only
        self.child.setDisabled(True)

        super().__init__(*args, **kwargs)
