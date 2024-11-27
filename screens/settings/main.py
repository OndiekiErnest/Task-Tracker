"""application settings"""

import logging
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from customwidgets.frames import Line
from customwidgets.searchtables import ProblemsTableview, TopicsTableview
from customwidgets.delegates import TopicsDelegate
from models import TopicsModel, ProblemsModel
from .notifications import NotificationsSettings


logger = logging.getLogger(__name__)


class SettingsWindow(QScrollArea):
    """settings window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWidgetResizable(True)
        self.setFrameStyle(0)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        swidget = QWidget()
        swidget.setMaximumWidth(900)

        layout = QVBoxLayout(swidget)
        layout.setContentsMargins(6, 20, 6, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.setWidget(swidget)

        # notifications group
        self.notifs_options = NotificationsSettings()

        # widgets
        # topics viewer and settings
        self.topic_options = TopicsTableview("Topics")
        self.topic_options.setItemDelegate(TopicsDelegate())

        # problems section
        self.problem_options = ProblemsTableview("Problems")

        layout.addWidget(self.notifs_options)
        layout.addWidget(Line())
        layout.addWidget(self.topic_options)
        layout.addWidget(Line())
        layout.addWidget(self.problem_options)

    def setTopicsModel(self, model: TopicsModel):
        """set model for topics"""
        logger.info(f"Model set to '{model}'")
        self.topic_options.setModel(model)

        self.topic_options.hideColumn(model.fieldIndex("id"))
        self.topic_options.hideColumn(model.fieldIndex("timestamp"))
        self.topic_options.hideColumn(model.fieldIndex("enabled"))

    def setProblemsModel(self, model: ProblemsModel):
        """set model for problems"""
        logger.info(f"Model set to '{model}'")
        self.problem_options.setModel(model)

        self.problem_options.hideColumn(model.fieldIndex("id"))
        self.problem_options.hideColumn(model.fieldIndex("timestamp"))
        self.problem_options.hideColumn(model.fieldIndex("solved"))
