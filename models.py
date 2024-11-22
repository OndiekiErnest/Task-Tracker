"""PyQt6 models"""

import logging
from datetime import datetime
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtSql import (
    QSqlQuery,
    QSqlRelation,
    QSqlTableModel,
    QSqlRelationalTableModel,
)
from datastructures.datas import ProblemData, TopicData
from constants import TIMEZONE


logger = logging.getLogger(__name__)

COMMENTS_HEADERS = {
    "timestamp": "Date Added",
    "topic_id": "Topic Title",
    "comment": "Comments",
}

TOPICS_HEADERS = {
    "topic": "Topic Title",
    "start": "Topic Start (daily)",
    "span": "Span (in minutes)",
}

PROBLEMS_HEADERS = {
    "timestamp": "Date Added",
    "problem": "Problem",
    "solved": "Solved",
}


class TopicsModel(QSqlTableModel):
    """table model class that reads and writes topics to a local file database"""

    def __init__(self, db, **kwargs):

        # create table if non-existent
        self._query = QSqlQuery(db=db)
        # start is time in the format HH:MM
        # span is number in seconds
        # enabled is number; enabled=1, disabled=0
        created = self._query.exec(
            """
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                topic TEXT NOT NULL UNIQUE,
                start TEXT NOT NULL,
                span INTEGER NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        super().__init__(db=db, **kwargs)
        if created:
            # set table name
            self.setTable("topics")
            logger.info("Table created and set to 'topics'")
        else:
            logger.error(
                f"Table 'topics' was not created:\n{self._query.lastError().driverText()}"
            )
        # change header titles
        for k, v in TOPICS_HEADERS.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Orientation.Horizontal, v)
        # edit strategy
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        # sort before select
        self.setSort(self.fieldIndex("start"), Qt.SortOrder.AscendingOrder)
        # select
        self.select()

    def getTopics(self):
        """prepare topics, and their details"""
        # get the number of rows
        row_count = self.rowCount()

        # create a list to store rows as tuples
        topics_list: list[TopicData] = []
        # iterate over each row and column to collect data
        for row in range(row_count):
            # get the QSqlRecord for the row
            record = self.record(row)
            topic_kw = {}
            # extract row data
            for c in range(record.count()):
                value = record.value(c)
                match c:
                    case 0:
                        topic_kw["topic_id"] = value
                    case 1:
                        topic_kw["created"] = datetime.strptime(
                            value, "%Y-%m-%d %H:%M:%S"
                        )
                    case 2:
                        # title
                        topic_kw["title"] = value
                    case 3:
                        dt = datetime.now(tz=TIMEZONE)
                        hr, mins, secs = value.split(":")
                        topic_kw["starts"] = dt.replace(
                            hour=int(hr),
                            minute=int(mins),
                            second=int(secs),
                        )
                    case 4:
                        topic_kw["span"] = int(value)
                    case 5:
                        topic_kw["enabled"] = bool(value)
                    case _:
                        pass

            topics_list.append(TopicData(**topic_kw))
        # sort based on the starts
        topics_list.sort(key=lambda t: t.starts)
        return topics_list

    def newTopic(self, time_now: str, topic: str, start: str, span: int):
        """add new topic to table"""
        self._query.prepare(
            """
            INSERT INTO topics (timestamp, topic, start, span)
            VALUES (?, ?, ?, ?)
            """
        )
        self._query.addBindValue(time_now)
        self._query.addBindValue(topic)
        self._query.addBindValue(start)
        self._query.addBindValue(span)

        if self._query.exec():
            self.select()
            logger.info(f"Set topic '{topic}'")
            return True
        else:
            logger.error(
                f"DB error setting topic: {self._query.lastError().driverText()}"
            )
            return False


class CommentsModel(QSqlRelationalTableModel):
    """table model class that reads and writes comments to a local file database"""

    def __init__(self, db, **kwargs):

        # create table if non-existent
        self._query = QSqlQuery(db=db)
        # returns True if success
        created = self._query.exec(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                topic_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
            )
            """
        )

        super().__init__(db=db, **kwargs)
        if created:
            # set table name
            self.setTable("comments")
            logger.info("Table created and set to 'comments'")
        else:
            logger.error(
                f"Table 'comments' was not created:\n{self._query.lastError().driverText()}"
            )

        # set relation
        self.setRelation(
            self.fieldIndex("topic_id"),
            QSqlRelation("topics", "id", "topic"),
        )

        # change header titles
        for k, v in COMMENTS_HEADERS.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Orientation.Horizontal, v)

        # edit strategy
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)

        # sort before select
        self.setSort(self.fieldIndex("timestamp"), Qt.SortOrder.DescendingOrder)
        # select
        self.select()

    def newNote(self, time_now: str, topic_id: int, notes: str):
        """ "add new notes to table"""
        self._query.prepare(
            """
            INSERT INTO comments (timestamp, topic_id, comment)
            VALUES (?, ?, ?)
            """
        )
        self._query.addBindValue(time_now)
        self._query.addBindValue(topic_id)
        self._query.addBindValue(notes)

        if self._query.exec():
            self.select()
            logger.info(f"Added comment related to topic at'{topic_id}'")
            return True
        else:
            logger.error(
                f"DB error adding comments: {self._query.lastError().driverText()}"
            )
            return False


class ProblemsModel(QSqlTableModel):
    """table model class that reads and writes problems to a local file database"""

    def __init__(self, db, **kwargs):

        # create table if non-existent
        self._query = QSqlQuery(db=db)
        # solved is number; 0=unsolved, 1=solved
        created = self._query.exec(
            """
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                problem TEXT NOT NULL UNIQUE,
                topic_id INTEGER NOT NULL,
                solved INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(topic_id) REFERENCES topics(id) ON DELETE CASCADE
            )
            """
        )

        super().__init__(db=db, **kwargs)
        if created:
            # set table name
            self.setTable("problems")
            logger.info("Table created and set to 'problems'")
        else:
            logger.error(
                f"Table 'problems' was not created:\n{self._query.lastError().driverText()}"
            )
        # change header titles
        for k, v in PROBLEMS_HEADERS.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Orientation.Horizontal, v)
        # edit strategy
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        # sort before select
        self.setSort(self.fieldIndex("timestamp"), Qt.SortOrder.AscendingOrder)
        # select
        self.select()

    def _idToRow(self, problem_id: int):
        """get row number from problem_id"""

        for row in range(self.rowCount()):
            # get the QSqlRecord for the row
            record = self.record(row)
            # extract row data
            if record.value(0) == problem_id:
                return row

    def getProblems(self):
        """create problems data"""

        # get the number of rows
        row_count = self.rowCount()

        # create a list to store rows as ProblemData instances
        problems_list: list[ProblemData] = []
        # iterate over each row and column to collect data
        for row in range(row_count):
            # get the QSqlRecord for the row
            record = self.record(row)
            problem_kw = {}
            # extract row data
            for c in range(record.count()):
                value = record.value(c)
                match c:
                    case 0:
                        problem_kw["problem_id"] = value
                    case 1:
                        problem_kw["created"] = datetime.strptime(
                            value, "%Y-%m-%d %H:%M:%S"
                        )
                    case 2:
                        problem_kw["problem"] = value
                    case 3:
                        problem_kw["topic_id"] = value
                    case 4:
                        problem_kw["solved"] = bool(value)
                    case _:
                        pass

            problems_list.append(ProblemData(**problem_kw))

        problems_list.sort(key=lambda p: p.created)
        return problems_list

    def newProblem(self, timestamp: str, topic_id: int, problem: str):
        """add new problem to table"""

        # create a new row in the model
        self._query.prepare(
            """
            INSERT INTO problems (timestamp, problem, topic_id)
            VALUES (?, ?, ?)
            """
        )
        self._query.addBindValue(timestamp)
        self._query.addBindValue(problem)
        self._query.addBindValue(topic_id)

        if self._query.exec():
            logger.info("Added new problem to table")
            self.select()
            return True
        else:
            logger.error(
                f"DB error adding problem: {self._query.lastError().driverText()}"
            )
            return False

    def markSolved(self, problem_id: int):
        """mark old problem as solved if exists"""

        self._query.prepare("UPDATE problems SET solved = 1 WHERE id = ?")
        self._query.addBindValue(problem_id)

        if self._query.exec():
            logger.info(f"Problem at '{problem_id}' marked as solved")
            self.select()
            return True
        else:
            logger.error(
                f"DB error marking problem as solved: {self._query.lastError().driverText()}"
            )
            return False


class SearchableModel(QSortFilterProxyModel):
    """model that can filter all columns"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterKeyColumn(-1)

    def sort(self, column, order):
        """use source model's sort"""
        self.sourceModel().sort(column, order)
