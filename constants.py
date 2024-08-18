"""app constant values"""

import os
from pytz import timezone
from tzlocal import get_localzone_name

_tz_name = get_localzone_name()
TIMEZONE = timezone(_tz_name)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_DIR = os.path.join(BASE_DIR, "appdata")
os.makedirs(APP_DIR, exist_ok=True)

DB_DIR = os.path.join(APP_DIR, "db")
os.makedirs(DB_DIR, exist_ok=True)

ICONS_DIR = os.path.join(APP_DIR, "icons")

APP_ICON = os.path.join(ICONS_DIR, "appicon_large.png")

APP_DB = os.path.join(DB_DIR, "app.sqlite")

TIME_UNITS = {"hours": 60, "minutes": 1}
