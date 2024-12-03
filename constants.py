"""app constant values"""

import os
from pytz import timezone
from tzlocal import get_localzone_name
from theme import isDarkMode

_tz_name = get_localzone_name()
TIMEZONE = timezone(_tz_name)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_DIR = os.path.join(BASE_DIR, "appdata")
os.makedirs(APP_DIR, exist_ok=True)

APPSETTINGS_FILE = os.path.join(APP_DIR, "cfg.json")

DB_DIR = os.path.join(APP_DIR, "db")
os.makedirs(DB_DIR, exist_ok=True)

APP_DB = os.path.join(DB_DIR, "app.sqlite")

APP_ICON = os.path.join(APP_DIR, "icons", "appicon_large.png")

if isDarkMode():
    ICONS_DIR = os.path.join(APP_DIR, "icons", "for_dark")
else:
    ICONS_DIR = os.path.join(APP_DIR, "icons", "for_light")

DELETE_ICON = os.path.join(ICONS_DIR, "delete_32dp.png")
SUBMIT_ICON = os.path.join(ICONS_DIR, "done_all_32dp.png")
ENTRIES_ICON = os.path.join(ICONS_DIR, "forum_32dp.png")
SEARCH_ICON = os.path.join(ICONS_DIR, "search_32dp.png")
SETTINGS_ICON = os.path.join(ICONS_DIR, "settings_32dp.png")
ADDCOMMENT_ICON = os.path.join(ICONS_DIR, "add_note_32dp.png")
ADD_ICON = os.path.join(ICONS_DIR, "add_32dp.png")
MORE_ICON = os.path.join(ICONS_DIR, "more.png")
NOTIFS_ON_ICON = os.path.join(ICONS_DIR, "notifs_on.png")
NOTIFS_OFF_ICON = os.path.join(ICONS_DIR, "notifs_off.png")

SOLVED_ICON = os.path.join(ICONS_DIR, "solved.png")
UNSOLVED_ICON = os.path.join(ICONS_DIR, "unsolved.png")


SHOW_FILE_ICON = os.path.join(ICONS_DIR, "see_file.png")
BACKUP_ICON = os.path.join(ICONS_DIR, "backup_table.png")

SOLVED_PLACEHOLDER = " -- Select -- "

TIME_UNITS = {"hours": 60, "minutes": 1}

DEFAULT_SETTINGS = {
    "notify_after": 30,
    "notify_units": "minutes",
    "disable_saturday": False,
    "disable_sunday": False,
}
