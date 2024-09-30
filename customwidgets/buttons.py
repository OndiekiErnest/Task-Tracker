"""custom PyQt6 buttons"""

from PyQt6.QtCore import QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtWidgets import QPushButton


class InOutButton(QPushButton):
    """button that slides into view and when hiding"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize the animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)  # duration of the slide animation

    def show(self):
        super().show()
        self.slide_in()

    def slide_in(self):
        self.animation.setStartValue(
            QRect(
                self.geometry().right() + 20,
                self.geometry().top(),
                self.width(),
                self.height(),
            )
        )
        self.animation.setEndValue(
            QRect(
                self.geometry().left(),
                self.geometry().top(),
                self.width(),
                self.height(),
            )
        )
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def slide_out(self):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(
            QRect(-100, self.geometry().top(), self.width(), self.height())
        )
        self.animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.animation.start()
