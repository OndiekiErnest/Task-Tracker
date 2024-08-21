"""widget for settings"""

import logging
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from screens.activity_setter import ActivitySetter
from customwidgets.frames import Line
from customwidgets.groupboxes import NamedLineEditV, DisableNotifs
from customwidgets.comboboxes import TimeUnits
from models import TopicsModel
from datastructures.settings import settings


logger = logging.getLogger(__name__)


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
        # set activity topic, start, stop
        self.activity_adder = ActivitySetter()
        # remind after:
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

        layout.addWidget(self.activity_adder)
        layout.addWidget(Line())
        layout.addLayout(remindlayout)
        layout.addWidget(self.disable_notifications)

    def setModel(self, model: TopicsModel):
        """set model for topics"""
        logger.info(f"Model set to '{model}'")
        self.activity_adder.setModel(model)

    def remindAfterEdited(self):
        """when remind after has been edited"""
        tm = int(self.remind_after.child.text())
        settings["notify_after"] = tm

    def remindUnitsChanged(self, current: str):
        """current units changed"""
        settings["notify_units"] = current
