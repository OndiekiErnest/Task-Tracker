"""The C in MVC"""

import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtCore import QTimer
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtGui import QIcon
from humanize import naturaltime
from gui import MainWindow
from models import CommentsModel, TopicsModel
from constants import APP_DB, APP_ICON, TIMEZONE, TIME_UNITS
from customwidgets.menus import TrayMenu
from screens.log_input import InputPopup
from datastructures.datas import TopicData
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

        self.app_icon = QIcon(APP_ICON)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(APP_DB)
        self.db.open()

        self.query = QSqlQuery(self.db)

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
        self.input_window.submit.clicked.connect(self.logActivity)

        self.notification_timer = QTimer(self.gui)
        self.notification_timer.timeout.connect(self.onTimeout)
        self._setNotificationsInterval()
        self.notification_timer.start()

        # models
        self.comments_model = CommentsModel(self.db)
        self.topics_model = TopicsModel(self.db)

        self.all_topics = self.getTopics()
        self.onTopicsChange()

        self.gui.setCommentsModel(self.comments_model)
        self.gui.setSettingsModel(self.topics_model)

        self.topics_model.modelReset.connect(self.on_data_changed)

        # database viewer
        self.gui.commentsview.add_record.clicked.connect(self.showInputWin)
        self.gui.commentsview.model_editor.delete_btn.clicked.connect(
            self.deleteActivity
        )
        # settings
        self.gui.settingsview.topic_adder.addbtn.clicked.connect(self.saveTopic)
        self.gui.settingsview.topic_adder.deletebtn.clicked.connect(self.deleteTopic)

        self.tray_menu = TrayMenu()
        self.tray_menu.addlog.clicked.connect(self.input_window.showNormal)
        self.tray_menu.addtopic_action.triggered.connect(self.showAddTopic)
        self.tray_menu.more.clicked.connect(self.showActivities)

        self.tray_menu.disableactn.toggled.connect(self.onTrayDisable)
        self.gui.settingsview.disable_notifications.disable_all.toggled.connect(
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

    def getCurrentTopics(self):
        """calculate the currrent topics based on the current time"""
        now = datetime.now(tz=TIMEZONE)
        return [topic for topic in self.all_topics if topic.starts <= now <= topic.ends]

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
            dsp = "<b>No task set for this hour</b>"
            end = ""

        self.input_window.prompt.setText(f"{dsp}{end}")
        self.tray_menu.current_slot.setText(dsp)

    def showActivities(self):
        """show the activities window"""
        self.gui.switchToActivities()
        self.gui.showMaximized()

    def showAddTopic(self):
        """show the settings window for adding new topic"""
        self.gui.switchToSettings()
        self.gui.showMaximized()

    def showInputWin(self):
        """popup input window"""
        if self.input_window.isVisible():
            self.input_window.hide()
        else:
            self.input_window.showNormal()

    def logActivity(self):
        """add activity record to database"""
        time_now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        topic = self.input_window.topic.child.currentText()
        comments = self.input_window.comments.child.toPlainText()

        self.query.prepare(
            """
            INSERT INTO comments (timestamp, topic, comment)
            VALUES (?, ?, ?)
            """
        )
        self.query.addBindValue(time_now)
        self.query.addBindValue(topic)
        self.query.addBindValue(comments)
        success = self.query.exec()
        if success:
            self.comments_model.select()
            self.input_window.comments.child.clear()
            self.input_window.hide()
            logger.info(f"Added comment related to '{topic}'")
        else:
            logger.error(
                f"DB error adding comments: {self.query.lastError().driverText()}"
            )

    def deleteActivity(self):
        """delete activity record from database"""
        row = self.gui.commentsview.mapper.currentIndex()
        self.gui.commentsview.model_editor.clear()
        self.comments_model.deleteRowFromTable(row)
        logger.info(f"Activity at {row} deleted from 'comments' table")
        # apply changes
        self.comments_model.select()
        self.gui.commentsview.mapper.toPrevious()

    def saveTopic(self):
        """set topic details in settings to database"""
        time_now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        topic = self.gui.settingsview.topic_adder.getTopic()
        start = self.gui.settingsview.topic_adder.getStart()
        span = self.gui.settingsview.topic_adder.getSpan()

        self.query.prepare(
            """
            INSERT INTO topics (timestamp, topic, start, span)
            VALUES (?, ?, ?, ?)
            """
        )
        self.query.addBindValue(time_now)
        self.query.addBindValue(topic)
        self.query.addBindValue(start)
        self.query.addBindValue(span)
        success = self.query.exec()
        if success:
            self.topics_model.select()
            self.gui.settingsview.topic_adder.clearInputs()
            self.gui.settingsview.topic_adder.addSpan()
            logger.info(f"Set topic '{topic}'")
        else:
            logger.error(
                f"DB error setting topic: {self.query.lastError().driverText()}"
            )

    def deleteTopic(self):
        """delete topic details in settings"""
        rows = self.gui.settingsview.topic_adder.sRows()
        for index in reversed(rows):
            row = index.row()
            self.topics_model.deleteRowFromTable(row)
            logger.info(f"Topic at {row} deleted from 'topics' table")
        # apply changes
        self.topics_model.select()
        self.gui.settingsview.topic_adder.disableDnCheck()

    def onTimeout(self):
        """
        set current time range,
        set current topic,
        show message
        """
        topics = self.getCurrentTopics()

        self.setCurrentTRange(topics)
        self.setCurrentTopics(topics)
        self.showMessage(topics)

    def showMessage(self, current_topics: list):
        """show log reminder"""
        if current_topics and self.notification_timer.isActive():
            tp_len = len(current_topics)
            end = naturaltime(max((t.ends for t in current_topics)))

            self.tray_icon.showMessage(
                "How is the task going?",
                f"Log your achievements. \n{tp_len} {'tasks' if tp_len > 1 else 'task'} ending {end}",
                self.app_icon,
                msecs=10000,
            )

    def onTrayDisable(self, disabled: bool):
        self.gui.settingsview.disable_notifications.disable_all.setChecked(disabled)
        self.toggleNotifications(disabled)

    def toggleNotifications(self, disabled: bool):
        """show/stop notification messages"""
        if disabled:
            self.notification_timer.stop()
            logger.info("Notifications disabled")
        else:
            self.notification_timer.start()
            logger.info("Notifications enabled")

    def on_data_changed(self):
        logger.info("Data changed in 'topics' model")
        self.all_topics = self.getTopics()
        self.onTopicsChange()

    def onTopicsChange(self):
        self.gui.commentsview.model_editor.addTopics(self.all_topics)


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
