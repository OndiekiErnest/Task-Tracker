"""custom QTableView classes"""

from PyQt6.QtWidgets import QTableView


class Tableview(QTableView):
    """table to display data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # set cols size on every resize
        self.set_column_widths()


class NotesTable(Tableview):
    """table to display note records"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(700)

        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)

        self.col_widths = (0.3, 0.68)  # percentages for each column

    def set_column_widths(self):
        table_width = self.width()
        for index, percentage in enumerate(self.col_widths, start=2):
            # apply % width
            self.setColumnWidth(index, int(table_width * percentage))


class TopicsTable(Tableview):
    """table to display topics"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumHeight(350)
        self.setWordWrap(True)

        self.col_widths = (0.5, 0.25, 0.23)  # percentages for each column

    def set_column_widths(self):
        table_width = self.width()
        for index, percentage in enumerate(self.col_widths, start=2):
            # apply % width
            self.setColumnWidth(index, int(table_width * percentage))


class ProblemsTable(Tableview):
    """table to display problems"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumHeight(350)
        self.setWordWrap(True)

        self.col_widths = (0.5, 0.48)  # percentages for each column

    def set_column_widths(self):
        table_width = self.width()
        for index, percentage in enumerate(self.col_widths, start=2):
            # apply % width
            self.setColumnWidth(index, int(table_width * percentage))
