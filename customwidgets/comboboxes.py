"""custom QComboBox classes"""

from PyQt6.QtWidgets import QComboBox
from constants import TIME_UNITS


class TimeUnits(QComboBox):
    """drop down to choose btwn hr, mins, secs"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.addItems(TIME_UNITS.keys())


class TopicsCombobox(QComboBox):
    """drop down for the topics"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setText(self, text: str):
        self.setCurrentText(text)

    def text(self):
        return self.currentText()
