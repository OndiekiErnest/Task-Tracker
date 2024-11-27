"""searchable table for the topics model"""

import logging
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from customwidgets.checkboxes import NotificationCheckBox
from constants import ADD_ICON
from .base import SearchableTable

logger = logging.getLogger(__name__)


class TopicsTableview(SearchableTable):
    """topics table viewer"""

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def _create_btns(self):
        """create top horizontal buttons"""

        # create delete and more btns
        self._default_btns()

        self.new_topic = QPushButton()
        self.new_topic.setIcon(QIcon(ADD_ICON))

        self.enabledtopic = NotificationCheckBox()
        self.enabledtopic.setToolTip("Toggle Notifications for all selected rows")
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

    def disableDnCheck(self):
        """disable btns"""
        self.enabledtopic.setDisabled(True)
        self.del_btn.hide()

    def setCheckState(self, selected):
        """check or uncheck topic based on database data"""
        states = (idx.model().record(idx.row()).value("enabled") for idx in selected)

        enabled = all(states)  # True if all states are 1

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
