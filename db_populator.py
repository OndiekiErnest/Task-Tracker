"""populate the database with fake data for testing purposes"""

import random
import sqlite3
from datetime import timedelta
from faker import Faker
from constants import TIMEZONE, APP_DB


fake = Faker()


def generate_topic():
    """create topic record data"""

    # timestamp in the format "%Y-%m-%d %H:%M:%S"
    timestamp = fake.date_time_this_decade(tzinfo=TIMEZONE).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # topic
    topic = fake.unique.sentence(nb_words=3)

    # start and end in the format "HH:MM"
    starts = fake.date_time_this_year()
    ends = starts + timedelta(minutes=20)

    # enabled
    enabled = random.randint(0, 1)

    return (
        timestamp,
        topic,
        starts.strftime("%H:%M:%S"),
        ends.strftime("%H:%M:%S"),
        enabled,
    )


def generate_note():
    """create topic record data"""

    # timestamp in the format "%Y-%m-%d %H:%M:%S"
    timestamp = fake.date_time_this_decade(tzinfo=TIMEZONE).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    note = fake.sentence(nb_words=30)

    return timestamp, note


def generate_problem():
    """create problem record data"""

    # timestamp in the format "%Y-%m-%d %H:%M:%S"
    timestamp = fake.date_time_this_decade(tzinfo=TIMEZONE).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    problem = fake.unique.sentence(nb_words=3)

    return timestamp, problem


def insert_topic(conn: sqlite3.Connection, *args):
    """insert topic to table"""
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO topics (timestamp, topic, starts, ends, enabled) 
        VALUES (?, ?, ?, ?, ?)
        """,
        args,
    )
    conn.commit()

    # return the primary key of the inserted record
    return cursor.lastrowid


def insert_note(conn: sqlite3.Connection, topic_id: int, *args):
    """insert note to table"""
    cursor = conn.cursor()
    timestamp, note = args

    cursor.execute(
        """
        INSERT INTO notes (timestamp, topic_id, note) 
        VALUES (?, ?, ?)
        """,
        (timestamp, topic_id, note),
    )
    conn.commit()


def insert_problem(conn: sqlite3.Connection, topic_id: int, *args):
    """insert problem to table"""
    cursor = conn.cursor()
    timestamp, problem = args

    cursor.execute(
        """
        INSERT INTO problems (timestamp, problem, topic_id) 
        VALUES (?, ?, ?)
        """,
        (timestamp, problem, topic_id),
    )
    conn.commit()


def main():
    conn = sqlite3.connect(APP_DB)

    for _ in range(1000):
        row = generate_topic()
        pk = insert_topic(conn, *row)

        for _ in range(random.randint(1, 10)):
            note = generate_note()
            insert_note(conn, pk, *note)

        for _ in range(random.randint(1, 3)):
            note = generate_problem()
            insert_problem(conn, pk, *note)

    conn.close()


if __name__ == "__main__":
    main()
