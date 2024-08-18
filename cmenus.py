"""custom menu widgets"""

from PyQt6.QtWidgets import (
    QMenu,
    QLabel,
    QPushButton,
    QWidgetAction,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt


class TrayMenu(QMenu):
    """menu widget for the tray icon"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(200)

        # top row

        labelwidget = QWidget()
        labellayout = QVBoxLayout(labelwidget)

        # 1500 - 1700 hrs
        self.current_slot = QLabel("<b>No task set</b>")
        self.current_slot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labellayout.addWidget(self.current_slot)

        firstrow = QWidgetAction(self)
        firstrow.setDefaultWidget(labelwidget)
        self.addAction(firstrow)

        self.addSeparator()

        # pause/resume timer
        self.disableactn = QAction("Disable notifications")
        self.disableactn.setCheckable(True)
        self.disableactn.setChecked(False)
        """disable notifications QAction"""
        self.addAction(self.disableactn)

        self.addSeparator()

        btnswidget = QWidget()
        hlayout = QHBoxLayout(btnswidget)

        self.quit = QPushButton("Quit")
        self.more = QPushButton("More")
        self.addlog = QPushButton("Add Log")

        hlayout.addWidget(self.addlog)
        hlayout.addWidget(self.more)
        hlayout.addWidget(self.quit)

        bottom_row = QWidgetAction(self)
        bottom_row.setDefaultWidget(btnswidget)
        self.addAction(bottom_row)

    def setSlotText(self, time_txt: str):
        """update topic title"""
        self.current_slot.setText(time_txt)
