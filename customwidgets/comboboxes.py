"""custom QComboBox classes"""

from PyQt6.QtWidgets import QComboBox
from constants import TIME_UNITS


class TimeUnits(QComboBox):
    """drop down to choose btwn hr, mins, secs"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.addItems(TIME_UNITS.keys())
