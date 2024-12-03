"""searchable table for the problems model"""

import logging
from PyQt6.QtWidgets import QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from customwidgets.checkboxes import ProblemCheckBox
from constants import ADD_ICON
from .base import SearchableTable

logger = logging.getLogger(__name__)


class ProblemsTableview(SearchableTable):
    """problems table viewer"""

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def _create_btns(self):
        """create top horizontal buttons"""

        self._default_btns()
        self.del_btn.clicked.connect(self._on_delete)

        self.new_problem = QPushButton()
        self.new_problem.setIcon(QIcon(ADD_ICON))

        self.solvedproblem = ProblemCheckBox()
        self.solvedproblem.setToolTip("Mark as Solved/Unsloved")
        self.solvedproblem.clicked.connect(self.toggleSolved)
        self.solvedproblem.setDisabled(True)

        # add extended btns
        self.btnslayout.addWidget(self.solvedproblem)
        self.btnslayout.addWidget(
            self.new_problem,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )
        # default btns/widgets
        self.btnslayout.addWidget(self.more_btn)
        self.btnslayout.addWidget(self.del_btn)
        self.btnslayout.addStretch()
        self.btnslayout.addWidget(self.search, alignment=Qt.AlignmentFlag.AlignRight)

    def _on_selection_changed(self):
        """override the parent method"""
        if selected := self.sRows():
            self.solvedproblem.setEnabled(True)
            if self.del_btn.isHidden():
                self.del_btn.show()
            self.setCheckState(selected)

        else:
            self.solvedproblem.setDisabled(True)
            self.del_btn.hide()

    def setCheckState(self, selected):
        """check or uncheck problem based on database data"""
        states = (idx.model().record(idx.row()).value("solved") for idx in selected)

        enabled = all(states)

        self.solvedproblem.setChecked(enabled)

    def toggleSolved(self):
        """toggle solved status"""
        if selected := self.sRows():
            checked = self.solvedproblem.isChecked()

            if smodel := self.table_view.model():
                model = smodel.sourceModel()
                for index in selected:
                    col = model.fieldIndex("solved")
                    row = index.row()

                    if model.setData(model.index(row, col), int(checked)):
                        if model.submitAll():
                            logger.info(f"Problem was solved: {checked}")
                        else:
                            logger.error(
                                f"Problem error: submitAll: {model.lastError().text()}"
                            )
                    else:
                        logger.error(
                            f"Problem error: setData: {model.lastError().text()}"
                        )

                model.select()

    def _on_delete(self):
        """delete selected rows"""
        if selected := self.sRows():

            len_s = len(selected)

            if (
                QMessageBox.question(
                    self,
                    "Confirm Delete",
                    f"Are you sure you want to delete ({len_s}) selected rows?",
                )
                == QMessageBox.StandardButton.Yes
            ):

                if smodel := self.table_view.model():

                    self.solvedproblem.setDisabled(True)
                    self.del_btn.hide()
                    model = smodel.sourceModel()

                    for index in selected:
                        row = index.row()
                        model.deleteRowFromTable(row)
                        logger.info(f"Deleted problem at row {row}")

                    if model.select():
                        logger.info(
                            "Delete changes in problems table have been submitted"
                        )
