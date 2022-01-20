from src.Mod.Mod import Mod

from PySide2 import QtCore, QtWidgets, QtGui


class InstalledModWidget(QtWidgets.QFrame):
    """
    Framed widget that holds and displays an installed Mod's info for use in Qt's list widget.
    """
    def __init__(self, mod: Mod, mod_manager, parent=None):
        """
        :param mod: Mod to base the widget off of.
        :param parent: Parent Qt Object/Widget
        """
        super().__init__(parent)
        self.setFrameStyle(QtCore.Qt.SolidLine)

        self.mod = mod
        self.mod_manager = mod_manager

        self.update_button = None
        self.uninstall_button = None

        self.setToolTip(self.mod.display_name)

        self.setup_widget()

    def setup_widget(self) -> None:
        """
        Sets up the widget representation; adding the labels and download button.
        """
        layout = QtWidgets.QGridLayout()

        self.update_button = QtWidgets.QPushButton(self)
        self.update_button.setText("Update")
        self.update_button.setDisabled(True)
        self.uninstall_button = QtWidgets.QPushButton(self)
        self.uninstall_button.setText("Uninstall")

        name_label = QtWidgets.QLabel(self)
        name_label.setText(self.mod.display_name)

        tags_label = QtWidgets.QLabel(self)
        tags_label.setStyleSheet("QLabel {color: #006994}")
        tags_label.setText(str(", ".join(self.mod.tags)))

        self.update_button.clicked.connect(self.update_mod)
        self.uninstall_button.clicked.connect(self.uninstall_mod)

        layout.addWidget(name_label, 0, 0, 1, 2)
        layout.addWidget(tags_label, 1, 0, 1, 2)
        layout.addWidget(self.update_button, 2, 0, 1, 1)
        layout.addWidget(self.uninstall_button, 2, 1, 1, 1)

        self.setLayout(layout)

        self.refresh_buttons()

    def refresh_buttons(self):
        if self.mod.update_available:
            self.update_button.setDisabled(False)
        else:
            self.update_button.setDisabled(True)

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

    def uninstall_mod(self):
        self.mod_manager.uninstall_mod(self.mod.id)
        self.refresh_list()

    def update_mod(self):
        self.mod_manager.uninstall_mod(self.mod.id)
        self.mod_manager.update_mod(self.mod.id, update_install=True)
        self.refresh_list()

    def refresh_list(self):
        self.parent().parent().refresh_list()
