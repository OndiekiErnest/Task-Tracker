"""custom QSplitter classes"""

from PyQt6.QtWidgets import QSplitter, QSizePolicy


class Splitter(QSplitter):
    """widgets splitter widget"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sizepolicy = QSizePolicy()
        sizepolicy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sizepolicy.setVerticalPolicy(QSizePolicy.Policy.Expanding)

        self.setSizePolicy(sizepolicy)
        self.setChildrenCollapsible(False)
