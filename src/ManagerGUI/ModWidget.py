from src.ManagerGUI.GenericThread import GenericThread
from src.Mod.Mod import Mod

from PySide2 import QtCore, QtWidgets, QtGui


class ModWidget(QtWidgets.QFrame):
    """
    Framed widget that holds and displays a Mod's info for use in Qt's list widget.
    """
    def __init__(self, mod: Mod, mod_manager, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QtCore.Qt.SolidLine)

        self.mod = mod
        self.mod_manager = mod_manager

        self.downloader_thread = GenericThread(self, lambda: self.mod_manager.download_mod(self.mod.id))
        self.updater_thread = GenericThread(self, lambda: self.mod_manager.update_mod(self.mod.id))

        self.download_button = None
        self.update_button = None
        self.install_button = None
        self.warning_icon = None

        self.rows = []

        self.setToolTip(self.mod.display_name)

        self.context_menu = None
        self.context_actions = []

        self.setup_widget()
        self.setup_context_menu()

    def setup_widget(self) -> None:
        """
        Sets up the widget representation; adding the labels and download button.
        """

        layout = QtWidgets.QVBoxLayout()

        self.downloader_thread.finished.connect(self.thread_finished)
        self.updater_thread.finished.connect(self.thread_finished)

        self.download_button = QtWidgets.QPushButton(self)
        self.download_button.setText("Download")
        self.download_button.clicked.connect(lambda: self.threaded_download())

        self.update_button = QtWidgets.QPushButton(self)
        self.update_button.setText("Update")
        self.update_button.clicked.connect(lambda: self.threaded_update())

        self.install_button = QtWidgets.QPushButton(self)
        self.install_button.setText("Install")
        self.install_button.clicked.connect(lambda: self.install_mod())

        self.warning_icon = QtWidgets.QLabel(self)
        self.warning_icon.setPixmap(QtGui.QPixmap("./data/graphics/outdated.png"))
        if self.mod.game_version in [None, ""]:
            self.warning_icon.setToolTip("This mod does not have a compatible game version set, and as such might not work for this version.")
        else:
            self.warning_icon.setToolTip("This mod was not made for this version and might not work properly.")

        if self.mod.compatible_game_version:
            self.warning_icon.hide()

        name_label = QtWidgets.QLabel(self)
        name_label.setText(self.mod.display_name)
        self.warning_icon.setMaximumHeight(name_label.height())
        self.warning_icon.setPixmap(self.warning_icon.pixmap().scaled(self.warning_icon.width(), self.warning_icon.height(), QtCore.Qt.KeepAspectRatio, QtGui.Qt.SmoothTransformation))
        self.warning_icon.setAlignment(QtCore.Qt.AlignRight)

        tags_label = QtWidgets.QLabel(self)
        tags_label.setStyleSheet("QLabel {color: #006994}")
        tags_label.setText(str(", ".join(self.mod.tags)))

        top_row = QtWidgets.QWidget(self)
        top_row_layout = QtWidgets.QHBoxLayout()

        name_label.setParent(top_row)
        self.warning_icon.setParent(top_row)

        top_row_layout.addWidget(name_label)
        top_row_layout.addWidget(self.warning_icon)

        top_row.setLayout(top_row_layout)

        layout.addWidget(top_row)

        second_row = QtWidgets.QWidget(self)
        second_row_layout = QtWidgets.QHBoxLayout()

        tags_label.setParent(second_row)

        second_row_layout.addWidget(tags_label)

        second_row.setLayout(second_row_layout)

        layout.addWidget(second_row)

        bottom_row = QtWidgets.QWidget(self)
        bottom_row_layout = QtWidgets.QGridLayout()

        self.download_button.setParent(bottom_row)
        self.install_button.setParent(bottom_row)
        self.update_button.setParent(bottom_row)

        bottom_row_layout.addWidget(self.download_button, 2, 0, 1, 2)
        bottom_row_layout.addWidget(self.install_button, 2, 0, 1, 1)
        bottom_row_layout.addWidget(self.update_button, 2, 1, 1, 1)

        bottom_row.setLayout(bottom_row_layout)

        layout.addWidget(bottom_row)

        self.rows.append(top_row)
        self.rows.append(second_row)
        self.rows.append(bottom_row)

        self.refresh_buttons()

        self.setLayout(layout)

    def refresh_buttons(self):
        if self.mod.downloaded_dir_path is None:
            self.update_button.hide()
            self.install_button.hide()
            self.download_button.show()
        else:
            self.update_button.show()
            self.install_button.show()
            self.download_button.hide()
            if not self.mod.update_available:
                self.update_button.setDisabled(True)
                self.update_button.setToolTip("You're up-to-date!")
            else:
                self.update_button.setDisabled(False)
                self.update_button.setToolTip("Update available!")

    def setup_context_menu(self) -> None:
        # self.context_actions.append(QtWidgets.QAction(text="Favourite"))
        # self.context_actions[-1].triggered.connect(self.favourite)
        # self.context_actions.append(QtWidgets.QAction(text="Set colour"))
        # self.context_actions[-1].triggered.connect(self.set_colour)
        self.context_actions.append(QtWidgets.QAction(text="Force download"))
        self.context_actions[-1].triggered.connect(self.threaded_download)
        self.context_actions.append(QtWidgets.QAction(text="Install"))
        self.context_actions[-1].triggered.connect(self.install_mod)

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

    def threaded_update(self):
        """
        Update the mod using the updater thread, preventing it from blocking the main thread.
        """
        if not self.updater_thread.isRunning():
            self.updater_thread.start()

    def thread_finished(self):
        """
        Called when the downloader thread is finished.
        """
        new_mod = self.mod_manager.get_mod(self.mod.id)
        self.mod = new_mod or self.mod
        self.refresh_buttons()

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        self.context_menu.popup(QtGui.QCursor.pos())

    def install_mod(self):
        self.mod_manager.install_mod(self.mod.id)
        self.parent().parent().refresh_installed_list()
