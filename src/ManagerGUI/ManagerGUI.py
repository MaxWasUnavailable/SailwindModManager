from src.ModManager.ModManager import ModManager
from src.ManagerGUI.ModWidget import ModWidget
from src.Logger.Loggable import Loggable
from src.Config.Config import Config
from src.Logger.Logger import Logger
from src.Mod.Mod import Mod

from PySide2 import QtCore, QtWidgets, QtGui
from copy import copy


class Popup(QtWidgets.QWidget):
    """
    Simple text popup.
    """
    def __init__(self, message):
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


class RefetcherThread(QtCore.QThread):
    def __init__(self, parent=None):
        super(RefetcherThread, self).__init__(parent)
        self.locked = False

    def run(self):
        if not self.locked:
            self.locked = True
            self.parent().refetch_list()
            self.locked = False


class ManagerGUI(Loggable, QtWidgets.QMainWindow):
    """
    Main GUI window.
    Holds all widgets.
    """
    def __init__(self, logger: Logger, config: Config = Config()):
        super().__init__(logger=logger)
        self.setWindowTitle("Sailwind Mod Manager")
        self.central_widget = None
        self.popups = []

        self.config = config
        self.mod_manager = ModManager(logger, config)

        self.setup_window()

    def closeEvent(self, QCloseEvent):
        """
        Close all remaining popups when the window is closed.
        """
        for popup in self.popups:
            popup.close()

    def popup(self, message):
        """
        Create and show a popup dialogue.
        :param message: The message to display.
        """
        self.popups.append(Popup(message))

    def setup_window(self):
        """
        Sets up the window.
        Initialises the necessary widgets.
        """
        self.central_widget = ManagerTabWidget(self, self.mod_manager)
        self.setCentralWidget(self.central_widget)


class ManagerTabWidget(QtWidgets.QTabWidget):
    """
    A widget that holds all tabs.
    """
    def __init__(self, parent, mod_manager: ModManager):
        super().__init__(parent)
        self.mod_manager = mod_manager

        self.setup_tabs()

    def setup_tabs(self):
        """
        Sets up the tabs.
        Initialises the necessary tabs and adds them to the tab widget.
        """

        self.addTab(DownloadTab(self, self.mod_manager), "Download Tab")


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

    def setup_widget(self):

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

    def resizeEvent(self, QResizeEvent):
        self.__resize()

    def __resize(self):
        self.setPixmap(self.pixmap().scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio, QtGui.Qt.SmoothTransformation))

    def set_placeholder(self):
        """
        Sets image using placeholder.
        """
        self.setPixmap(QtGui.QPixmap("./data/placeholder-image.png"))

    def set_image(self, image):
        """
        Sets the image based on the raw bytes given.
        Copy is made since the image was otherwise lost after being read.
        TODO: Can probably be done cleaner.
        :param image: The raw bytes to use.
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

    def set_text(self, text: str):
        """
        Sets the text displayed in the panel.
        :param text: Text to display.
        """
        self.setHtml(text)


class ModDisplay(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        self.setFrameStyle(QtCore.Qt.SolidLine)

        self.mod_image = None
        self.mod_info = None

        self.setup_widget()

    def setup_widget(self):
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

    def update_display(self, mod: ModWidget):
        """
        Update the Mod Display Image & Info widgets with information from the provided mod widget.
        :param mod: The mod to display.
        """
        self.mod_image.set_image(mod.mod.image)
        self.mod_info.set_text(mod.get_display_text())


class ModListContainer(QtWidgets.QFrame):
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

    def execute_search(self):
        self.mod_manager.set_filter_search(self.search_bar.text())
        self.download_tab.mod_list.list.refresh_list()


class ModListSearchBar(QtWidgets.QLineEdit):
    def __init__(self,  parent):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def keyPressEvent(self, arg__1) -> None:
        super(ModListSearchBar, self).keyPressEvent(arg__1)
        # if arg__1.nativeVirtualKey() == 13 or self.text() == "":
        self.parent().execute_search()


class ModListSearchButton(QtWidgets.QPushButton):
    """
    Unused
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
    def __init__(self,  parent, mod_manager: ModManager):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        self.mod_manager = mod_manager

        self.refetcher_thread = RefetcherThread(self)
        self.download_tab = self.parent().parent()
        self.rate_limited = False

        self.refetcher_thread.finished.connect(self.thread_finished)
        self.currentItemChanged.connect(self.current_item_changed)

        self.threaded_refetch_list()

    def current_item_changed(self):
        """
        Execute when the selected item has changed in the Mod List widget.
        """
        if self.currentItem() is not None:
            self.download_tab.mod_display.update_display(self.itemWidget(self.currentItem()))

    def refetch_list(self):
        """
        Refresh the mod list.
        """
        self.rate_limited = not self.mod_manager.fetch_info()

    def threaded_refetch_list(self):
        """
        Refresh the mod list using the refresher thread, preventing it from blocking the main thread.
        """
        if not self.refetcher_thread.isRunning():
            self.refetcher_thread.start()

    def thread_finished(self):
        """
        Called when the refresher thread is finished.
        """
        self.refresh_list()
        if self.rate_limited:
            self.main_window.popup("Error 403.<br>Github has rate limited you for refreshing too often.<br>Please wait a couple of minutes before trying again.<br>My apologies for this!")
            self.rate_limited = False

    def clear_list(self):
        """
        Clears the list.
        """
        self.clear()

    def add_item(self, mod: Mod):
        """
        Adds an item to the list, and then sets that item to display the given ModEntry widget.
        :param mod: The mod to list.
        """
        item = QtWidgets.QListWidgetItem()
        mod_widget = ModWidget(mod=mod)
        item.setSizeHint(mod_widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, mod_widget)

    def fill_list(self, mods: list[Mod]):
        """
        Fills the mod list with mods.
        :param mods: List of mods to use.
        """
        self.clear_list()
        for mod in mods:
            self.add_item(mod)

    def refresh_list(self):
        self.fill_list(self.mod_manager.get_mods())


class MiscMenu(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))
        self.setFrameStyle(QtCore.Qt.SolidLine)
        self.main_window = self.parent().parent().parent()

        self.setup_widget()

    def setup_widget(self):
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
        label.setText("See the config.yaml file in the data folder for settings.\nCreated by Max.")
        label.setAlignment(QtCore.Qt.AlignCenter)

        discord_button.clicked.connect(lambda: self.main_window.popup("""<a href=\"https://discord.gg/msuBMFrpYg\">https://discord.gg/msuBMFrpYg</a>"""))
        about_button.clicked.connect(lambda: self.main_window.popup("For more information, feel free to contact me on the Sailwind Discord server!<br>This tool was written in Python 3.9, using Qt as graphics library.<br>The mod repository can be found <a href=\"https://github.com/MaxWasUnavailable/SailwindModRepository\">here</a>.<br>The tool's source code can be found <a href=\"https://github.com/MaxWasUnavailable/SailwindModManager\">here</a>."))

        layout.addWidget(discord_button, 0, 0)
        layout.addWidget(about_button, 0, 1)
        layout.addWidget(label, 1, 0, 1, 2)

        self.setLayout(layout)
