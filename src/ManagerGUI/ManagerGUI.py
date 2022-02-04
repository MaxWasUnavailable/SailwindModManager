from src.ManagerGUI.InstalledModWidget import InstalledModWidget
from src.ManagerGUI.GenericThread import GenericThread
from src.ModManager.ModManager import ModManager
from src.ManagerGUI.ModWidget import ModWidget
from src.Logger.Loggable import Loggable
from src.Config.Config import Config
from src.Logger.Logger import Logger
from src.Mod.Mod import Mod

from PySide2 import QtCore, QtWidgets, QtGui
from ast import literal_eval
from copy import copy


class Popup(QtWidgets.QWidget):
    """
    Simple text popup.
    """
    def __init__(self, message):
        """
        Sets its content to the given message, and enabled rich text representation as well as opening links through the browser.
        Shows itself when it's created, so no further action is necessary after creating this object.
        (Make sure the object doesn't go out of scope, otherwise it'll instantly close)
        # TODO: Replace with built-in QT Dialogue?
        :param message: Message to display.
        """
        super().__init__()
        label = QtWidgets.QLabel(message)
        label.setTextFormat(QtCore.Qt.RichText)
        label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        label.setOpenExternalLinks(True)
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        self.setLayout(layout)
        self.setFixedSize(400, 120)
        self.show()


class ManagerGUI(Loggable, QtWidgets.QMainWindow):
    """
    Main GUI window.
    Holds all widgets.
    """
    def __init__(self, logger: Logger, config: Config = Config()):
        """
        :param logger: Logger class to use to handle the logs
        :param config: Config object to use as config. Optional.
        """
        super().__init__(logger=logger)
        self.setWindowTitle("Sailwind Mod Manager")
        self.central_widget = None
        self.popups = []

        self.config = config
        self.mod_manager = ModManager(logger, config)

        self.setup_window()

    def closeEvent(self, QCloseEvent) -> None:
        """
        Called when the window closes.
        Close all remaining popups when the window is closed.
        """
        for popup in self.popups:
            popup.close()

    def popup(self, message: str) -> None:
        """
        Create and show a popup dialogue.
        :param message: The message to display.
        """
        self.popups.append(Popup(message))

    def setup_window(self) -> None:
        """
        Sets up the window.
        Initialises the necessary widgets.
        """
        self.central_widget = ManagerTabWidget(self, self.mod_manager, self.config)
        self.setCentralWidget(self.central_widget)


class ManagerTabWidget(QtWidgets.QTabWidget):
    """
    A widget that holds all tabs.
    """
    def __init__(self, parent, mod_manager: ModManager, config: Config):
        super().__init__(parent)
        self.mod_manager = mod_manager
        self.config = config

        self.download_tab = None
        self.installation_tab = None
        self.settings_tab = None
        self.save_manager_tab = None

        self.setup_tabs()

    def setup_tabs(self):
        """
        Sets up the tabs.
        Initialises the necessary tabs and adds them to the tab widget.
        """

        self.download_tab = DownloadTab(self, self.mod_manager)

        self.addTab(self.download_tab, "Download Mods")

        self.installation_tab = InstallationTab(self, self.mod_manager)

        self.addTab(self.installation_tab, "Installed Mods")

        # self.save_manager_tab = SaveManagerTab(self, self.config)
        #
        # self.addTab(self.save_manager_tab, "Save Manager")

        self.settings_tab = SettingsTab(self, self.config)

        self.addTab(self.settings_tab, "Settings")


# Save Manager Tab


class SaveManagerTab(QtWidgets.QWidget):
    """
    A tab that holds save manager-related widgets.
    """
    def __init__(self, parent, config: Config):
        super().__init__(parent)
        self.config = config

        self.save_manager_widget = None

        self.setup_widget()

    def setup_widget(self):

        layout = QtWidgets.QGridLayout(self)

        self.save_manager_widget = SaveManagerWidget(self, config=self.config)

        self.save_manager_widget.setMinimumSize(self.save_manager_widget.sizeHint())

        layout.addWidget(self.save_manager_widget, 0, 0)

        self.setLayout(layout)


class SaveManagerWidget(QtWidgets.QFrame):
    """
    Widget that handles editing of settings.
    """
    def __init__(self,  parent, config: Config):
        super().__init__(parent)
        self.config = config

        self.setFrameStyle(QtCore.Qt.SolidLine)
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel("WORK IN PROGRESS", self))

        self.setLayout(layout)


# Settings Tab


class SettingsTab(QtWidgets.QWidget):
    """
    A tab that holds settings-related widgets.
    """
    def __init__(self, parent, config: Config):
        super().__init__(parent)
        self.config = config

        self.settings_editor = None

        self.setup_widget()

    def setup_widget(self):

        layout = QtWidgets.QGridLayout(self)

        self.settings_editor = SettingsEditor(self, config=self.config)
        self.settings_menu = SettingsMenu(self, config=self.config)

        self.settings_editor.setMinimumSize(self.settings_editor.sizeHint())
        self.settings_menu.setMinimumSize(self.settings_menu.sizeHint())

        layout.addWidget(self.settings_editor, 0, 0, 7, 1)
        layout.addWidget(self.settings_menu, 7, 0, 1, 1)

        self.setLayout(layout)


class SettingsEditor(QtWidgets.QFrame):
    """
    Widget that handles editing of settings.
    """
    def __init__(self,  parent, config: Config):
        super().__init__(parent)
        self.config = config

        self.setFrameStyle(QtCore.Qt.SolidLine)

        self.github_access_token_field = None
        self.downloads_directory_field = None
        self.game_directory_field = None
        self.game_version_field = None
        self.repository_ids_list = None

        self.setup_widget()

    def setup_widget(self):
        self.github_access_token_field = QtWidgets.QLineEdit(self)
        self.github_access_token_field.setToolTip("Optional. Can be changed to a personal token to prevent being rate limited.")
        self.github_access_token_field.setText(self.config.config.get("github_access_token", ""))

        self.downloads_directory_field = QtWidgets.QLineEdit(self)
        self.downloads_directory_field.setToolTip("Directory to download mods to.")
        self.downloads_directory_field.setText(self.config.config.get("downloads_directory", ""))

        self.game_directory_field = QtWidgets.QLineEdit(self)
        self.game_directory_field.setToolTip("Game's directory.")
        self.game_directory_field.setText(self.config.config.get("game_directory", ""))

        self.game_version_field = QtWidgets.QLineEdit(self)
        self.game_version_field.setToolTip("Game's version. For now, this has to be manually set.")
        self.game_version_field.setText(self.config.config.get("game_version", ""))

        self.repository_ids_list = QtWidgets.QLineEdit(self)
        self.repository_ids_list.setToolTip("List of repositories to pull mods from. Do not touch if you don't know what you're doing. If in doubt, ask a Modder (or Max) on the official Discord.")
        self.repository_ids_list.setText(str(self.config.config.get("repository_ids", [])))

        layout = QtWidgets.QVBoxLayout()

        for field in [(self.github_access_token_field, 'Github Access Token:'),
                      (self.downloads_directory_field, 'Downloads Directory:'),
                      (self.game_directory_field, 'Game Directory:'),
                      (self.game_version_field, 'Game Version:'),
                      (self.repository_ids_list, 'Repository IDs:')]:

            subwidget_layout = QtWidgets.QHBoxLayout()

            subwidget = QtWidgets.QWidget(self)

            field[0].setParent(subwidget)

            field_label = QtWidgets.QLabel(subwidget)
            field_label.setText(field[1])

            subwidget_layout.addWidget(field_label)
            subwidget_layout.addWidget(field[0])

            subwidget.setLayout(subwidget_layout)

            layout.addWidget(subwidget)

        self.setLayout(layout)

    def apply_settings(self):
        self.config.config["github_access_token"] = self.github_access_token_field.text()
        self.config.config["downloads_directory"] = self.downloads_directory_field.text()
        self.config.config["game_directory"] = self.game_directory_field.text()
        self.config.config["repository_ids"] = literal_eval(self.repository_ids_list.text())
        self.config.config["game_version"] = self.game_version_field.text()
        self.config.save_config()


class SettingsMenu(QtWidgets.QFrame):
    """
    Widget that handles confirming of settings.
    """
    def __init__(self,  parent, config: Config):
        super().__init__(parent)
        self.config = config

        self.confirm_button = None

        self.setup_widget()

    def setup_widget(self):
        layout = QtWidgets.QHBoxLayout()

        self.confirm_button = QtWidgets.QPushButton(self)
        self.confirm_button.setText("Apply settings")

        layout.addWidget(QtWidgets.QLabel(self))
        layout.addWidget(self.confirm_button)
        layout.addWidget(QtWidgets.QLabel(self))

        self.setLayout(layout)

        self.confirm_button.pressed.connect(lambda: self.parent().settings_editor.apply_settings())


# Installation Tab


class InstallationTab(QtWidgets.QWidget):
    """
    A tab that holds installation-related widgets.
    """
    def __init__(self, parent, mod_manager: ModManager):
        super().__init__(parent)
        self.mod_manager = mod_manager

        self.mod_display = None
        self.mod_list = None
        self.installation_misc_menu = None

        self.setup_widget()

    def setup_widget(self):

        layout = QtWidgets.QGridLayout(self)

        self.mod_display = ModDisplay(self)
        self.mod_list = InstalledModListContainer(self, mod_manager=self.mod_manager)
        self.installation_misc_menu = InstallMiscMenu(self)

        self.mod_display.setMinimumSize(self.mod_display.sizeHint())
        self.mod_list.setMinimumSize(self.mod_list.sizeHint())
        self.installation_misc_menu.setMinimumSize(self.installation_misc_menu.sizeHint())

        layout.addWidget(self.mod_list, 0, 0, 5, 1)
        layout.addWidget(self.installation_misc_menu, 5, 0, 1, 1)
        layout.addWidget(self.mod_display, 0, 1, 6, 1)

        self.setLayout(layout)


class InstalledModListContainer(QtWidgets.QFrame):
    """
    Widget that contains Installed Mod List related widgets.
    """
    def __init__(self,  parent, mod_manager: ModManager):
        super().__init__(parent)
        self.setFrameStyle(QtCore.Qt.SolidLine)
        layout = QtWidgets.QVBoxLayout()

        self.list = InstalledModList(self, mod_manager)

        layout.addWidget(self.list, stretch=1)

        self.setLayout(layout)


class InstalledModList(QtWidgets.QListWidget):
    """
    List that contains and represents installed mods.
    """
    def __init__(self,  parent, mod_manager: ModManager):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        self.mod_manager = mod_manager

        self.installation_tab = self.parent().parent()

        self.currentItemChanged.connect(self.current_item_changed)

        self.refresh_list()

    def current_item_changed(self) -> None:
        """
        Execute when the selected item has changed in the Mod List widget.
        """
        if self.currentItem() is not None:
            self.installation_tab.mod_display.update_display(self.itemWidget(self.currentItem()))

    def clear_list(self) -> None:
        """
        Clears the list.
        """
        self.clear()

    def add_item(self, mod: Mod) -> None:
        """
        Adds an item to the list, and then sets that item to display the given ModEntry widget.
        :param mod: The mod to list.
        """
        item = QtWidgets.QListWidgetItem()
        mod_widget = InstalledModWidget(mod=mod, mod_manager=self.mod_manager)
        item.setSizeHint(mod_widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, mod_widget)

    def fill_list(self, mods: list[Mod]) -> None:
        """
        Fills the mod list with mods.
        :param mods: List of mods to use.
        """
        self.clear_list()
        for mod in mods:
            self.add_item(mod)

    def refresh_list(self, refresh: bool = False) -> None:
        """
        Refresh the list.
        """
        self.fill_list(self.mod_manager.get_installed_mods(refresh=refresh))


class InstallMiscMenu(QtWidgets.QFrame):
    """
    Misc menu widget with buttons related to the installation tab.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QtCore.Qt.SolidLine)
        self.main_window = self.parent().parent().parent()

        self.setup_widget()

    def setup_widget(self) -> None:
        """
        Sets up the widget.
        Initialises misc buttons and the like.
        """
        layout = QtWidgets.QGridLayout()

        refresh_button = QtWidgets.QPushButton(self)
        refresh_button.setText("Refresh")

        about_button = QtWidgets.QPushButton(self)
        about_button.setText("About")

        label = QtWidgets.QLabel(self)
        label.setText("Created by Max.")
        label.setAlignment(QtCore.Qt.AlignCenter)

        refresh_button.clicked.connect(lambda: self.parent().mod_list.list.refresh_list(refresh=True))
        about_button.clicked.connect(lambda: self.main_window.popup("For more information, feel free to contact me on the Sailwind Discord server!<br>This tool was written in Python 3.9, using Qt as graphics library.<br>The mod repository can be found <a href=\"https://github.com/MaxWasUnavailable/SailwindModRepository\">here</a>.<br>The tool's source code can be found <a href=\"https://github.com/MaxWasUnavailable/SailwindModManager\">here</a>."))

        layout.addWidget(refresh_button, 0, 0)
        layout.addWidget(about_button, 0, 1)
        layout.addWidget(label, 1, 0, 1, 2)

        self.setLayout(layout)


# Download Tab


class DownloadTab(QtWidgets.QWidget):
    """
    A tab that holds download-related widgets.
    """
    def __init__(self, parent, mod_manager: ModManager):
        super().__init__(parent)
        self.mod_manager = mod_manager

        self.mod_display = None
        self.mod_list = None
        self.misc_menu = None

        self.setup_widget()

    def setup_widget(self) -> None:
        layout = QtWidgets.QGridLayout(self)

        self.mod_display = ModDisplay(self)
        self.mod_list = ModListContainer(self, mod_manager=self.mod_manager)
        self.misc_menu = MiscMenu(self)

        self.mod_display.setMinimumSize(self.mod_display.sizeHint())
        self.mod_list.setMinimumSize(self.mod_list.sizeHint())
        self.misc_menu.setMinimumSize(self.misc_menu.sizeHint())

        layout.addWidget(self.mod_list, 0, 0, 5, 1)
        layout.addWidget(self.misc_menu, 5, 0, 1, 1)
        layout.addWidget(self.mod_display, 0, 1, 6, 1)

        self.setLayout(layout)


class ModImage(QtWidgets.QLabel):
    """
    Represents a mod's image.

    TODO: Still needs some work to properly scale images / keep aspect ratio correct.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setScaledContents(True)
        self.setMinimumSize(1, 1)
        self.set_placeholder()

    def resizeEvent(self, QResizeEvent) -> None:
        """
        Called whenever the window is resized.
        """
        self.__resize()

    def __resize(self) -> None:
        """
        Private function to resize the mod's image.
        """
        self.setPixmap(self.pixmap().scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio, QtGui.Qt.SmoothTransformation))

    def set_placeholder(self) -> None:
        """
        Sets image using placeholder.
        """
        self.setPixmap(QtGui.QPixmap("./data/placeholder-image.png"))

    def set_image(self, image) -> None:
        """
        Sets the image based on the raw bytes given.
        Copy is made since the image was otherwise lost after being read.
        TODO: Can probably be done cleaner.
        :param image: The raw bytes to use for the image.
        """
        if image is not None:
            self.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(QtCore.QByteArray(copy(image)))))
        else:
            self.set_placeholder()


class ModInfo(QtWidgets.QTextEdit):
    """
    A text panel that displays a mod's information.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        self.setReadOnly(True)
        self.setAcceptRichText(True)

    def set_text(self, text: str) -> None:
        """
        Sets the text displayed in the panel.
        :param text: Text to display.
        """
        self.setHtml(text)


class ModDisplay(QtWidgets.QFrame):
    """
    Framed widget that contains widgets that display information on the selected mod.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        self.setFrameStyle(QtCore.Qt.SolidLine)

        self.mod_image = None
        self.mod_info = None

        self.setup_widget()

    def setup_widget(self) -> None:
        """
        Sets up the widget.
        Initialises the mod image and info widgets.
        """
        layout = QtWidgets.QGridLayout()

        self.mod_image = ModImage(self)
        self.mod_info = ModInfo(self)

        self.mod_image.setMinimumSize(self.mod_image.sizeHint())
        self.mod_info.setMinimumSize(self.mod_info.sizeHint())

        layout.addWidget(self.mod_image, 0, 0, 2, 1)
        layout.addWidget(self.mod_info, 2, 0, 1, 1)

        self.setLayout(layout)

    def update_display(self, mod: ModWidget) -> None:
        """
        Update the Mod Display Image & Info widgets with information from the provided mod widget.
        :param mod: The mod to display.
        """
        try:
            self.mod_image.set_image(mod.mod.image)
        except Exception as e:
            # TODO: Log error
            self.mod_image.set_placeholder()
        self.mod_info.set_text(mod.get_display_text())


class ModListContainer(QtWidgets.QFrame):
    """
    Widget that contains Mod List related widgets.
    """
    def __init__(self,  parent, mod_manager: ModManager):
        super().__init__(parent)
        self.setFrameStyle(QtCore.Qt.SolidLine)
        layout = QtWidgets.QVBoxLayout()

        self.search = ModListSearch(self, mod_manager)
        self.list = ModList(self, mod_manager)

        layout.addWidget(self.search, stretch=1)
        layout.addWidget(self.list, stretch=9)

        self.setLayout(layout)


class ModListSearch(QtWidgets.QWidget):
    """
    Widget that contains widgets and functionality related to the Mod List's search.
    """
    def __init__(self,  parent, mod_manager: ModManager):
        super().__init__(parent)
        self.mod_manager = mod_manager

        self.setFixedHeight(25)

        self.download_tab = self.parent().parent()

        layout = QtWidgets.QHBoxLayout()

        self.search_bar = ModListSearchBar(self)
        # self.search_button = ModListSearchButton(self, mod_manager)

        layout.addWidget(self.search_bar, stretch=8)
        # layout.addWidget(self.search_button, stretch=1)

        layout.setMargin(0)

        self.setLayout(layout)

    def execute_search(self) -> None:
        """
        Executes the search by applying the search filter to the Mod Manager and refresh the Mod List.
        """
        self.mod_manager.set_filter_search(self.search_bar.text())
        self.download_tab.mod_list.list.refresh_list()


class ModListSearchBar(QtWidgets.QLineEdit):
    """
    Mod List's search bar.
    """
    def __init__(self,  parent):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def keyPressEvent(self, arg__1) -> None:
        """
        Executed when a key press is detected in the search bar.
        """
        super(ModListSearchBar, self).keyPressEvent(arg__1)
        self.parent().execute_search()


class ModListSearchButton(QtWidgets.QPushButton):
    """
    Unused since the Search Bar now triggers the execute search function on any key press.
    Used to be a button that executes the search.
    """
    def __init__(self,  parent, mod_manager: ModManager):
        super().__init__(parent)
        self.mod_manager = mod_manager

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setFixedWidth(25)

        self.setText(">")

        self.main_window = self.parent().parent().parent().parent().parent()
        self.search_bar = self.parent().search_bar

        self.pressed.connect(self.parent().execute_search)


class ModList(QtWidgets.QListWidget):
    """
    List that contains and represents mods available in the configured central mod repositories.
    """
    def __init__(self,  parent, mod_manager: ModManager):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        self.mod_manager = mod_manager

        self.refetcher_thread = GenericThread(self, self.refetch_list)
        self.download_tab = self.parent().parent()
        self.rate_limited = False
        self.refreshing = False
        self.refresh_icon = None

        self.refetcher_thread.finished.connect(self.thread_finished)
        self.currentItemChanged.connect(self.current_item_changed)

        self.setup_widget()

        self.threaded_refetch_list()

    def setup_widget(self):
        self.refresh_icon = QtWidgets.QLabel(self)
        try:
            self.refresh_icon.setMovie(QtGui.QMovie("./data/loading.gif"))
            self.refresh_icon.movie().start()
        except Exception as e:
            return

    def refresh_refreshing(self) -> None:
        if self.refreshing:
            self.refresh_icon.show()
        else:
            self.refresh_icon.hide()

    def current_item_changed(self) -> None:
        """
        Execute when the selected item has changed in the Mod List widget.
        """
        if self.currentItem() is not None:
            self.download_tab.mod_display.update_display(self.itemWidget(self.currentItem()))

    def refetch_list(self) -> None:
        """
        Refetch the mod list.
        """
        self.rate_limited = not self.mod_manager.fetch_info()

    def threaded_refetch_list(self) -> None:
        """
        Refetch the mod list using the refetcher thread, preventing it from blocking the main thread.
        """
        if not self.refetcher_thread.isRunning():
            self.refreshing = True
            self.refresh_refreshing()
            self.refetcher_thread.start()

    def thread_finished(self) -> None:
        """
        Called when the refresher thread is finished.
        """
        self.refresh_list()
        self.refreshing = False
        self.refresh_refreshing()
        if self.rate_limited:
            self.main_window.popup("Error 403.<br>Github has rate limited you for refreshing too often.<br>To circumvent this, you'll need to use a Github token.<br>My apologies for this!")
            self.rate_limited = False

    def clear_list(self) -> None:
        """
        Clears the list.
        """
        self.clear()

    def add_item(self, mod: Mod) -> None:
        """
        Adds an item to the list, and then sets that item to display the given ModEntry widget.
        :param mod: The mod to list.
        """
        item = QtWidgets.QListWidgetItem()
        mod_widget = ModWidget(mod=mod, parent=self, mod_manager=self.mod_manager)
        item.setSizeHint(mod_widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, mod_widget)

    def fill_list(self, mods: list[Mod]) -> None:
        """
        Fills the mod list with mods.
        :param mods: List of mods to use.
        """
        self.clear_list()
        for mod in mods:
            self.add_item(mod)

    def refresh_list(self) -> None:
        """
        Refresh the mod list without refetching all entries.
        """
        self.fill_list(self.mod_manager.get_mods())

    def refresh_installed_list(self) -> None:
        """
        Force a refresh for the install list.
        (Useful, for example, if you install a mod)
        """
        self.parent().parent().parent().parent().installation_tab.mod_list.list.refresh_list()


class MiscMenu(QtWidgets.QFrame):
    """
    Misc menu widget with buttons related to the downloads tab.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QtCore.Qt.SolidLine)
        self.main_window = self.parent().parent().parent()

        self.setup_widget()

    def setup_widget(self) -> None:
        """
        Sets up the widget.
        Initialises misc buttons and the like.
        """
        layout = QtWidgets.QGridLayout()

        discord_button = QtWidgets.QPushButton(self)
        discord_button.setText("Discord")

        about_button = QtWidgets.QPushButton(self)
        about_button.setText("About")

        label = QtWidgets.QLabel(self)
        label.setText("Created by Max.")
        label.setAlignment(QtCore.Qt.AlignCenter)

        discord_button.clicked.connect(lambda: self.main_window.popup("""<a href=\"https://discord.gg/msuBMFrpYg\">https://discord.gg/msuBMFrpYg</a>"""))
        about_button.clicked.connect(lambda: self.main_window.popup("For more information, feel free to contact me on the Sailwind Discord server!<br>This tool was written in Python 3.9, using Qt as graphics library.<br>The mod repository can be found <a href=\"https://github.com/MaxWasUnavailable/SailwindModRepository\">here</a>.<br>The tool's source code can be found <a href=\"https://github.com/MaxWasUnavailable/SailwindModManager\">here</a>."))

        layout.addWidget(discord_button, 0, 0)
        layout.addWidget(about_button, 0, 1)
        layout.addWidget(label, 1, 0, 1, 2)

        self.setLayout(layout)
