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
from customwidgets.groupboxes import NewTopic
from constants import TIME_UNITS


class TrayMenu(QMenu):
    """menu widget for the tray icon"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(200)

        # top row

        labelwidget = QWidget()
        labellayout = QVBoxLayout(labelwidget)

        # 1500 - 1700 hrs
        self.current_slot = QLabel("<b>No task set for this hour</b>")
        self.current_slot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labellayout.addWidget(self.current_slot)

        firstrow = QWidgetAction(self)
        firstrow.setDefaultWidget(labelwidget)
        self.addAction(firstrow)

        self.addSeparator()

        # action to new topic
        self.addtopic_action = QAction("Add Topic")
        """add topic QAction"""
        self.addAction(self.addtopic_action)

        self.addSeparator()

        # action to disable notifications until restart
        self.disableactn = QAction("Disable notifications")
        """disable notifications QAction"""
        self.disableactn.setCheckable(True)
        self.disableactn.setChecked(False)
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


class NewTopicMenu(QMenu):
    """Menu class to add new topic"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.new_topic = NewTopic()

        newtopic = QWidgetAction(self)
        newtopic.setDefaultWidget(self.new_topic)
        self.addAction(newtopic)

    def clearInputs(self):
        """clear input fields"""
        self.new_topic.topic_title.child.clear()

    def getTopic(self):
        return self.new_topic.topic_title.child.text()

    def getStart(self):
        # "HH:mm"
        return self.new_topic.start_time.child.time().toString()

    def getSpan(self):
        """span in unit"""
        unit = self.new_topic.duration_unit.currentText()
        span = int(self.new_topic.duration.child.text()) * TIME_UNITS[unit]
        return span

    def addSpan(self):
        """add span to current set time"""
        unit = self.new_topic.duration_unit.currentText()
        # span in mins
        span = int(self.new_topic.duration.child.text()) * TIME_UNITS[unit]

        time = self.new_topic.start_time.child.time().addSecs(span * 60)
        self.new_topic.start_time.child.setTime(time)
