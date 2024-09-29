"""custom PyQt6 QStyledItemDelegate classes"""

from PyQt6.QtWidgets import (
    QStyledItemDelegate,
    QPlainTextEdit,
    QComboBox,
    QTimeEdit,
    QSpinBox,
    QDateTimeEdit,
)
from PyQt6.QtCore import Qt, QRect, QModelIndex, QTime, QDateTime
from PyQt6.QtGui import QPainter


class CommentsDelegate(QStyledItemDelegate):
    """
    delegate for the comments table,
    uses: QPlainTextEdit and QDateTimeEdit for editing large texts and datetimes
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # variables
        self.datetime_col = 1
        self.topic_col = 2
        self.comment_col = 3
        # topics
        self._topics = []

    def setTopics(self, topics: list):
        """update topics list"""
        self._topics = topics

    def topicID(self, title: str):
        """get topic id from title"""
        for tpc in self._topics:
            if tpc.title == title:
                return tpc.topic_id

    def topicTitle(self, topic_id: int):
        """get topic title from id"""
        for tpc in self._topics:
            if tpc.topic_id == topic_id:
                return tpc.title

    def paint(self, painter: QPainter, option, index: QModelIndex):
        # use topic id to get title for display
        if index.column() == self.topic_col:
            topic_id = index.data(Qt.ItemDataRole.DisplayRole)
            title = self.topicTitle(topic_id)
            # paint background
            painter.fillRect(option.rect, option.backgroundBrush)
            # set the text color
            painter.setPen(option.palette.text().color())

            # draw text with proper alignment
            painter.drawText(
                option.rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                title,
            )

        else:
            super().paint(painter, option, index)

    def createEditor(self, parent, option, index: QModelIndex):
        column = index.column()
        if column == self.datetime_col:
            # Use QDateTimeEdit
            editor = QDateTimeEdit(parent)
            editor.setDisplayFormat("yyyy-MM-dd HH:mm:ss")  # set time format

        elif column == self.comment_col:
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
        if column == self.datetime_col:
            # set data for QTimeEdit
            datetime_str = index.data(Qt.ItemDataRole.EditRole)
            qdt = QDateTime.fromString(datetime_str, "yyyy-MM-dd HH:mm:ss")
            editor.setDateTime(qdt)

        elif column == self.comment_col:
            # set data for QPlainTextEdit
            text = index.data(Qt.ItemDataRole.EditRole)
            editor.setPlainText(text)

        elif column == self.topic_col:
            topic_id = index.data(Qt.ItemDataRole.EditRole)
            if title := self.topicTitle(topic_id):
                editor.setCurrentText(title)

        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index: QModelIndex):
        column = index.column()
        if column == self.datetime_col:
            # save data from QTimeEdit
            qdatetime = editor.dateTime()
            datetime_str = qdatetime.toString("yyyy-MM-dd HH:mm:ss")
            model.setData(index, datetime_str, Qt.ItemDataRole.EditRole)

        elif column == self.comment_col:
            # save data from QPlainTextEdit
            text = editor.toPlainText()
            model.setData(index, text, Qt.ItemDataRole.EditRole)

        elif column == self.topic_col:
            tpc_title = editor.currentText()
            tpc_id = self.topicID(tpc_title)
            model.setData(index, tpc_id, Qt.ItemDataRole.EditRole)

        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index: QModelIndex):
        column = index.column()

        if column == self.datetime_col:
            rect = QRect(
                option.rect.left(),
                option.rect.top(),
                option.rect.width() + 15,
                option.rect.height(),
            )
            editor.setGeometry(rect)

        elif column == self.comment_col:
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
        self.time_col = 3
        self.int_col = 4

    def createEditor(self, parent, option, index: QModelIndex):
        column = index.column()
        if column == self.time_col:
            # use QTimeEdit
            editor = QTimeEdit(parent)
            editor.setDisplayFormat("HH:mm:ss")  # set time format

        elif column == self.int_col:
            # use QSpinBox
            editor = QSpinBox(parent)
            editor.setRange(1, 1440)
            editor.setSuffix(" mins")

        else:
            # default to base class implementation for other columns
            editor = super().createEditor(parent, option, index)

        return editor

    def setEditorData(self, editor, index: QModelIndex):
        column = index.column()
        if column == self.time_col:
            # set data for QTimeEdit
            time_str = index.data(Qt.ItemDataRole.EditRole)
            time = QTime.fromString(time_str, "HH:mm:ss")
            editor.setTime(time)

        elif column == self.int_col:
            # set data for QSpinBox
            span_int = index.data(Qt.ItemDataRole.EditRole)
            editor.setValue(span_int)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index: QModelIndex):
        column = index.column()
        if column == self.time_col:
            # Save data from QTimeEdit
            time = editor.time()
            time_str = time.toString("HH:mm:ss")
            model.setData(index, time_str, Qt.ItemDataRole.EditRole)

        elif column == self.int_col:
            # Save data from QSpinBox
            span_int = editor.value()
            model.setData(index, span_int, Qt.ItemDataRole.EditRole)
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index: QModelIndex):
        editor.setGeometry(option.rect)
