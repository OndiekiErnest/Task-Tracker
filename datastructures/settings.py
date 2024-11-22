"""messages data model"""

import logging
from datastructures.qdicts import QDict
from utils import saveJSON, readJSON
from constants import DEFAULT_SETTINGS, APPSETTINGS_FILE

logger = logging.getLogger(__name__)


class AppSettings(QDict):
    """app-specific settings"""

    def __init__(self, filename=APPSETTINGS_FILE):
        super().__init__()
        self.filename = filename

        self.load()

    def load(self):
        """load settings from filename"""

        # populate settings
        setts = readJSON(self.filename, default=DEFAULT_SETTINGS)
        self.update(setts)

    def save(self):
        """save to filename"""
        data = self.raw()
        logger.info(f"Saving settings: {data}")
        saveJSON(self.filename, data)


settings = AppSettings()
