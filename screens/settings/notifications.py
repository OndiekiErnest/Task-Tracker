"""notifications settings"""

import logging
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout
from customwidgets.groupboxes import NamedLineEditV, NotifsToggle
from customwidgets.comboboxes import TimeUnits
from datastructures.settings import settings


logger = logging.getLogger(__name__)


class NotificationsSettings(QGroupBox):
    """notifications settings group"""

    def __init__(self, **kwargs):
        super().__init__("Notifications", **kwargs)

        mainlayout = QVBoxLayout(self)
        mainlayout.setSpacing(20)
        mainlayout.setContentsMargins(8, 20, 8, 8)

        remindlayout = QHBoxLayout()

        self.remind_after = NamedLineEditV("Notify after every")
        self.remind_after.child.setText(str(settings["notify_after"]))
        self.remind_after.child.editingFinished.connect(self.remindAfterEdited)

        self.remind_units = TimeUnits()
        self.remind_units.setCurrentText(settings["notify_units"])
        self.remind_units.currentTextChanged.connect(self.remindUnitsChanged)

        remindlayout.addWidget(self.remind_after)
        remindlayout.addWidget(self.remind_units)
        # disable notifications
        self.disable_notifications = NotifsToggle("Disable notifications")

        mainlayout.addLayout(remindlayout)
        mainlayout.addWidget(self.disable_notifications)

    def remindAfterEdited(self):
        """when remind after has been edited"""
        tm = int(self.remind_after.child.text())
        settings["notify_after"] = tm
        logger.info(f"'notify_after' changed to: {tm}")

    def remindUnitsChanged(self, current: str):
        """current units changed"""
        settings["notify_units"] = current
        logger.info(f"'notify_units' changed to: {current}")
