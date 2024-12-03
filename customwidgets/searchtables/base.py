"""searchable table in a QGroupBox with widgets like btns and search area"""

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
from customwidgets.tableviews import NotesTable, TopicsTable, ProblemsTable
from customwidgets.lineedits import SearchInput
from customwidgets.buttons import InOutButton
from customwidgets.menus import TableMoreMenu
from utils import open_folder_in_explorer
from models import SearchableModel
from backup import FileCopyWorker, threadpool_manager
from constants import DELETE_ICON, APP_DB, MORE_ICON

logger = logging.getLogger(__name__)


class SearchableTable(QGroupBox):
    """base searchable table class"""

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        # supported tables
        tables = {
            "Notes": NotesTable,
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
            # access the table view attrs and methods
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

            worker = FileCopyWorker(APP_DB, backup_dir)
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
        """add source model for the proxy model"""

        self.model.setSourceModel(model)
        self.table_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
