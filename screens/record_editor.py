"""custom QWidget with widgets to be used in QDataWidgetMapper"""

from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QIcon
from customwidgets.groupboxes import (
    NamedPlainTextEdit,
    NamedCombobox,
)
from constants import UNDO_ICON, NEXT_ICON, PREVIOUS_ICON, DELETE_ICON, SUBMIT_ICON


class RecordsEditor(QWidget):
    """database row editor widgets"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMaximumWidth(800)

        layout = QVBoxLayout(self)

        buttonslayout = QHBoxLayout()

        self.topic_edit = NamedCombobox("Topic Title")

        self.comment_edit = NamedPlainTextEdit("Comments")

        layout.addWidget(self.topic_edit)
        layout.addWidget(self.comment_edit)

        # buttons
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setIcon(QIcon(DELETE_ICON))
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(QIcon(PREVIOUS_ICON))
        self.save_btn = QPushButton("Update")
        self.save_btn.setIcon(QIcon(SUBMIT_ICON))
        self.next_btn = QPushButton()
        self.next_btn.setIcon(QIcon(NEXT_ICON))
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.setIcon(QIcon(UNDO_ICON))

        buttonslayout.addWidget(self.delete_btn)
        buttonslayout.addWidget(self.prev_btn)
        buttonslayout.addWidget(self.save_btn)
        buttonslayout.addWidget(self.next_btn)
        buttonslayout.addWidget(self.undo_btn)
        # add buttons at the bottom
        layout.addLayout(buttonslayout)

    def addTopics(self, topics: list):
        """add topics to the topic"""
        self.topic_edit.child.clear()
        self.topic_edit.addItems(topics)

    def clear(self):
        """clear fields"""
        self.comment_edit.child.clear()
