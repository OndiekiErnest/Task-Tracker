"""custom PyQt6 QStyledItemDelegate classes"""

import logging
from PyQt6.QtWidgets import (
    QStyledItemDelegate,
    QPlainTextEdit,
    QComboBox,
    QTimeEdit,
)
from PyQt6.QtCore import Qt, QRect, QModelIndex, QTime


logger = logging.getLogger(__name__)


class NotesDelegate(QStyledItemDelegate):
    """
    delegate for the notes table,
    uses: QPlainTextEdit and QDateTimeEdit for editing large texts and datetimes
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # variables
        self.topic_col = 2
        self.note_col = 3
        # topics
        self._topics = []

    def setTopics(self, topics: list):
        """update topics list"""
        self._topics = topics
        logger.info(f"Notes topics updated")

    def topicID(self, title: str):
        """get topic id from title"""
        for tpc in self._topics:
            if tpc.title == title:
                logger.info(f"Found topic ID for {title!r}")
                return tpc.topic_id

        logger.info(f"Not Found: topic ID for {title!r}")

    def topicTitle(self, topic_id: int):
        """get topic title from id"""
        for tpc in self._topics:
            if tpc.topic_id == topic_id:
                logger.info(f"Found topic title of ID {topic_id}")
                return tpc.title

        logger.info(f"Not Found: topic title of ID {topic_id}")

    # def paint(self, painter: QPainter, option, index: QModelIndex):
    #     # use topic id to get title for display
    #     if index.column() == self.topic_col:
    #         topic_id = index.data(Qt.ItemDataRole.DisplayRole)
    #         title = self.topicTitle(topic_id)
    #         # paint background
    #         painter.fillRect(option.rect, option.backgroundBrush)
    #         # set the text color
    #         painter.setPen(option.palette.text().color())

    #         # draw text with proper alignment
    #         painter.drawText(
    #             option.rect,
    #             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
    #             title,
    #         )

    #     else:
    #         super().paint(painter, option, index)

    def createEditor(self, parent, option, index: QModelIndex):
        column = index.column()

        if column == self.note_col:
            # Use QPlainTextEdit
            editor = QPlainTextEdit(parent)
            editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            editor.setTabChangesFocus(True)

        elif column == self.topic_col:
            editor = QComboBox(parent)
            editor.addItems(t.title for t in self._topics)

        else:
            # default to base class implementation for other columns
            editor = super().createEditor(parent, option, index)

        return editor

    def setEditorData(self, editor, index: QModelIndex):
        column = index.column()
        value = index.data(Qt.ItemDataRole.EditRole)

        if column == self.note_col:
            # set data for QPlainTextEdit
            editor.setPlainText(value)

        elif column == self.topic_col:
            try:
                editor.setCurrentText(value)
            except TypeError:
                # raised if an int is being set
                pass

        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index: QModelIndex):
        column = index.column()

        if column == self.note_col:
            # save data from QPlainTextEdit
            text = editor.toPlainText()
            model.setData(index, text, Qt.ItemDataRole.EditRole)
            logger.info(f"Notes updated to: {text!r}")

        elif column == self.topic_col:
            tpc_title = editor.currentText()
            tpc_id = self.topicID(tpc_title)
            model.setData(index, tpc_id, Qt.ItemDataRole.EditRole)
            logger.info(f"Notes topic updated to: {tpc_title!r}")

        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index: QModelIndex):
        column = index.column()

        if column == self.note_col:
            rect = QRect(
                option.rect.left(),
                option.rect.top(),
                max(200, option.rect.width()),
                300,
            )
            editor.setGeometry(rect)
        else:
            editor.setGeometry(option.rect)


class TopicsDelegate(QStyledItemDelegate):
    """
    delegate for the topics table,
    uses: QTimeEdit and QSpinBox for editing time and integers
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # variables
        self.starts_col = 3
        self.ends_col = 4

    def createEditor(self, parent, option, index: QModelIndex):
        column = index.column()
        if column == self.starts_col:
            # use QTimeEdit
            editor = QTimeEdit(parent)
            editor.setDisplayFormat("HH:mm:ss")  # set time format

        elif column == self.ends_col:
            # use QSpinBox
            editor = QTimeEdit(parent)
            editor.setDisplayFormat("HH:mm:ss")  # set time format

        else:
            # default to base class implementation for other columns
            editor = super().createEditor(parent, option, index)

        return editor

    def setEditorData(self, editor, index: QModelIndex):
        column = index.column()
        if column == self.starts_col:
            # set data for QTimeEdit
            starts_str = index.data(Qt.ItemDataRole.EditRole)
            time = QTime.fromString(starts_str, "HH:mm:ss")
            editor.setTime(time)

        elif column == self.ends_col:
            # set data for QSpinBox
            ends_str = index.data(Qt.ItemDataRole.EditRole)
            time = QTime.fromString(ends_str, "HH:mm:ss")
            editor.setTime(time)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index: QModelIndex):
        column = index.column()
        if column == self.starts_col:
            # save data from QTimeEdit
            starts = editor.time()
            starts_str = starts.toString("HH:mm:ss")
            model.setData(index, starts_str, Qt.ItemDataRole.EditRole)
            logger.info(f"Topic start time changed to: {starts_str!r}")

        elif column == self.ends_col:
            # save data from QTimeEdit
            ends = editor.time()
            ends_str = ends.toString("HH:mm:ss")
            model.setData(index, ends_str, Qt.ItemDataRole.EditRole)
            logger.info(f"Topic ends changed to: {ends_str}")

        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index: QModelIndex):
        editor.setGeometry(option.rect)


class ProblemsDelegate(QStyledItemDelegate):
    """
    delegate for the problems table,
    uses: QComboBox for editing topics
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # variables
        self.topics_col = 3
        # topics
        self._topics = []

    def setTopics(self, topics: list):
        """update topics list"""
        self._topics = topics
        logger.info(f"Problems topics updated")

    def topicID(self, title: str):
        """get topic id from title"""
        for tpc in self._topics:
            if tpc.title == title:
                logger.info(f"Found topic ID for {title!r}")
                return tpc.topic_id

        logger.info(f"Not Found: topic ID for {title!r}")

    def createEditor(self, parent, option, index: QModelIndex):
        column = index.column()
        if column == self.topics_col:
            editor = QComboBox(parent)
            editor.addItems(t.title for t in self._topics)

        else:
            # default to base class implementation for other columns
            editor = super().createEditor(parent, option, index)

        return editor

    def setEditorData(self, editor, index: QModelIndex):
        column = index.column()
        value = index.data(Qt.ItemDataRole.EditRole)

        if column == self.topics_col:
            try:
                editor.setCurrentText(value)
            except TypeError:
                # raised if an int is being set
                pass
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index: QModelIndex):
        column = index.column()
        if column == self.topics_col:
            tpc_title = editor.currentText()
            tpc_id = self.topicID(tpc_title)
            model.setData(index, tpc_id, Qt.ItemDataRole.EditRole)
            logger.info(f"Problems topic updated to: {tpc_title!r}")
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index: QModelIndex):
        editor.setGeometry(option.rect)
