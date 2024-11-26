import os
from shutil import copy2
from PyQt6.QtCore import QObject, QThreadPool, QRunnable, pyqtSignal
from constants import APP_DB


class FileTransferSignals(QObject):

    # error message
    errored = pyqtSignal(str)
    # done msg
    done = pyqtSignal(str)


class BackupWorker(QRunnable):
    """backup thread"""

    __slots__ = ("output_dir", "signals")

    def __init__(self, output_dir: str):
        super().__init__()
        self.setAutoDelete(True)

        self.output_dir = output_dir

        self.signals = FileTransferSignals()

    def run(self):
        backup_file = os.path.join(self.output_dir, os.path.basename(APP_DB))

        try:
            copy2(APP_DB, backup_file)
            self.signals.done.emit(f"Backup saved: '{backup_file}'")

        except Exception as e:
            self.signals.errored.emit(str(e))


threadpool_manager = QThreadPool()
