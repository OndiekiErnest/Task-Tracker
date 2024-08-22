"""functions to work with system color schemes"""

import logging
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)


def isDarkMode() -> bool | None:
    """check if system is in dark mode"""
    if app := QApplication.instance():
        theme = app.styleHints().colorScheme().name
        logger(f"Current colorScheme: {theme}")
        return theme == "Dark"
    else:
        logger.error("Couldn't check system theme: No application instance found")
        return
