"""custom PyQt6 widgets"""

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QGroupBox,
    QCheckBox,
    QVBoxLayout,
    QComboBox,
    QSpinBox,
    QTimeEdit,
    QPlainTextEdit,
    QDateTimeEdit,
    QTableView,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QDataWidgetMapper,
    QSizePolicy,
    QSplitter,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from models import CommentsModel
from constants import TIME_UNITS


class Line(QFrame):
    """graphical line"""

    def __init__(self, *args, horizontal=True, **kwargs):
        super().__init__(*args, **kwargs)
        if horizontal:
            # defaults to horizontal line
            self.setFrameShape(QFrame.Shape.HLine)
        else:
            self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class NamedItem(QGroupBox):
    """base named widget; shouldn't be instantiated"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainlayout = QVBoxLayout(self)

        self.mainlayout.addWidget(self.child)


class NamedLineEdit(NamedItem):
    """QLineEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QLineEdit()

        super().__init__(*args, **kwargs)


class NamedCombobox(NamedItem):
    """QComboBox in a QGroupBox"""

    def __init__(self, *args, **kwargs):

        self.child = QComboBox()

        super().__init__(*args, **kwargs)

    def addItems(self, items):
        self.child.clear()
        self.child.addItems(items)

    def setCurrentTopic(self, title):
        self.child.setCurrentText(title)


class NamedSpinbox(NamedItem):
    """QSpinBox in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QSpinBox()
        # read only
        self.child.setDisabled(True)

        super().__init__(*args, **kwargs)


class NamedDatetimeEdit(NamedItem):
    """QDateTimeEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QDateTimeEdit()
        # for consistency, match the format used in the database
        self.child.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.child.setCalendarPopup(True)

        super().__init__(*args, **kwargs)


class NamedTimeEdit(NamedItem):
    """QTimeEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QTimeEdit()
        # for consistency, match the format used in the database
        self.child.setDisplayFormat("HH:mm")

        super().__init__(*args, **kwargs)


class NamedPlainTextEdit(NamedItem):
    """QPlainTextEdit in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QPlainTextEdit()

        super().__init__(*args, **kwargs)


class NamedCheckbox(NamedItem):
    """QCheckBox in a QGroupBox widget"""

    def __init__(self, *args, **kwargs):

        self.child = QCheckBox()

        super().__init__(*args, **kwargs)


class NamedLineEditV(NamedLineEdit):
    """named QLineEdit with an int validator"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        validator = QRegularExpressionValidator(self)
        validator.setRegularExpression(QRegularExpression("[0-9]+"))
        self.child.setValidator(validator)


class TimeUnits(QComboBox):
    """drop down to choose btwn hr, mins, secs"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.addItems(TIME_UNITS.keys())


class RecordsTable(QTableView):
    """table to display records"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(600)

        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        # resize all columns to fit their contents
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.setSortingEnabled(True)


class RecordsEditor(QWidget):
    """database row editor widgets"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMaximumWidth(800)

        layout = QVBoxLayout(self)

        buttonslayout = QHBoxLayout()

        self.id_edit = NamedSpinbox("Comment ID")

        # create mapping widgets
        self.datetime_edit = NamedDatetimeEdit("Date Added")

        self.topic_edit = NamedPlainTextEdit("Topic Title")

        self.comment_edit = NamedPlainTextEdit("Comments")

        layout.addWidget(self.id_edit)
        layout.addWidget(self.datetime_edit)
        layout.addWidget(self.topic_edit)
        layout.addWidget(self.comment_edit)

        # buttons
        self.delete_btn = QPushButton("Delete")
        self.prev_btn = QPushButton("<<")
        self.save_btn = QPushButton("Update")
        self.next_btn = QPushButton(">>")
        self.cancel_btn = QPushButton("Cancel")

        buttonslayout.addWidget(self.delete_btn)
        buttonslayout.addWidget(self.prev_btn)
        buttonslayout.addWidget(self.save_btn)
        buttonslayout.addWidget(self.next_btn)
        buttonslayout.addWidget(self.cancel_btn)
        # add buttons at the bottom
        layout.addLayout(buttonslayout)


class DatabaseMapper(QDataWidgetMapper):
    """widget for editing database records"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSubmitPolicy(QDataWidgetMapper.SubmitPolicy.ManualSubmit)

    def setModel(self, model: CommentsModel):
        """set database model"""
        super().setModel(model)


class Splitter(QSplitter):
    """widgets splitter widget"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sizepolicy = QSizePolicy()
        sizepolicy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sizepolicy.setVerticalPolicy(QSizePolicy.Policy.Expanding)

        self.setSizePolicy(sizepolicy)
        self.setChildrenCollapsible(False)


class InputPopup(QWidget):
    """form widget"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("TLog - Log Activity")

        layout = QVBoxLayout(self)

        # what are you doing right now; What are you up to?
        self.prompt = QLabel("<b>What are you up to?</b>")
        self.prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.prompt)

        # form widgets
        self.topic = NamedCombobox("Current Topic")
        self.topic.child.setDisabled(True)
        self.topic.child.currentTextChanged.connect(self.enableSubmit)

        self.comments = NamedPlainTextEdit("Describe the activity/what you have learnt")
        self.comments.child.textChanged.connect(self.enableSubmit)

        self.submit = QPushButton("Add Log")
        self.submit.setDisabled(True)

        layout.addWidget(self.topic)
        layout.addWidget(self.comments)
        layout.addWidget(self.submit, alignment=Qt.AlignmentFlag.AlignLeft)

        # set geometry after widgets have been drawn
        # screen sizes
        xw, xh = self.screen().size().width(), self.screen().size().height()
        # widget sizes
        ww, wh = self.width(), self.height()
        x, y = xw - ww, xh - wh

        self.setGeometry(x - 10, y - 40, ww, wh)  # y - window titlebar
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, False)

    def enableSubmit(self, txt=None):
        """enable/disable submit button"""
        topic, comments = self.topic.child.text(), self.comments.child.toPlainText()
        if all((topic, comments)):
            self.submit.setEnabled(True)
        else:
            self.submit.setDisabled(True)

    def setTopicText(self, title):
        """update topic title"""
        self.topic.child.setText(title)

    def closeEvent(self, event):
        self.hide()
        event.ignore()


class DisableNotifs(QGroupBox):
    """group of checkboxes for disabling notifications"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mainlayout = QHBoxLayout(self)
        # widgets
        self.disable_all = QCheckBox("Until restart")
        self.disable_saturday = QCheckBox("On Saturdays")
        self.disable_sunday = QCheckBox("On Sundays")

        mainlayout.addWidget(self.disable_all)
        mainlayout.addWidget(self.disable_saturday)
        mainlayout.addWidget(self.disable_sunday)
