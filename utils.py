"""app utility functions"""

import os
import ctypes
import orjson
import logging
from datetime import datetime
from subprocess import run as subrun
from datastructures.datas import TopicData
from constants import TIMEZONE

logger = logging.getLogger(__name__)


def diff_key(now: datetime):
    """return the difference between now and the 'starts' datetime of a topic"""

    def wrapper(topic: TopicData):
        return abs(now - topic.starts)

    return wrapper


def close_topic(topics: list[TopicData]):
    """return the closest topic whose 'starts' datetime is close to now"""
    if not topics:
        return None

    now = datetime.now(tz=TIMEZONE)
    current_topic = min(topics, key=diff_key(now))
    return current_topic


def hidePath(path: str):
    """
    hide file/folder
    works on: Windows
    """
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    INVALID_FILE_ATTRIBUTES = -1
    FILE_ATTRIBUTE_HIDDEN = 2
    attrs = kernel32.GetFileAttributesW(path)
    if attrs == INVALID_FILE_ATTRIBUTES:
        logger.error(f"hidePath() error: {ctypes.get_last_error()}")
    attrs |= FILE_ATTRIBUTE_HIDDEN
    if not kernel32.SetFileAttributesW(path, attrs):
        logger.error(f"hidePath() error: {ctypes.get_last_error()}")


def readJSON(filename: str, default=None):
    """read json file and return data"""
    try:
        with open(filename, "rb") as file:
            loaded_data = orjson.loads(file.read())
            return loaded_data
    except Exception as e:  # like FileNotFound
        logger.exception(e)
        return default


def saveJSON(filename: str, data):
    """save data to filename"""
    with open(filename, "wb") as file:
        serialized = orjson.dumps(data, option=orjson.OPT_INDENT_2)
        file.write(serialized)


def open_folder_in_explorer(folder_path: str):
    """open a folder in Windows File Explorer"""
    if os.path.exists(folder_path):
        subrun(["explorer", folder_path])
