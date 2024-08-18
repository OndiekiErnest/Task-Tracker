"""PyQt6 models"""

import logging
from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlQuery, QSqlTableModel


logger = logging.getLogger(__name__)

COMMENTS_HEADERS = {
    "timestamp": "Date Added",
    "topic": "Topic Title",
    "comment": "Comments",
}

TOPICS_HEADERS = {
    "topic": "Topic Title",
    "start": "Activity Start (daily)",
    "span": "Span (in seconds)",
}


class CommentsModel(QSqlTableModel):
    """table model class that reads and writes comments to a local file database"""

    def __init__(self, db, **kwargs):

        # create table if non-existent
        query = QSqlQuery(db=db)
        # returns True if success
        created = query.exec(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                topic TEXT NOT NULL,
                comment TEXT NOT NULL
            )
            """
        )

        super().__init__(db=db, **kwargs)
        if created:
            # set table name
            self.setTable("comments")
            logger.info("Table set to 'comments'")
        else:
            logger.error(
                f"Table was not set to 'comments':\n{query.lastError().driverText()}"
            )
        # change header titles
        for k, v in COMMENTS_HEADERS.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Orientation.Horizontal, v)
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
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                topic TEXT NOT NULL,
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
            logger.info("Table set to 'topics'")
        else:
            logger.error(
                f"Table was not set to 'topics':\n{query.lastError().driverText()}"
            )
        # change header titles
        for k, v in TOPICS_HEADERS.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Orientation.Horizontal, v)
        # select
        self.select()
