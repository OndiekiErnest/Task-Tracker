"""dict that emits PyQt6 signals when it changes"""

from PyQt6.QtCore import QObject, pyqtSignal
from contextlib import contextmanager


class QDict(QObject):
    """mapping protocol"""

    __slots__ = ("_data",)

    changed = pyqtSignal(object)
    """signal emits changed key or None for batch changes"""

    def __init__(self, data: dict = None):
        super().__init__()

        self._data = {}
        """storage"""
        self._should_emit = True
        if data:
            self._data.update(data)

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return bool(self._data)

    def __repr__(self):
        return repr(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        if self._should_emit:
            self.changed.emit(key)

    def __delitem__(self, key):
        del self._data[key]
        if self._should_emit:
            self.changed.emit(key)

    def __eq__(self, other):
        if isinstance(other, dict):
            return self._data == other
        return False

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, key):
        return key in self._data

    @contextmanager
    def dontEmit(self):
        """suppress signal emit"""
        prev_state = self._should_emit
        self._should_emit = False
        try:
            yield self
        finally:
            self._should_emit = prev_state

    def clear(self):
        self._data.clear()
        if self._should_emit:
            self.changed.emit(None)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def pop(self, key, default=None):
        item = self._data.pop(key, default)
        if self._should_emit:
            self.changed.emit(key)
        return item

    def setdefault(self, key, default=None):
        value = self._data.setdefault(key, default)
        if self._should_emit:
            self.changed.emit(key)
        return value

    def update(self, data):
        self._data.update(data)
        if self._should_emit:
            self.changed.emit(None)

    def raw(self):
        """raw data"""
        return self._data
