"""custom QWidget with widgets for typing and saving user logs"""

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from customwidgets.groupboxes import NamedCombobox, NamedPlainTextEdit
from constants import ADDCOMMENT_ICON


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
        self.topic = NamedCombobox("Current Topic")
        self.topic.child.currentTextChanged.connect(self.enableSubmit)

        self.comments = NamedPlainTextEdit("Describe the activity")
        self.comments.child.setPlaceholderText(placeholder)
        self.comments.child.textChanged.connect(self.enableSubmit)

        self.submit = QPushButton("Add Log")
        self.submit.setIcon(QIcon(ADDCOMMENT_ICON))
        self.submit.setMinimumWidth(60)
        self.submit.setDisabled(True)

        layout.addWidget(self.topic)
        layout.addWidget(self.comments)
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
        topic, comments = (
            self.topic.child.currentText(),
            self.comments.child.toPlainText(),
        )
        if all((topic, comments)):
            self.submit.setEnabled(True)
        else:
            self.submit.setDisabled(True)

    def setTopicText(self, title):
        """update topic title"""
        self.topic.child.setText(title)

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
        super().showNormal()
        self.slide_in()

    def show(self):
        super().show()
        self.slide_in()

    def _hide_screen(self):
        super().hide()
        self.animation.finished.disconnect(self._hide_screen)

    def closeEvent(self, event):
        self.hide()
        event.ignore()
