from src.Mod.Mod import Mod

from PySide2 import QtCore, QtWidgets, QtGui


class InstalledModWidget(QtWidgets.QFrame):
    """
    Framed widget that holds and displays an installed Mod's info for use in Qt's list widget.
    """
    def __init__(self, mod: Mod, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QtCore.Qt.SolidLine)

        self.mod = mod

        self.setToolTip(self.mod.display_name)

        self.setup_widget()

    def setup_widget(self) -> None:
        """
        Sets up the widget representation; adding the labels and download button.
        """
        layout = QtWidgets.QGridLayout()

        update_button = QtWidgets.QPushButton(self)
        update_button.setText("Update")
        update_button.setDisabled(True)
        uninstall_button = QtWidgets.QPushButton(self)
        uninstall_button.setText("Uninstall")

        name_label = QtWidgets.QLabel(self)
        name_label.setText(self.mod.display_name)

        tags_label = QtWidgets.QLabel(self)
        tags_label.setStyleSheet("QLabel {color: #006994}")
        tags_label.setText(str(", ".join(self.mod.tags)))

        update_button.clicked.connect(lambda: self.parent().mod_manager.update_mod(self.mod.id))
        uninstall_button.clicked.connect(lambda: self.parent().mod_manager.uninstall_mod(self.mod.id))

        layout.addWidget(name_label, 0, 0, 1, 2)
        layout.addWidget(tags_label, 1, 0, 1, 2)
        layout.addWidget(update_button, 2, 0, 1, 1)
        layout.addWidget(uninstall_button, 2, 0, 1, 1)

        self.setLayout(layout)

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
