"""custom line edits"""

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QIcon
from constants import SEARCH_ICON


class SearchInput(QLineEdit):
    """search line edit"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(300)

        self.setClearButtonEnabled(True)
        self.addAction(QIcon(SEARCH_ICON), QLineEdit.ActionPosition.LeadingPosition)
        self.setPlaceholderText("Search...")
