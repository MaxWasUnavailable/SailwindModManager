from PySide2 import QtCore


class DownloaderThread(QtCore.QThread):
    def __init__(self, parent=None):
        super(DownloaderThread, self).__init__(parent)
        self.locked = False

    def run(self):
        if not self.locked:
            self.locked = True
            self.parent().mod.download()
            self.locked = False
