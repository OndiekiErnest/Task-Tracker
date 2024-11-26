"""PyQt6 windows and widgets"""

import logging
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QMessageBox,
)
from PyQt6.QtGui import QIcon
from models import CommentsModel, TopicsModel, ProblemsModel
from customwidgets.menus import NewTopicMenu, NewProblemMenu
from screens.settings import SettingsWindow
from screens.comments import CommentsWindow
from constants import APP_ICON, ENTRIES_ICON, SETTINGS_ICON


logger = logging.getLogger(__name__)


class MainWindow(QWidget):
    """main application window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle("TLog")
        self.setWindowIcon(QIcon(APP_ICON))

        layout = QVBoxLayout(self)

        self.topic_menu = NewTopicMenu(self)

        self.problem_menu = NewProblemMenu(self)

        # widgets
        self.commentsview = CommentsWindow()
        self.commentsview.table_group.new_topic.setMenu(self.topic_menu)

        self.settingsview = SettingsWindow()
        self.settingsview.topic_options.new_topic.setMenu(self.topic_menu)
        self.settingsview.problem_options.new_problem.setMenu(self.problem_menu)

        self.tabwidget = QTabWidget()
        self.tabwidget.setTabBarAutoHide(True)
        self.tabwidget.setMovable(True)
        self.tabwidget.setDocumentMode(True)

        layout.addWidget(self.tabwidget)

        # add views to tab widget
        self.tabwidget.addTab(self.commentsview, QIcon(ENTRIES_ICON), "Entries")
        self.tabwidget.addTab(self.settingsview, QIcon(SETTINGS_ICON), "Settings")

    def switchToEntries(self):
        """make entries the active tab"""
        index = self.tabwidget.indexOf(self.commentsview)
        self.tabwidget.setCurrentIndex(index)

    def switchToSettings(self):
        """make settings the active tab"""
        index = self.tabwidget.indexOf(self.settingsview)
        self.tabwidget.setCurrentIndex(index)

    def setCommentsModel(self, model: CommentsModel):
        """set database model"""
        self.commentsview.setModel(model)

    def setTopicsModel(self, model: TopicsModel):
        """set model for topics"""
        self.settingsview.setTopicsModel(model)

    def setProblemsModel(self, model: ProblemsModel):
        """set model for problems"""
        self.settingsview.setProblemsModel(model)

    def ask(self, quiz: str):
        return (
            QMessageBox.question(
                self,
                "Action Confirmation",
                quiz,
            )
            == QMessageBox.StandardButton.Yes
        )

    def inform(self, info: str):
        QMessageBox.information(
            self,
            "Action Feedback",
            info,
        )

    def closeEvent(self, event):
        self.hide()
        event.ignore()
