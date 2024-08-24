"""PyQt6 windows and widgets"""

import logging
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
)
from PyQt6.QtGui import QIcon
from models import CommentsModel, TopicsModel
from screens.settings import SettingsWindow
from screens.comments import CommentsWindow
from constants import APP_ICON, ACTIVITIES_ICON, SETTINGS_ICON


logger = logging.getLogger(__name__)


class MainWindow(QWidget):
    """main application window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle("TLog")
        self.setWindowIcon(QIcon(APP_ICON))

        layout = QVBoxLayout(self)

        # widgets
        self.commentsview = CommentsWindow()

        self.settingsview = SettingsWindow()

        self.tabwidget = QTabWidget()
        self.tabwidget.setTabBarAutoHide(True)
        self.tabwidget.setMovable(True)
        self.tabwidget.setDocumentMode(True)

        layout.addWidget(self.tabwidget)

        # add views to tab widget
        self.tabwidget.addTab(self.commentsview, QIcon(ACTIVITIES_ICON), "Activities")
        self.tabwidget.addTab(self.settingsview, QIcon(SETTINGS_ICON), "Settings")

    def switchToActivities(self):
        """make activities the active tab"""
        index = self.tabwidget.indexOf(self.commentsview)
        self.tabwidget.setCurrentIndex(index)

    def switchToSettings(self):
        """make settings the active tab"""
        index = self.tabwidget.indexOf(self.settingsview)
        self.tabwidget.setCurrentIndex(index)

    def setCommentsModel(self, model: CommentsModel):
        """set database model"""
        self.commentsview.setModel(model)

    def setSettingsModel(self, model: TopicsModel):
        """set model for topics"""
        self.settingsview.setModel(model)

    def closeEvent(self, event):
        self.hide()
        event.ignore()
