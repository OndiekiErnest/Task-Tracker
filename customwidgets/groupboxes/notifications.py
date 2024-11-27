"""notifications settings"""

import logging
from PyQt6.QtWidgets import (
    QGroupBox,
    QCheckBox,
    QHBoxLayout,
)
from datastructures.settings import settings


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
