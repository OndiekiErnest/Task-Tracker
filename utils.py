"""app utility functions"""

import ctypes
import orjson
import logging
from datastructures.datas import Key

logger = logging.getLogger(__name__)


class Singleton(type):
    """singleton metaclass"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        key = Key(obj=cls, args=args, kwargs=frozenset(kwargs.items()))
        if key not in cls._instances:
            cls._instances[key] = super().__call__(*args, **kwargs)
        return cls._instances[key]


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
        raise ctypes.WinError(ctypes.get_last_error())
    attrs |= FILE_ATTRIBUTE_HIDDEN
    if not kernel32.SetFileAttributesW(path, attrs):
        raise ctypes.WinError(ctypes.get_last_error())


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
