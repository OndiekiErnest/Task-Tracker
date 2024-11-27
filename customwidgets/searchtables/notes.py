"""searchable table for the notes model"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from constants import ADD_ICON
from .base import SearchableTable


class CommentsTableview(SearchableTable):
    """comments table viewer"""

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def _create_btns(self):
        """create top horizontal buttons"""

        # create delete and more btns
        self._default_btns()

        self.new_topic = QPushButton("Topic")
        self.new_topic.setIcon(QIcon(ADD_ICON))

        self.new_comment = QPushButton("Notes")
        self.new_comment.setIcon(QIcon(ADD_ICON))

        # add extended btns
        self.btnslayout.addWidget(self.new_topic, alignment=Qt.AlignmentFlag.AlignLeft)
        self.btnslayout.addWidget(self.new_comment)
        # default btns/widgets
        self.btnslayout.addWidget(self.more_btn)
        self.btnslayout.addWidget(self.del_btn)
        self.btnslayout.addStretch()
        self.btnslayout.addWidget(self.search, alignment=Qt.AlignmentFlag.AlignRight)
