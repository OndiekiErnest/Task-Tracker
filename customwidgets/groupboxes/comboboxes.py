"""QComboBox in a named QGroupBox"""

from typing import Iterable
from PyQt6.QtWidgets import QComboBox
from .base import NamedItem


class NamedCombobox(NamedItem):
    """QComboBox in a QGroupBox"""

    def __init__(self, *args, **kwargs):

        self.child = QComboBox()
        self.child.setMaxVisibleItems(15)

        super().__init__(*args, **kwargs)

    def addItems(self, topics: Iterable[str]):
        """clear before adding"""
        self.child.clear()
        self.child.addItems(topics)

    def setCurrentTopic(self, title: str):
        """set title as current text"""
        self.child.setCurrentText(title)
