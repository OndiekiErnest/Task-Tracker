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
from constants import APP_DB, APP_ICON, TIMEZONE
from customwidgets.menus import TrayMenu
from screens.log_input import InputPopup
from datas import TopicData
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

        self.app_icon = QIcon(APP_ICON)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(APP_DB)
        self.db.open()

        self.query = QSqlQuery(self.db)

        if self.db.isOpen():
            logger.info("SQLite file opened successfully")
        else:
            logger.error("SQLite did not open")

        self.gui = MainWindow()

        self.input_window = InputPopup()
        self.input_window.setWindowIcon(self.app_icon)
        # link buttons
        self.input_window.submit.clicked.connect(self.logActivity)

        self.notification_timer = QTimer(self.gui)

        # models
        self.comments_model = CommentsModel(self.db)
        self.topics_model = TopicsModel(self.db)

        self.gui.setCommentsModel(self.comments_model)
        self.gui.setSettingsModel(self.topics_model)

        self.all_topics = self.getTopics()

        self.topics_model.dataChanged.connect(self.on_data_changed)
        self.topics_model.rowsInserted.connect(self.on_rows_inserted)
        self.topics_model.rowsRemoved.connect(self.on_rows_removed)
        self.topics_model.layoutChanged.connect(self.on_layout_changed)

        # database viewer
        self.gui.databaseview.add_record.clicked.connect(self.showInputWin)
        self.gui.databaseview.delete_record.clicked.connect(self.deleteActivity)
        # settings
        self.gui.settingsview.activity_adder.addbtn.clicked.connect(self.saveTopic)
        self.gui.settingsview.activity_adder.deletebtn.clicked.connect(self.removeTopic)

        self.tray_menu = TrayMenu()
        self.tray_menu.addlog.clicked.connect(self.showInputWin)
        self.tray_menu.more.clicked.connect(self.gui.showMaximized)

        self.tray_icon = QSystemTrayIcon(self.app_icon, self.gui)
        self.tray_icon.setToolTip("TLog - Time Tracker")
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.messageClicked.connect(self.showInputWin)
        self.tray_icon.show()

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

    def setCurrentTopics(self):
        """add current topics to the input window"""
        tpcs = [t.title for t in self.getCurrentTopics()]
        self.input_window.topic.addItems(tpcs)

    def setCurrentTRange(self):
        """set current time range on the tray menu"""
        current_topics = self.getCurrentTopics()
        if current_topics:
            min_dt, max_dt = (
                min((t.starts for t in current_topics)),
                max((t.ends for t in current_topics)),
            )
            dsp = f"<b>{min_dt.strftime('%a, %H:%M')} - {max_dt.strftime('%a, %H:%M')}</b>"
        else:
            dsp = "<b>No task set</b>"
        self.tray_menu.current_slot.setText(dsp)

    def showInputWin(self):
        """popup input window"""
        if self.input_window.isVisible():
            self.input_window.hide()
        else:
            self.input_window.showNormal()

    def logActivity(self):
        """add activity record to database"""
        time_now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        topic = self.input_window.topic.child.text()
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
        rows = self.gui.databaseview.sRows()
        for index in reversed(rows):
            row = index.row()
            self.comments_model.deleteRowFromTable(row)
            logger.info(f"Activity at {row} deleted from 'comments' table")
        # apply changes
        self.comments_model.select()

    def saveTopic(self):
        """set topic details in settings to database"""
        time_now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        topic = self.gui.settingsview.activity_adder.getTopic()
        start = self.gui.settingsview.activity_adder.getStart()
        span = self.gui.settingsview.activity_adder.getSpan()

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
            self.gui.settingsview.activity_adder.clearInputs()
            logger.info(f"Set topic '{topic}'")
        else:
            logger.error(
                f"DB error setting topic: {self.query.lastError().driverText()}"
            )

    def removeTopic(self):
        """delete topic details in settings"""
        rows = self.gui.settingsview.activity_adder.sRows()
        for index in reversed(rows):
            row = index.row()
            self.topics_model.deleteRowFromTable(row)
            logger.info(f"Topic at {row} deleted from 'topics' table")
        # apply changes
        self.topics_model.select()
        self.gui.settingsview.activity_adder.disableDnCheck()

    def showMessage(self):
        """show log reminder"""
        tpcs = self.getCurrentTopics()
        ending = max((t.ends for t in tpcs))
        self.tray_icon.showMessage(
            "Click this message. Log what you are working on.",
            f"You have {len(tpcs)} tasks ending {naturaltime(ending)}",
            msecs=10000,
        )

    def toggleNotifications(self, disabled: bool):
        """show/stop notification messages"""
        if disabled:
            self.notification_timer.stop()
        else:
            self.notification_timer.start()

    def on_data_changed(self, topLeft, bottomRight, roles: list[int]):
        self.all_topics = self.getTopics()

    def on_rows_inserted(self, parent, first: int, last: int):
        self.all_topics = self.getTopics()

    def on_rows_removed(self, parent, first: int, last: int):
        self.all_topics = self.getTopics()

    def on_layout_changed(self):
        self.all_topics = self.getTopics()


if __name__ == "__main__":
    # run app
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)

    main = Tracker()
    main.tray_menu.quit.clicked.connect(app.quit)
    main.gui.showMaximized()

    sys.exit(app.exec())
