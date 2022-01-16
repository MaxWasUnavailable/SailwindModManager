from PySide2 import QtCore


class GenericThread(QtCore.QThread):
    """
    Generic thread object that can call a given function when it is ran.
    """
    def __init__(self, parent, func):
        """
        :param parent: Parent Qt Object/Widget
        :param func: Function to call when the thread is ran
        """
        super(GenericThread, self).__init__(parent)
        self.locked = False
        self.func = func

    def run(self) -> None:
        """
        Executed when the thread is started.
        If the thread is already executing, the self.locked variable will prevent it from running again.
        """
        if not self.locked:
            self.locked = True
            self.func()
            self.locked = False
