"""custom QTableView classes"""

from PyQt6.QtWidgets import QTableView


class CommentsTable(QTableView):
    """table to display comment records"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(700)

        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)

        self.col_width_percentages = (0.16, 0.3, 0.54)  # percentages for each column

    def set_column_widths(self):
        table_width = self.viewport().width()
        for index, percentage in enumerate(self.col_width_percentages, start=1):
            # apply % width
            self.setColumnWidth(index, int(table_width * percentage))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # set cols size on every resize
        self.set_column_widths()


class TopicsTable(QTableView):
    """table to display topics"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumHeight(350)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setWordWrap(True)

        self.col_width_percentages = (0.5, 0.25, 0.25)  # percentages for each column

    def set_column_widths(self):
        table_width = self.viewport().width()
        for index, percentage in enumerate(self.col_width_percentages, start=2):
            # apply % width
            self.setColumnWidth(index, int(table_width * percentage))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # set cols size on every resize
        self.set_column_widths()
