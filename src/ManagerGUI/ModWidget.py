from src.ManagerGUI.DownloaderThread import DownloaderThread
from src.Mod.Mod import Mod

from PySide2 import QtCore, QtWidgets, QtGui


class ModWidget(QtWidgets.QFrame):
    """
    Framed widget that holds and displays a Mod's info for use in Qt's list widget.
    """
    def __init__(self, mod: Mod, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QtCore.Qt.SolidLine)

        self.mod = mod

        self.downloader_thread = DownloaderThread(self)

        self.setToolTip(self.mod.display_name)

        self.context_menu = None
        self.context_actions = []

        self.setup_widget()
        self.setup_context_menu()

    def setup_widget(self) -> None:
        """
        Sets up the widget representation; adding the labels and download button.
        """
        layout = QtWidgets.QGridLayout()

        download_button = QtWidgets.QPushButton(self)
        download_button.setText("Download")
        name_label = QtWidgets.QLabel(self)
        name_label.setText(self.mod.display_name)
        tags_label = QtWidgets.QLabel(self)
        tags_label.setStyleSheet("QLabel {color: #006994}")
        tags_label.setText(str(", ".join(self.mod.tags)))

        self.downloader_thread.finished.connect(self.thread_finished)
        download_button.clicked.connect(lambda: self.threaded_download())
        # TODO: replace with lambda call to mod manager through parent?
        # Technically not necessary, though.

        layout.addWidget(name_label, 0, 0)
        layout.addWidget(tags_label, 1, 0)
        layout.addWidget(download_button, 2, 0)

        self.setLayout(layout)

    def setup_context_menu(self) -> None:
        self.context_actions.append(QtWidgets.QAction(text="Favourite"))
        self.context_actions[-1].triggered.connect(self.favourite)
        self.context_actions.append(QtWidgets.QAction(text="Set colour"))
        self.context_actions[-1].triggered.connect(self.set_colour)

        self.context_menu = QtWidgets.QMenu()
        self.context_menu.addActions(self.context_actions)

    def favourite(self):
        print("Favourite")

    def set_colour(self):
        print("Set colour")

    def get_display_text(self) -> str:
        """
        Generates the text to display in the mod info widget when selected.
        :return: The text to display.
        """
        text = ""

        text += f"""<h1>{self.mod.display_name} ({self.mod.id})</h1>"""

        if len(self.mod.tags) > 0:
            text += f"""<div style="color: #808080">"""
            text += f"""<i>{"</i> | <i>".join(self.mod.tags)}</i>"""
            text += f"""</div><br><br>"""

        if self.mod.description:
            text += f"""{self.mod.description}<br><br>"""

        if self.mod.author:
            text += f"""<u>Author:</u> {self.mod.author}<br>"""

        if self.mod.version:
            text += f"""<u>Version:</u> {self.mod.version}<br>"""

        if self.mod.game_version:
            text += f"""<u>Game version:</u> {self.mod.game_version}<br>"""

        if self.mod.manager_version:
            text += f"""<u>UMM version:</u> {self.mod.manager_version}<br>"""

        if self.mod.repository:
            text += f"""<u>Repository:</u> {self.mod.repository}<br>"""

        if self.mod.home_page:
            text += f"""<u>Home page:</u> {self.mod.home_page}"""

        return text

    def threaded_download(self):
        """
        Download the mod using the downloader thread, preventing it from blocking the main thread.
        """
        if not self.downloader_thread.isRunning():
            self.downloader_thread.start()

    def thread_finished(self):
        """
        Called when the downloader thread is finished.
        """
        pass

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        self.context_menu.popup(QtGui.QCursor.pos())

