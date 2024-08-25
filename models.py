"""PyQt6 models"""

import logging
from PyQt6.QtCore import Qt
from PyQt6.QtSql import (
    QSqlRelation,
    QSqlQuery,
    QSqlTableModel,
    QSqlRelationalTableModel,
)


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


class CommentsModel(QSqlRelationalTableModel):
    """table model class that reads and writes comments to a local file database"""

    def __init__(self, db, **kwargs):

        # create table if non-existent
        query = QSqlQuery(db=db)
        # returns True if success
        created = query.exec(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
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
            self.setRelation(
                self.fieldIndex("topic_id"),
                QSqlRelation("topics", "id", "topic"),
            )
            logger.info("Table created and set to 'comments'")
        else:
            logger.error(
                f"Table 'comments' was not created:\n{query.lastError().driverText()}"
            )
        # change header titles
        for k, v in COMMENTS_HEADERS.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Orientation.Horizontal, v)
        # edit strategy
        self.setEditStrategy(QSqlRelationalTableModel.EditStrategy.OnFieldChange)
        # sort before select
        self.setSort(self.fieldIndex("timestamp"), Qt.SortOrder.DescendingOrder)
        # select
        self.select()


class TopicsModel(QSqlTableModel):
    """table model class that reads and writes topics to a local file database"""

    def __init__(self, db, **kwargs):

        # create table if non-existent
        query = QSqlQuery(db=db)
        # returns True if success
        # start is time in the format HH:MM
        # span is number in seconds
        created = query.exec(
            """
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
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
                f"Table 'topics' was not created:\n{query.lastError().driverText()}"
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
