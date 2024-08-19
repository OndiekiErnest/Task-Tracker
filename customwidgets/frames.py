"""custom PyQt6 QFrame classes"""

from PyQt6.QtWidgets import QFrame


class Line(QFrame):
    """graphical line"""

    def __init__(self, *args, horizontal=True, **kwargs):
        super().__init__(*args, **kwargs)
        if horizontal:
            # defaults to horizontal line
            self.setFrameShape(QFrame.Shape.HLine)
        else:
            self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
