"""custom QWidget with widgets to be used in QDataWidgetMapper"""

from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from customwidgets.groupboxes import (
    NamedPlainTextEdit,
    NamedCombobox,
)


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
        self.prev_btn = QPushButton("<<")
        self.save_btn = QPushButton("Update")
        self.next_btn = QPushButton(">>")
        self.cancel_btn = QPushButton("Cancel")

        buttonslayout.addWidget(self.delete_btn)
        buttonslayout.addWidget(self.prev_btn)
        buttonslayout.addWidget(self.save_btn)
        buttonslayout.addWidget(self.next_btn)
        buttonslayout.addWidget(self.cancel_btn)
        # add buttons at the bottom
        layout.addLayout(buttonslayout)

    def addTopics(self, topics: list):
        """add topics to the topic"""
        self.topic_edit.child.clear()
        self.topic_edit.addItems(topics)

    def clear(self):
        """clear fields"""
        self.comment_edit.child.clear()
