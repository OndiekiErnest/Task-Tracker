"""notifications settings"""

import logging
from PyQt6.QtWidgets import (
    QGroupBox,
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
)
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from datastructures.settings import settings
from constants import TIME_UNITS

logger = logging.getLogger(__name__)


class NotifsToggle(QGroupBox):
    """group of checkboxes for toggling notifications"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mainlayout = QHBoxLayout(self)
        # widgets
        self.disable_all = QCheckBox("Until restart")

        self.disable_saturday = QCheckBox("On Saturdays")
        self.disable_saturday.setChecked(settings["disable_saturday"])
        self.disable_saturday.toggled.connect(self.onCheckSat)

        self.disable_sunday = QCheckBox("On Sundays")
        self.disable_sunday.setChecked(settings["disable_sunday"])
        self.disable_sunday.toggled.connect(self.onCheckSun)

        mainlayout.addWidget(self.disable_all)
        mainlayout.addWidget(self.disable_saturday)
        mainlayout.addWidget(self.disable_sunday)

    def onCheckSat(self, disabled: bool):
        settings["disable_saturday"] = disabled
        logger.info(f"Saturday disabled: {disabled}")

    def onCheckSun(self, disabled: bool):
        settings["disable_sunday"] = disabled
        logger.info(f"Sunday disabled: {disabled}")


class DurationChooser(QGroupBox):
    """widget for specifying duration"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mainlayout = QHBoxLayout(self)

        self.duration = QLineEdit()
        self.duration.setText(str(settings["notify_after"]))
        self.duration.editingFinished.connect(self.notify_after_edited)

        self.units = QComboBox()
        self.units.addItems(TIME_UNITS.keys())
        self.units.setCurrentText(settings["notify_units"])
        self.units.currentTextChanged.connect(self.notify_units_changed)

        validator = QRegularExpressionValidator(self)
        validator.setRegularExpression(QRegularExpression("[0-9]+"))

        self.duration.setValidator(validator)

        mainlayout.addWidget(self.duration)
        mainlayout.addWidget(self.units)

    def set_units(self, unit: str):
        self.units.setCurrentText(unit)

    def set_duration(self, dur: str):
        self.duration.setText(dur)

    def minutes(self):
        return int(self.duration.text()) * TIME_UNITS[self.units.currentText()]

    def notify_after_edited(self):
        """when notify after has been edited"""
        tm = int(self.duration.text())
        settings["notify_after"] = tm
        logger.info(f"'notify_after' changed to: {tm}")

    def notify_units_changed(self, current: str):
        """current units changed"""
        settings["notify_units"] = current
        logger.info(f"'notify_units' changed to: {current}")
