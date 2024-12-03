"""QLineEdit in a named QGroupBox"""

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QValidator
from .base import NamedItem


class WordCountValidator(QValidator):
    def __init__(self, max_words, parent=None):
        super().__init__(parent)
        self.max_words = max_words

    def validate(self, input_str, pos):
        # split the input string by whitespace
        words = input_str.split()
        word_count = len(words)

        # if word count exceeds the max limit, invalidate
        if word_count > self.max_words:
            return QValidator.State.Invalid, input_str, pos

        # else, acceptable
        return QValidator.State.Acceptable, input_str, pos


class NamedLineEdit(NamedItem):
    """QLineEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        validator = WordCountValidator(7, parent=self)

        self.child = QLineEdit()
        self.child.setValidator(validator)

        super().__init__(*args, **kwargs)
