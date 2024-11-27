import os
from shutil import copy2
from PyQt6.QtCore import QObject, QThreadPool, QRunnable, pyqtSignal


class FileTransferSignals(QObject):

    # error message
    errored = pyqtSignal(str)
    # done msg
    done = pyqtSignal(str)


class FileCopyWorker(QRunnable):
    """file copy runnable"""

    __slots__ = ("dest_dir", "signals")

    def __init__(self, src: str, dest_dir: str):
        super().__init__()
        self.setAutoDelete(True)

        self.src = src
        self.dest_dir = dest_dir

        self.signals = FileTransferSignals()

    def run(self):
        dest_file = os.path.join(self.dest_dir, os.path.basename(self.src))

        try:
            # passing a file as dest overwrites existing
            # passing a folder as dest raises error if file exists
            copy2(self.src, dest_file)
            self.signals.done.emit(f"'{self.src}' copied to '{dest_file}'")

        except Exception as e:
            self.signals.errored.emit(str(e))


threadpool_manager = QThreadPool()
