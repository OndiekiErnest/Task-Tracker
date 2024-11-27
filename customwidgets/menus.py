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
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from customwidgets.groupboxes import NewTopic, NewProblem
from constants import SHOW_FILE_ICON, BACKUP_ICON


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

        self.setMinimumWidth(450)

        self.new_topic = NewTopic()

        newtopic = QWidgetAction(self)
        newtopic.setDefaultWidget(self.new_topic)
        self.addAction(newtopic)

    def on_done(self):
        """clear and hide"""
        self.clearInputs()
        self.hide()
        self.addSpan()

    def clearInputs(self):
        """clear input fields"""
        self.new_topic.topic_title.child.clear()

    def getTopic(self):
        return self.new_topic.topic_title.child.text()

    def getStart(self):
        """HH:mm"""
        return self.new_topic.start_time.child.time().toString()

    def getEnds(self):
        """return ends str (HH:mm)"""
        return self.new_topic.end_time.child.time().toString()

    def addSpan(self):
        """set end time as the new start time"""
        # QTime
        ends = self.new_topic.end_time.child.time()

        self.new_topic.start_time.child.setTime(ends)
        # add 5 minutes to the ends
        self.new_topic.end_time.child.setTime(ends.addSecs(5 * 60))


class NewProblemMenu(QMenu):
    """Menu class to add new problem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(450)

        self.new_problem = NewProblem()

        newproblem = QWidgetAction(self)
        newproblem.setDefaultWidget(self.new_problem)
        self.addAction(newproblem)

    def on_done(self):
        """clear and hide"""
        self.clear()
        self.hide()

    def problem(self):
        """problem title"""
        return self.new_problem.problem_title.child.text()

    def topic(self):
        """related topic"""
        return self.new_problem.topics.child.currentText()

    def setTopics(self, topics, current=None):
        self.new_problem.setTopics(topics, current=current)

    def clear(self):
        """clear fields"""
        self.new_problem.problem_title.child.clear()


class TableMoreMenu(QMenu):
    """Menu for the 'More' btn in tables"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.show_file = QAction(QIcon(SHOW_FILE_ICON), "Database Location")
        self.backup_file = QAction(QIcon(BACKUP_ICON), "Backup Database")

        self.addAction(self.show_file)
        self.addAction(self.backup_file)
