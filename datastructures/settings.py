"""messages data model"""

from PyQt6.QtCore import QObject, pyqtSignal
from datastructures.qdicts import QDict
from utils import saveJSON, readJSON, Singleton
from constants import DEFAULT_SETTINGS, APPSETTINGS_FILE


class BaseSettingsSignals(QObject):
    """pyqtSignals"""

    changes_made = pyqtSignal(object)


# use this method because QObject is not friendly with metaclass
class BaseSettings(metaclass=Singleton):
    """Base Settings; supports mapping protocol"""

    def __init__(self, filename):

        self.filename = filename
        """JSON filename used for storing settings"""
        self.signals = BaseSettingsSignals()

        # storage
        self.data = QDict()
        """dict of all settings"""
        # load from file
        self.load()
        self.data.changed.connect(self._on_changes)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __iter__(self):
        return iter(self.data)

    def __reversed__(self):
        return reversed(self.data)

    def __contains__(self, key):
        return key in self.data

    def __eq__(self, other):
        if isinstance(other, QDict):
            return self._data == other
        return False

    def __len__(self):
        return len(self.data)

    def __bool__(self):
        return bool(self.data)

    def __delitem__(self, key):
        del self.data[key]

    def _on_changes(self, key):
        """receive the key that changed"""
        self.signals.changes_made.emit(key)

    def items(self):
        """return k-v pair"""
        return self.data.items()

    def keys(self):
        """return keys"""
        return self.data.keys()

    def values(self):
        """return values"""
        return self.data.values()

    def pop(self, key, default=None):
        """pop item of key and return it"""
        return self.data.pop(key, default)

    def get(self, key, default=None):
        """get setting of key or None"""
        return self.data.get(key, default)

    def resetAll(self):
        """clear settings"""
        self.data.clear()


class AppSettings(BaseSettings):
    """app-specific settings"""

    def __init__(self, filename=APPSETTINGS_FILE):
        super().__init__(filename)

    def load(self):
        """load settings from filename"""

        # populate settings
        setts = readJSON(self.filename, default=DEFAULT_SETTINGS)
        self.data.update(setts)

    def save(self):
        """save to filename"""

        saveJSON(self.filename, self.data.raw())


settings = AppSettings()
