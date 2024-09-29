"""widget for settings"""

import logging
from PyQt6.QtWidgets import QScrollArea, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from screens.topic_setter import TopicSetter
from customwidgets.frames import Line
from customwidgets.groupboxes import NamedLineEditV, DisableNotifs
from customwidgets.comboboxes import TimeUnits
from models import TopicsModel
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
        self.disable_notifications = DisableNotifs("Disable notifications")

        mainlayout.addLayout(remindlayout)
        mainlayout.addWidget(self.disable_notifications)

    def remindAfterEdited(self):
        """when remind after has been edited"""
        tm = int(self.remind_after.child.text())
        settings["notify_after"] = tm

    def remindUnitsChanged(self, current: str):
        """current units changed"""
        settings["notify_units"] = current


class SettingsWindow(QScrollArea):
    """settings window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWidgetResizable(True)
        self.setFrameStyle(0)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        swidget = QWidget()
        swidget.setMaximumWidth(900)

        layout = QVBoxLayout(swidget)
        layout.setContentsMargins(6, 20, 6, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.setWidget(swidget)

        # widgets
        # set topic title, start, stop
        self.topic_adder = TopicSetter()

        # notifications group
        self.notifs_group = NotificationsSettings()

        layout.addWidget(self.topic_adder)
        layout.addWidget(Line())
        layout.addWidget(self.notifs_group)

    def setModel(self, model: TopicsModel):
        """set model for topics"""
        logger.info(f"Model set to '{model}'")
        self.topic_adder.setModel(model)
