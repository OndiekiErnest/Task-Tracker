"""The C in MVC"""

import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtCore import QTimer
from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtGui import QIcon
from humanize import naturaltime
from gui import MainWindow
from models import NotesModel, TopicsModel, ProblemsModel
from customwidgets.menus import TrayMenu
from customwidgets.delegates import NotesDelegate, ProblemsDelegate
from screens.note_input import InputPopup
from datastructures.settings import settings
from datastructures.datas import TopicData
from utils import close_topic
from qstyles import STYLE
from constants import APP_DB, APP_ICON, TIMEZONE, SOLVED_PLACEHOLDER


logging.basicConfig(
    level=logging.DEBUG,
    encoding="utf-8",
)
logger = logging.getLogger("main")


class Tracker:
    """
    put the GUI and models together;
    application-level logic
    """

    def __init__(self):

        self._today = datetime.now(tz=TIMEZONE).weekday()
        """day of the week where Mon=0 and Sun=6"""
        self.show_notifications = True

        self.app_icon = QIcon(APP_ICON)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(APP_DB)
        self.db.open()

        self.disable_sat = settings["disable_saturday"]
        self.disable_sun = settings["disable_sunday"]

        if self.db.isOpen():
            logger.info("SQLite file opened successfully")
        else:
            logger.error(f"SQLite did not open: {self.db.lastError().driverText()}")

        settings.changed.connect(self.onSettingsChange)

        self.gui = MainWindow()

        self.input_window = InputPopup()
        self.input_window.setWindowIcon(self.app_icon)
        # link buttons
        self.input_window.submit.clicked.connect(self.logNote)
        self.input_window.prompt.linkActivated.connect(self.showAddTopic)

        self.notification_timer = QTimer(self.gui)
        self.notification_timer.timeout.connect(self.onTimeout)
        self._setNotificationsInterval()
        self.notification_timer.start()

        # models
        self.topics_model = TopicsModel(self.db)
        self.problems_model = ProblemsModel(self.db)
        self.notes_model = NotesModel(self.db)

        self.all_topics = self.topics_model.getTopics()

        self.gui.setNotesModel(self.notes_model)
        self.gui.setTopicsModel(self.topics_model)
        self.gui.setProblemsModel(self.problems_model)

        self.notes_delegate = NotesDelegate()
        self.problems_delegate = ProblemsDelegate()

        self.gui.notesview.table_group.setItemDelegate(self.notes_delegate)
        self.gui.settingsview.problem_options.table_view.setItemDelegate(
            self.problems_delegate
        )

        self.topics_model.modelReset.connect(self.on_topics_changed)
        self.topics_model.dataChanged.connect(self.on_topics_changed)
        # self.topics_model.layoutChanged.connect(self.on_topics_changed)
        self.topics_model.rowsRemoved.connect(self.on_topics_changed)

        self.topics_model.modelReset.connect(self.on_problems_changed)
        self.topics_model.dataChanged.connect(self.on_problems_changed)
        # self.topics_model.layoutChanged.connect(self.on_problems_changed)
        self.topics_model.rowsRemoved.connect(self.on_problems_changed)

        # notes viewer btns
        self.gui.notesview.table_group.new_note.clicked.connect(self.showInputWin)
        self.gui.notesview.table_group.del_btn.clicked.connect(self.deleteNote)
        # settings
        self.gui.topic_menu.new_topic.addbtn.clicked.connect(self.saveTopic)
        self.gui.problem_menu.new_problem.addbtn.clicked.connect(self.from_problemenu)
        self.gui.settingsview.topic_options.del_btn.clicked.connect(self.deleteTopic)

        self.tray_menu = TrayMenu()
        self.tray_menu.addlog.clicked.connect(self.input_window.showNormal)
        self.tray_menu.addtopic_action.triggered.connect(self.showAddTopic)
        self.tray_menu.more.clicked.connect(self.showEntries)

        self.tray_menu.disableactn.toggled.connect(self.onTrayDisable)
        self.gui.settingsview.notifs_options.disable_notifications.disable_all.toggled.connect(
            self.tray_menu.disableactn.setChecked
        )

        self.tray_icon = QSystemTrayIcon(self.app_icon, self.gui)
        self.tray_icon.setToolTip("TLog - Time Tracker")
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.messageClicked.connect(self.input_window.showNormal)
        self.tray_icon.show()

        # set things on start
        # check if is weekend and if any notifications have been disabled
        # show notifications right away if any
        self.onStartup()

    def _topicIDByTitle(self, title: str):
        """return topic id"""
        for topic in self.all_topics:
            if topic.title == title:
                return topic.topic_id

    def _problemID(self, problem: str):
        """get problem id by it's statement"""
        for p in self.problems_model.getProblems():
            if p.problem == problem:
                return p.problem_id

    def _setNotificationsInterval(self):
        """update notification interval"""
        after = self.gui.settingsview.notifs_options.duration_setter.minutes()
        logger.info(f"Interval set to: {after} minutes")
        # convert to millisecs
        self.notification_timer.setInterval(after * 60000)

    def _checkWeekend(self):
        """if weekend; enable/disable notifications"""
        if self._today == 5:
            logger.info("It is Saturday")
            if self.disable_sat:
                self.toggleNotifications(True)
            else:
                self.toggleNotifications(False)

        elif self._today == 6:
            logger.info("It is Sunday")
            if self.disable_sun:
                self.toggleNotifications(True)
            else:
                self.toggleNotifications(False)
        else:
            logger.info("It is a weekday")

    def onStartup(self):
        """get things running right away"""
        self.notes_delegate.setTopics(self.all_topics)
        self.problems_delegate.setTopics(self.all_topics)
        self._checkWeekend()
        self.onTimeout()

    def onSettingsChange(self, key: str):
        """handle settings change"""
        logger.info(f"Settings '{key}' changed")
        match key:
            case "notify_after":
                self._setNotificationsInterval()
            case "notify_units":
                self._setNotificationsInterval()
            case "disable_saturday":
                self.disable_sat = settings["disable_saturday"]
                self._checkWeekend()
            case "disable_sunday":
                self.disable_sun = settings["disable_sunday"]
                self._checkWeekend()
            case _:
                pass

    def getCurrentTopics(self):
        """calculate the currrent topics based on the current time"""
        now = datetime.now(tz=TIMEZONE)
        return [
            topic for topic in self.all_topics if (topic.starts <= now <= topic.ends)
        ]

    def getUnsolvedProblems(self):
        """get problems that not been solved"""
        all_problems = self.problems_model.getProblems()
        return [problem for problem in all_problems if not problem.solved]

    def setCurrentTopics(
        self,
        current_topics: list[TopicData],
        current_topic: TopicData | None,
    ):
        """add current topics to the input window"""
        self.input_window.topics.addItems(t.title for t in current_topics)
        if current_topic:
            self.input_window.topics.setCurrentTopic(current_topic.title)

    def setCurrentTRange(self, current_topic: TopicData | None):
        """set current time range on the tray menu"""
        if current_topic:
            min_dt, max_dt = (current_topic.starts, current_topic.ends)
            dsp = f"<b>{min_dt.strftime('%a, %H:%M')} - {max_dt.strftime('%a, %H:%M')}</b>"
            end = f"  (ends about {naturaltime(max_dt)})"
        else:
            dsp = "<b>No topic set for this hour</b>"
            end = '  <a href="add_topic">Add</a>'

        self.input_window.prompt.setText(f"{dsp}{end}")
        self.tray_menu.current_slot.setText(dsp)

    def showEntries(self):
        """show the entries window"""
        self.gui.switchToEntries()
        self.gui.showMaximized()

    def showAddTopic(self, *args):
        """show the settings window for adding new topic"""
        logger.info(f"showAddTopic called with: {args}")
        self.gui.showMaximized()
        self.gui.switchToEntries()
        self.gui.notesview.table_group.new_topic.click()

    def showInputWin(self):
        """popup input window"""
        if self.input_window.isVisible():
            self.input_window.hide()
        else:
            self.input_window.showNormal()

    def from_problemenu(self):
        """add new problem when 'add' from problem menu is triggered"""
        time_now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        new_problem = self.gui.problem_menu.problem()
        topic_title = self.gui.problem_menu.topic()
        topic_id = self._topicIDByTitle(topic_title)
        self.gui.problem_menu.on_done()

        self.handle_problem(time_now, topic_id, new_problem, "")

    def handle_problem(
        self,
        timestamp: str,
        topic_id: int,
        new_problem: str,
        solved: str,
    ):
        """create new problem if does not exists, mark old as solved if exists"""

        changed = False

        if new_problem:
            changed = self.problems_model.newProblem(timestamp, topic_id, new_problem)

        if solved and (solved != SOLVED_PLACEHOLDER):
            solved_id = self._problemID(solved)
            changed = self.problems_model.markSolved(solved_id)

        if changed:  # if problems table changed

            problems = self.getUnsolvedProblems()
            self.input_window.setProblems(problems)

    def logNote(self):
        """add note record to database"""
        time_now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        topic_title = self.input_window.topics.child.currentText()
        topic_id = self._topicIDByTitle(topic_title)
        notes = self.input_window.notes.child.toPlainText()

        new_problem = self.input_window.problem.child.text()
        solved_problem = self.input_window.solved_problem.child.currentText()

        self.handle_problem(time_now, topic_id, new_problem, solved_problem)

        if self.notes_model.newNote(time_now, topic_id, notes):
            self.input_window.clear()
            self.input_window.hide()

    def deleteNote(self):
        """delete note record from database"""
        selected = self.gui.notesview.sRows()
        if selected:
            logs_len = len(selected)
            if self.gui.ask(
                f"{logs_len} {'logs' if logs_len > 1 else 'log'} will be deleted permanently.\nAre you sure you want to delete?"
            ):
                for index in selected:
                    row = index.row()
                    self.notes_model.deleteRowFromTable(row)
                    logger.info(f"Activity at {row} deleted from 'notes' table")

                    # apply changes
                self.notes_model.select()
                self.gui.notesview.table_group.del_btn.hide()

    def saveTopic(self):
        """set topic details in settings to database"""
        time_now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        topic = self.gui.topic_menu.getTopic()
        starts = self.gui.topic_menu.getStart()
        ends = self.gui.topic_menu.getEnds()
        show_notifs = self.gui.topic_menu.showNotifications()

        if self.topics_model.newTopic(time_now, topic, starts, ends, show_notifs):
            self.gui.topic_menu.on_done()
            # show changes right away
            self.onTimeout()

    def deleteTopic(self):
        """delete topic details in settings"""
        rows = self.gui.settingsview.topic_options.sRows()
        rows_len = len(rows)
        logger.info(f"Total to be deleted: {rows_len}")
        if self.gui.ask(
            f"All logs related to {rows_len} {'topics' if rows_len > 1 else 'topic'} will be deleted.\nAre you sure you want to delete?"
        ):

            for index in rows:
                row = index.row()
                self.topics_model.deleteRowFromTable(row)
                logger.info(f"Topic at {row} deleted from 'topics' table")

            # apply changes
            self.topics_model.select()
            self.gui.settingsview.topic_options.disableDnCheck()
            # run check right away
            self.onTimeout()

    def onTimeout(self):
        """
        set current time range,
        set current topic,
        show message
        """
        topics = self.getCurrentTopics()
        current_topic = close_topic(topics)

        self.gui.problem_menu.setTopics(self.all_topics, current=current_topic)

        if current_topic:
            # if topic is disabled or notifications are disabled for the current day
            # show_notifications is given priority
            disabled = (not self.show_notifications) or (not current_topic.enabled)
            # set disabled action checked
            self.tray_menu.disableactn.setChecked(disabled)
        else:
            self.tray_menu.disableactn.setChecked(False)

        problems = self.getUnsolvedProblems()
        self.input_window.setProblems(problems)

        self.setCurrentTRange(current_topic)
        self.setCurrentTopics(topics, current_topic)

        self.showMessage(current_topic)

    def showMessage(self, current_topic: TopicData):
        """show log reminder"""
        if self.input_window.isHidden() and current_topic and self.show_notifications:

            end = naturaltime(current_topic.ends)

            self.tray_icon.showMessage(
                "Click to add Notes.",
                f"{current_topic.title} ends {end}",
                self.app_icon,
                # msecs=10000,
            )

    def onTrayDisable(self, disabled: bool):
        self.gui.settingsview.notifs_options.disable_notifications.disable_all.setChecked(
            disabled
        )
        self.toggleNotifications(disabled)

    def toggleNotifications(self, disabled: bool):
        """show/stop notification messages"""
        if disabled:
            self.show_notifications = False
            logger.info("Notifications disabled")
        else:
            self.show_notifications = True
            logger.info("Notifications enabled")

    def on_topics_changed(self, *args, **kwargs):
        logger.info(f"Data changed in 'topics' model")
        self.all_topics = self.topics_model.getTopics()

        topics = self.getCurrentTopics()
        current_topic = close_topic(topics)

        self.setCurrentTRange(current_topic)
        self.setCurrentTopics(topics, current_topic)

        # select to reflect any new changes
        self.notes_model.select()
        self.problems_model.select()

        self.notes_delegate.setTopics(self.all_topics)
        self.problems_delegate.setTopics(self.all_topics)
        self.gui.problem_menu.setTopics(self.all_topics, current=current_topic)

    def on_problems_changed(self, *args, **kwargs):
        logger.info(f"Data changed in 'problems' model")

        problems = self.getUnsolvedProblems()
        self.input_window.setProblems(problems)


if __name__ == "__main__":
    # run app
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)

    try:
        main = Tracker()
        main.tray_menu.quit.clicked.connect(app.quit)
        main.gui.showMaximized()
        exit_code = app.exec()
    finally:
        settings.save()

    sys.exit(exit_code)
