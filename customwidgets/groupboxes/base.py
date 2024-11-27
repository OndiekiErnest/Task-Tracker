"""base groupbox widget"""

from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
)


class NamedItem(QGroupBox):
    """base named widget; shouldn't be instantiated"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainlayout = QVBoxLayout(self)

        self.mainlayout.addWidget(self.child)
