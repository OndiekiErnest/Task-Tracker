"""custom QWidget with widgets for typing and saving user logs"""

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from customwidgets.groupboxes import NamedCombobox, NamedPlainTextEdit, NamedLineEdit
from constants import ADDCOMMENT_ICON, SOLVED_PLACEHOLDER


placeholder = """
An example:
- The lessons you have learnt
- The goals you have achieved
- The problems you have solved
- The challenges you're facing
"""

class InputPopup(QWidget):
    """log form widget"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("TLog - Log Activity")

        layout = QVBoxLayout(self)

        # initialize the animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)

        # what are you doing right now; What are you up to?
        self.prompt = QLabel("<b>What are you up to?</b>")
        self.prompt.setOpenExternalLinks(False)
        self.prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.prompt)

        # form widgets
        self.topics = NamedCombobox("Current Topic")
        self.topics.child.currentTextChanged.connect(self.enableSubmit)

        self.notes = NamedPlainTextEdit("Describe the activity")
        self.notes.child.setPlaceholderText(placeholder)
        self.notes.child.textChanged.connect(self.enableSubmit)

        self.solved_problem = NamedCombobox("Problem solved (Optional)")

        self.problem = NamedLineEdit("Problem you're facing (Optional)")

        self.submit = QPushButton("Submit")
        self.submit.setIcon(QIcon(ADDCOMMENT_ICON))
        self.submit.setMinimumWidth(60)
        self.submit.setDisabled(True)

        layout.addWidget(self.topics)
        layout.addWidget(self.notes)
        layout.addWidget(self.solved_problem)
        layout.addWidget(self.problem)
        layout.addWidget(self.submit, alignment=Qt.AlignmentFlag.AlignLeft)

        # set geometry after widgets have been drawn
        # screen sizes
        xw, xh = self.screen().size().width(), self.screen().size().height()
        # widget sizes
        ww, wh = self.width(), self.height()
        x, y = xw - ww, xh - wh

        self.instart_geometry = QRect(
            x + 100,
            xh,
            self.width() - 100,
            self.height() - 300,
        )
        self.inend_geometry = QRect(x - 10, y - 80, ww, wh)

        self.setGeometry(self.inend_geometry)  # y - window titlebar
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, False)

    def enableSubmit(self, txt=None):
        """enable/disable submit button"""
        topic, notes = (
            self.topics.child.currentText(),
            self.notes.child.toPlainText(),
        )
        if all((topic, notes)):
            self.submit.setEnabled(True)
        else:
            self.submit.setDisabled(True)

    def setTopicText(self, title: str):
        """update topic title"""
        self.topics.child.setCurrentText(title)

    def setProblems(self, problems):
        """set problem titles"""
        self.solved_problem.child.clear()
        self.solved_problem.child.addItems(p.problem for p in problems)
        self.solved_problem.child.addItem(SOLVED_PLACEHOLDER)
        self.solved_problem.child.setCurrentText(SOLVED_PLACEHOLDER)

    def clear(self):
        """clear/reset fields"""
        self.notes.child.clear()
        self.problem.child.clear()
        # set the solved problem to placeholder
        self.solved_problem.child.setCurrentText(SOLVED_PLACEHOLDER)

    def slide_in(self):
        self.animation.setStartValue(self.instart_geometry)
        self.animation.setEndValue(self.inend_geometry)
        self.animation.start()

    def slide_out(self):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.instart_geometry)
        self.animation.start()

    def hide(self):
        self.slide_out()
        self.animation.finished.connect(self._hide_screen)

    def showNormal(self):
        self.slide_in()
        super().showNormal()

    def show(self):
        self.slide_in()
        super().show()

    def _hide_screen(self):
        super().hide()
        self.animation.finished.disconnect(self._hide_screen)

    def closeEvent(self, event):
        self.hide()
        event.ignore()
