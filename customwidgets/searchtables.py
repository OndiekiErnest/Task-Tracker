"""custom searchable table"""

import os
import logging
from PyQt6.QtWidgets import (
    QGroupBox,
    QPushButton,
    QTableView,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from customwidgets.tableviews import CommentsTable, TopicsTable, ProblemsTable
from customwidgets.checkboxes import NotificationCheckBox, ProblemCheckBox
from customwidgets.lineedits import SearchInput
from customwidgets.buttons import InOutButton
from customwidgets.menus import TableMoreMenu
from utils import open_folder_in_explorer
from models import SearchableModel
from backup import BackupWorker, threadpool_manager
from constants import DELETE_ICON, ADD_ICON, APP_DB, MORE_ICON

logger = logging.getLogger(__name__)


class SearchableTable(QGroupBox):

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        tables = {
            "Notes": CommentsTable,
            "Topics": TopicsTable,
            "Problems": ProblemsTable,
        }

        self.mainlayout = QVBoxLayout(self)

        self.btnslayout = QHBoxLayout()
        self.btnslayout.setContentsMargins(2, 2, 2, 2)

        self.last_known_dir = os.path.expanduser(f"~{os.sep}Documents")

        self.model = SearchableModel()

        self.table_view: QTableView = tables[name]()  # create table instance
        self.table_view.setModel(self.model)

        self.mainlayout.addLayout(self.btnslayout)
        self.mainlayout.addWidget(self.table_view)

        self.more_menu = TableMoreMenu(self)
        self.more_menu.show_file.triggered.connect(self._open_source)
        self.more_menu.backup_file.triggered.connect(self._backup)

        # create btns
        self._create_btns()

    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return getattr(self.table_view, name)
            except AttributeError:
                raise AttributeError(
                    f"SearchableTable has no attributed named {name!r}"
                )

    def _default_btns(self):
        """create default btns/widgets"""

        self.search = SearchInput()
        self.search.textChanged.connect(self.model.setFilterFixedString)

        self.more_btn = QPushButton()
        self.more_btn.setIcon(QIcon(MORE_ICON))
        self.more_btn.setMenu(self.more_menu)

        self.del_btn = InOutButton()
        self.del_btn.setIcon(QIcon(DELETE_ICON))
        self.del_btn.setToolTip("Delete selected rows")
        self.del_btn.hide()

    def _on_selection_changed(self):
        """hide/show del btn"""
        if self.sRows():
            if self.del_btn.isHidden():
                self.del_btn.show()
        else:
            self.del_btn.hide()

    def _open_source(self):
        """open db file in explorer"""
        open_folder_in_explorer(os.path.dirname(APP_DB))
        logger.info("Database file location opened")

    def _backup(self):
        """copy database file to chosen location"""
        backup_dir = os.path.normpath(
            QFileDialog.getExistingDirectory(
                self,
                "Choose Backup Folder",
                self.last_known_dir,
            )
        )
        if backup_dir != ".":
            self.last_known_dir = backup_dir

            worker = BackupWorker(backup_dir)
            worker.signals.done.connect(self._show_info)
            worker.signals.errored.connect(self._show_error)

            threadpool_manager.start(worker)

            logger.info("Database backup initiated")

    def _show_info(self, info: str):
        """show info message box"""
        QMessageBox.information(
            self,
            "Backup Information",
            info,
        )

    def _show_error(self, err: str):
        """show error message box"""
        QMessageBox.warning(
            self,
            "Backup Errored",
            err,
        )

    def sRows(self):
        """return selected rows"""
        return {
            self.model.mapToSource(idx)
            for idx in self.table_view.selectionModel().selectedRows()
        }

    def setModel(self, model):
        """add source model for the proxy"""

        self.model.setSourceModel(model)
        self.table_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )


class CommentsTableview(SearchableTable):
    """comments table viewer"""

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def _create_btns(self):
        """create top horizontal buttons"""

        self._default_btns()

        self.new_topic = QPushButton("Topic")
        self.new_topic.setIcon(QIcon(ADD_ICON))

        self.new_comment = QPushButton("Notes")
        self.new_comment.setIcon(QIcon(ADD_ICON))

        # add extended btns
        self.btnslayout.addWidget(self.new_topic, alignment=Qt.AlignmentFlag.AlignLeft)
        self.btnslayout.addWidget(self.new_comment)
        # default btns/widgets
        self.btnslayout.addWidget(self.more_btn)
        self.btnslayout.addWidget(self.del_btn)
        self.btnslayout.addStretch()
        self.btnslayout.addWidget(self.search, alignment=Qt.AlignmentFlag.AlignRight)


class TopicsTableview(SearchableTable):
    """topics table viewer"""

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def _create_btns(self):
        """create top horizontal buttons"""

        self._default_btns()

        self.new_topic = QPushButton()
        self.new_topic.setIcon(QIcon(ADD_ICON))

        self.enabledtopic = NotificationCheckBox()
        self.enabledtopic.setToolTip("Toggle for all the selected rows")
        self.enabledtopic.clicked.connect(self.toggleNotifs)
        self.enabledtopic.setDisabled(True)

        # add extended btns
        self.btnslayout.addWidget(
            self.enabledtopic,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )
        self.btnslayout.addWidget(self.new_topic)
        # default btns/widgets
        self.btnslayout.addWidget(self.more_btn)
        self.btnslayout.addWidget(self.del_btn)
        self.btnslayout.addStretch()
        self.btnslayout.addWidget(self.search, alignment=Qt.AlignmentFlag.AlignRight)

    def toggleNotifs(self):
        """disable/enable topic from sending notifications"""
        if selected_rows := self.sRows():

            checked = self.enabledtopic.isChecked()
            if smodel := self.table_view.model():
                model = smodel.sourceModel()

                for index in selected_rows:
                    col = model.fieldIndex("enabled")
                    row = index.row()

                    if model.setData(model.index(row, col), int(checked)):
                        if model.submitAll():
                            logger.info(f"Topic was enabled: {checked}")
                        else:
                            logger.error(
                                f"Topic error: submitAll: {model.lastError().text()}"
                            )
                    else:
                        logger.error(
                            f"Topic error: setData: {model.lastError().text()}"
                        )
                # model.select()

    def disableDnCheck(self):
        """disable btns"""
        self.enabledtopic.setDisabled(True)
        self.del_btn.hide()

    def setCheckState(self, selected):
        """check or uncheck topic based on database data"""
        states = (idx.model().record(idx.row()).value("enabled") for idx in selected)

        enabled = all(states)

        self.enabledtopic.setChecked(enabled)

    def _on_selection_changed(self):
        """override the parent method"""
        if selected := self.sRows():
            self.enabledtopic.setEnabled(True)
            if self.del_btn.isHidden():
                self.del_btn.show()
            self.setCheckState(selected)

        else:
            self.disableDnCheck()


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
        self.solvedproblem.setToolTip("Toggle for all the selected rows")
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
