"""custom QCheckBox classes"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtGui import QIcon
from constants import NOTIFS_ON_ICON, NOTIFS_OFF_ICON, SOLVED_ICON, UNSOLVED_ICON


class NotificationCheckBox(QCheckBox):
    """notification check"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.notification_on = QIcon(NOTIFS_ON_ICON)
        self.notification_off = QIcon(NOTIFS_OFF_ICON)

        self.setIcon(self.notification_off)

        self.stateChanged.connect(self.update_icon)

    def update_icon(self, state):
        """update the icon based on the state of the checkbox"""
        if state == Qt.CheckState.Checked.value:
            self.setIcon(self.notification_on)
        else:
            self.setIcon(self.notification_off)


class ProblemCheckBox(QCheckBox):
    """problem state check btn"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the images for the checked and unchecked states
        self.solved_icon = QIcon(SOLVED_ICON)
        self.unsolved_icon = QIcon(UNSOLVED_ICON)

        self.setIcon(self.unsolved_icon)

        self.stateChanged.connect(self.update_icon)

    def update_icon(self, state):
        """update the icon based on the state of the checkbox"""
        if state == Qt.CheckState.Checked.value:
            self.setIcon(self.solved_icon)
        else:
            self.setIcon(self.unsolved_icon)
