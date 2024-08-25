"""custom QTableView classes"""

from PyQt6.QtWidgets import QTableView, QHeaderView


class CommentsTable(QTableView):
    """table to display records"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(600)

        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        # resize all columns to fit their contents
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.setSortingEnabled(True)
