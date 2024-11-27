"""notifications settings"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout
from customwidgets.groupboxes import NotifsToggle, DurationChooser


class NotificationsSettings(QGroupBox):
    """notifications settings group"""

    def __init__(self, **kwargs):
        super().__init__("Notifications", **kwargs)

        mainlayout = QVBoxLayout(self)
        mainlayout.setSpacing(20)
        mainlayout.setContentsMargins(8, 20, 8, 8)

        self.duration_setter = DurationChooser("Notify after every")
        # disable notifications
        self.disable_notifications = NotifsToggle("Disable notifications")

        mainlayout.addWidget(self.duration_setter)
        mainlayout.addWidget(self.disable_notifications)
