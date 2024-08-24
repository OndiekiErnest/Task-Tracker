"""functions to work with system color schemes"""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)


def isDarkMode() -> bool:
    """check if system is set to dark mode"""
    if app := QApplication.instance():
        theme = app.styleHints().colorScheme()
        logger.info(f"Current colorScheme: {theme.name}")
        return theme == Qt.ColorScheme.Dark
    else:
        logger.error("No application instance found: Creating one...")
        app = QApplication(sys.argv)
        theme = app.styleHints().colorScheme()
        logger.info(f"Current colorScheme: {theme.name}")
        return theme == Qt.ColorScheme.Dark
