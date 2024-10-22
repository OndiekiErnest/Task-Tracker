"""The C in MVC"""

import re
import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtCore import QTimer
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtGui import QIcon
from humanize import naturaltime
from gui import MainWindow
from models import CommentsModel, TopicsModel, ProblemsModel
from constants import APP_DB, APP_ICON, TIMEZONE, TIME_UNITS, SOLVED_PLACEHOLDER
from customwidgets.menus import TrayMenu
from customwidgets.delegates import CommentsDelegate
from screens.comment_input import InputPopup
from datastructures.datas import TopicData, ProblemData
from datastructures.settings import settings
from qstyles import STYLE


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
            logger.error("SQLite did not open")

        settings.signals.changes_made.connect(self.onSettingsChange)

        self.gui = MainWindow()

        self.input_window = InputPopup()
        self.input_window.setWindowIcon(self.app_icon)
        # link buttons
        self.input_window.submit.clicked.connect(self.logComment)
        self.input_window.prompt.linkActivated.connect(self.showAddTopic)

        self.notification_timer = QTimer(self.gui)
        self.notification_timer.timeout.connect(self.onTimeout)
        self._setNotificationsInterval()
        self.notification_timer.start()

        # models
        self.comments_model = CommentsModel(self.db)
        self.topics_model = TopicsModel(self.db)
        self.problems_model = ProblemsModel(self.db)

        self.all_topics = self.getTopics()
        self.all_problems = self.getProblems()

        self.gui.setCommentsModel(self.comments_model)
        self.gui.setSettingsModel(self.topics_model)

        self.comments_delegate = CommentsDelegate()
        self.gui.commentsview.tableview.setItemDelegate(self.comments_delegate)

        self.topics_model.modelReset.connect(self.on_topics_changed)
        self.topics_model.dataChanged.connect(self.on_topics_changed)
        # self.topics_model.layoutChanged.connect(self.on_data_changed)
        self.topics_model.rowsRemoved.connect(self.on_topics_changed)

        self.topics_model.modelReset.connect(self.on_problems_changed)
        self.topics_model.dataChanged.connect(self.on_problems_changed)
        self.topics_model.rowsRemoved.connect(self.on_problems_changed)

        # comments viewer btns
        self.gui.commentsview.add_record.clicked.connect(self.showInputWin)
        self.gui.commentsview.delete_btn.clicked.connect(self.deleteComment)
        # settings
        self.gui.settingsview.topic_adder.addbtn.clicked.connect(self.saveTopic)
        self.gui.settingsview.topic_adder.deletebtn.clicked.connect(self.deleteTopic)
        self.gui.commentsview.search_input.textChanged.connect(self.onSearch)

        self.tray_menu = TrayMenu()
        self.tray_menu.addlog.clicked.connect(self.input_window.showNormal)
        self.tray_menu.addtopic_action.triggered.connect(self.showAddTopic)
        self.tray_menu.more.clicked.connect(self.showActivities)

        self.tray_menu.disableactn.toggled.connect(self.onTrayDisable)
        self.gui.settingsview.notifs_group.disable_notifications.disable_all.toggled.connect(
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
        for p in self.all_problems:
            if p.problem == problem:
                return p.problem_id

    def _setNotificationsInterval(self):
        """update notification interval"""
        after = settings["notify_after"] * TIME_UNITS[settings["notify_units"]]
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
        self.comments_delegate.setTopics(self.all_topics)
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

    def getTopics(self):
        """prepare topics, and their details"""
        # get the number of rows
        row_count = self.topics_model.rowCount()

        # create a list to store rows as tuples
        topics_list = []
        # iterate over each row and column to collect data
        for row in range(row_count):
            # get the QSqlRecord for the row
            record = self.topics_model.record(row)
            topic_kw = {}
            # extract row data
            for c in range(record.count()):
                value = record.value(c)
                match c:
                    case 0:
                        topic_kw["topic_id"] = value
                    case 1:
                        topic_kw["created"] = datetime.strptime(
                            value, "%Y-%m-%d %H:%M:%S"
                        )
                    case 2:
                        # title
                        topic_kw["title"] = value
                    case 3:
                        dt = datetime.now(tz=TIMEZONE)
                        hr, mins, secs = value.split(":")
                        topic_kw["starts"] = dt.replace(
                            hour=int(hr),
                            minute=int(mins),
                            second=int(secs),
                        )
                    case 4:
                        topic_kw["span"] = int(value)
                    case 5:
                        topic_kw["enabled"] = bool(value)
                    case _:
                        pass

            topics_list.append(TopicData(**topic_kw))
        # sort based on the starts
        topics_list.sort(key=lambda t: t.starts)
        return topics_list

    def getProblems(self):
        """create problems data"""

        # get the number of rows
        row_count = self.problems_model.rowCount()

        # create a list to store rows as ProblemData instances
        problems_list: list[ProblemData] = []
        # iterate over each row and column to collect data
        for row in range(row_count):
            # get the QSqlRecord for the row
            record = self.problems_model.record(row)
            problem_kw = {}
            # extract row data
            for c in range(record.count()):
                value = record.value(c)
                match c:
                    case 0:
                        problem_kw["problem_id"] = value
                    case 1:
                        problem_kw["created"] = datetime.strptime(
                            value, "%Y-%m-%d %H:%M:%S"
                        )
                    case 2:
                        problem_kw["problem"] = value
                    case 3:
                        problem_kw["topic_id"] = value
                    case 4:
                        problem_kw["solved"] = bool(value)
                    case _:
                        pass

            problems_list.append(ProblemData(**problem_kw))

        problems_list.sort(key=lambda p: p.created)
        return problems_list

    def getCurrentTopics(self):
        """calculate the currrent topics based on the current time"""
        now = datetime.now(tz=TIMEZONE)
        return [topic for topic in self.all_topics if topic.starts <= now <= topic.ends]

    def getUnsolvedProblems(self):
        """get problems that not been solved"""
        return [problem for problem in self.all_problems if not problem.solved]

    def setCurrentTopics(self, current_topics: list):
        """add current topics to the input window"""
        self.input_window.topic.addItems(current_topics)

    def setCurrentTRange(self, current_topics: list):
        """set current time range on the tray menu"""
        if current_topics:
            min_dt, max_dt = (
                min((t.starts for t in current_topics)),
                max((t.ends for t in current_topics)),
            )
            dsp = f"<b>{min_dt.strftime('%a, %H:%M')} - {max_dt.strftime('%a, %H:%M')}</b>"
            end = f"  (ends about {naturaltime(max_dt)})"
        else:
            dsp = "<b>No topic set for this hour</b>"
            end = '  <a href="add_topic">Add</a>'

        self.input_window.prompt.setText(f"{dsp}{end}")
        self.tray_menu.current_slot.setText(dsp)

    def showActivities(self):
        """show the activities window"""
        self.gui.switchToActivities()
        self.gui.showMaximized()

    def showAddTopic(self, *args):
        """show the settings window for adding new topic"""
        logger.info(f"showAddTopic called with: {args}")
        self.gui.switchToSettings()
        self.gui.showMaximized()

    def showInputWin(self):
        """popup input window"""
        if self.input_window.isVisible():
            self.input_window.hide()
        else:
            self.input_window.showNormal()

    def handle_problem(self, timestamp: str, topic_id: int, new: str, solved: str):
        """create new problem if exists, mark old as solved if exists"""
        problems_changed = False

        if new:
            query = QSqlQuery(self.db)
            query.prepare(
                """
                INSERT INTO problems (timestamp, problem, topic_id)
                VALUES (?, ?, ?)
                """
            )
            query.addBindValue(timestamp)
            query.addBindValue(new)
            query.addBindValue(topic_id)

            if query.exec():
                problems_changed = True
                logger.info("Added problem to table")
            else:
                logger.error(
                    f"DB error adding problem: {query.lastError().driverText()}"
                )

        if solved and (solved != SOLVED_PLACEHOLDER):
            solved_id = self._problemID(solved)

            query = QSqlQuery(self.db)
            query.prepare("UPDATE problems SET solved = 1 WHERE id = ?")
            query.addBindValue(solved_id)

            if query.exec():
                problems_changed = True
                logger.info(f"Problem marked as solved: '{solved}'")
            else:
                logger.error(
                    f"DB error updating problem: {query.lastError().driverText()}"
                )

        if problems_changed:

            self.problems_model.select()
            self.all_problems = self.getProblems()

            problems = self.getUnsolvedProblems()
            self.input_window.setProblems(problems)

    def logComment(self):
        """add comment record to database"""
        time_now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        topic_title = self.input_window.topic.child.currentText()
        topic_id = self._topicIDByTitle(topic_title)
        comments = self.input_window.comments.child.toPlainText()

        new_problem = self.input_window.problem.child.text()
        solved_problem = self.input_window.solved_problem.child.currentText()

        self.handle_problem(time_now, topic_id, new_problem, solved_problem)

        query = QSqlQuery(self.db)
        query.prepare(
            """
            INSERT INTO comments (timestamp, topic_id, comment)
            VALUES (?, ?, ?)
            """
        )
        query.addBindValue(time_now)
        query.addBindValue(topic_id)
        query.addBindValue(comments)

        if query.exec():
            self.comments_model.select()
            self.input_window.clear()
            self.input_window.hide()
            logger.info(f"Added comment related to '{topic_id} - {topic_title}'")
        else:
            logger.error(f"DB error adding comments: {query.lastError().driverText()}")

    def deleteComment(self):
        """delete comment record from database"""
        selected = self.gui.commentsview.sRows()
        if selected:
            logs_len = len(selected)
            if self.gui.ask(
                f"{logs_len} {'logs' if logs_len > 1 else 'log'} will be deleted permanently.\nAre you sure you want to delete?"
            ):
                for index in selected:
                    row = index.row()
                    self.comments_model.deleteRowFromTable(row)
                    logger.info(f"Activity at {row} deleted from 'comments' table")
                    # apply changes
                self.comments_model.select()

    def saveTopic(self):
        """set topic details in settings to database"""
        time_now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        topic = self.gui.settingsview.topic_adder.getTopic()
        start = self.gui.settingsview.topic_adder.getStart()
        span = self.gui.settingsview.topic_adder.getSpan()

        query = QSqlQuery(self.db)
        query.prepare(
            """
            INSERT INTO topics (timestamp, topic, start, span)
            VALUES (?, ?, ?, ?)
            """
        )
        query.addBindValue(time_now)
        query.addBindValue(topic)
        query.addBindValue(start)
        query.addBindValue(span)

        if query.exec():
            self.topics_model.select()
            logger.info(f"comments selected: {self.comments_model.select()}")
            self.gui.settingsview.topic_adder.clearInputs()
            self.gui.settingsview.topic_adder.addSpan()
            # show changes right away
            self.onTimeout()
            logger.info(f"Set topic '{topic}'")
        else:
            logger.error(f"DB error setting topic: {query.lastError().driverText()}")

    def deleteTopic(self):
        """delete topic details in settings"""
        rows = self.gui.settingsview.topic_adder.sRows()
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
            logger.info(f"comments selected: {self.comments_model.select()}")
            self.gui.settingsview.topic_adder.disableDnCheck()
            # run check right away
            self.onTimeout()

    def onSearch(self, text: str):
        """search and filter"""
        # TODO: Improve search
        ss = re.sub(r"[\W_]+", "", text.strip().lower())
        if ss:
            filter_query = (
                f'comments.comment LIKE "%{ss}%" OR comments.timestamp LIKE "%{ss}%"'
            )
            self.comments_model.setFilter(filter_query)
        else:
            self.comments_model.setFilter("")  # remove the filter to show all records

    def onTimeout(self):
        """
        set current time range,
        set current topic,
        show message
        """
        topics = self.getCurrentTopics()
        # if notifications are enabled
        if self.show_notifications:
            # if not all topics are enabled
            disabled = not all((t.enabled for t in topics))
            # set disabled action checked
            self.tray_menu.disableactn.setChecked(disabled)

        problems = self.getUnsolvedProblems()
        self.input_window.setProblems(problems)

        self.setCurrentTRange(topics)
        self.setCurrentTopics(topics)

        self.showMessage(topics)

    def showMessage(self, current_topics: list):
        """show log reminder"""
        if current_topics and self.show_notifications:
            tp_len = len(current_topics)
            end = naturaltime(max((t.ends for t in current_topics)))

            self.tray_icon.showMessage(
                "How is the topic going?",
                f"Log your achievements. \n{tp_len} {'topics' if tp_len > 1 else 'topic'} ending {end}",
                self.app_icon,
                # msecs=10000,
            )

    def onTrayDisable(self, disabled: bool):
        self.gui.settingsview.notifs_group.disable_notifications.disable_all.setChecked(disabled)
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
        logger.info("Data changed in 'topics' model")
        self.all_topics = self.getTopics()

        topics = self.getCurrentTopics()
        self.setCurrentTRange(topics)
        self.setCurrentTopics(topics)

        self.comments_model.select()

        self.comments_delegate.setTopics(self.all_topics)

    def on_problems_changed(self, *args, **kwargs):
        logger.info("Data changed in 'problems' model")
        self.all_problems = self.getProblems()

        problems = self.getUnsolvedProblems()
        self.input_window.setProblems(problems)

        # self.problems_delegate.setTopics(self.all_topics)


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
