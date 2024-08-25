"""custom PyQt6 QStyledItemDelegate classes"""

from PyQt6.QtWidgets import (
    QStyledItemDelegate,
    QPlainTextEdit,
    QTimeEdit,
    QSpinBox,
    QDateTimeEdit,
)
from PyQt6.QtSql import QSqlRelationalDelegate
from PyQt6.QtCore import Qt, QRect, QModelIndex, QTime, QDateTime


class CommentsDelegate(QSqlRelationalDelegate):
    """
    delegate for the comments table,
    uses: QPlainTextEdit and QDateTimeEdit for editing large texts and datetimes
    """

    def __init__(self, datetime_col: int, comment_col: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # variables
        self.datetime_col = datetime_col
        self.comment_col = comment_col

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

        else:
            # default to base class implementation for other columns
            editor = super().createEditor(parent, option, index)

        return editor

    def setEditorData(self, editor, index: QModelIndex):
        column = index.column()
        if column == self.datetime_col:
            # set data for QTimeEdit
            datetime_str = index.model().data(index, Qt.ItemDataRole.EditRole)
            qdt = QDateTime.fromString(datetime_str, "yyyy-MM-dd HH:mm:ss")
            editor.setDateTime(qdt)

        elif column == self.comment_col:
            # set data for QPlainTextEdit
            text = index.model().data(index, Qt.ItemDataRole.EditRole)
            editor.setPlainText(text)
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
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index: QModelIndex):
        column = index.column()

        if column == self.comment_col:
            rect = QRect(
                option.rect.left(),
                option.rect.top(),
                max(200, option.rect.width()),
                400,
            )
            editor.setGeometry(rect)
        else:
            editor.setGeometry(option.rect)


class TopicsDelegate(QStyledItemDelegate):
    """
    delegate for the topics table,
    uses: QTimeEdit and QSpinBox for editing time and integers
    """

    def __init__(self, time_col: int, int_col: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # variables
        self.time_col = time_col
        self.int_col = int_col

    def createEditor(self, parent, option, index: QModelIndex):
        column = index.column()
        if column == self.time_col:
            print("Creating QTimeEdit widget")
            # Use QTimeEdit
            editor = QTimeEdit(parent)
            editor.setDisplayFormat("HH:mm:ss")  # set time format

        elif column == self.int_col:
            # Use QSpinBox
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
            time_str = index.model().data(index, Qt.ItemDataRole.EditRole)
            time = QTime.fromString(time_str, "HH:mm:ss")
            editor.setTime(time)

        elif column == self.int_col:
            # set data for QSpinBox
            span_int = index.model().data(index, Qt.ItemDataRole.EditRole)
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
