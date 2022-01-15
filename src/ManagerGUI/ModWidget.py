from PySide2 import QtCore, QtWidgets, QtGui
from src.Mod.Mod import Mod


class ModWidget(QtWidgets.QFrame):
    """
    Framed widget that holds and displays a Mod's info for use in Qt's list widget.
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

        download_button = QtWidgets.QPushButton(self)
        download_button.setText("Download")
        name_label = QtWidgets.QLabel(self)
        name_label.setText(self.mod.display_name)
        tags_label = QtWidgets.QLabel(self)
        tags_label.setStyleSheet("QLabel {color: #e9a576}")
        tags_label.setText(str(", ".join(self.mod.tags)))

        download_button.clicked.connect(lambda: self.mod.download())
        # TODO: replace with lambda call to mod manager through parent.

        layout.addWidget(name_label, 0, 0)
        layout.addWidget(tags_label, 1, 0)
        layout.addWidget(download_button, 2, 0)

        self.setLayout(layout)

    def get_display_text(self) -> str:
        """
        Generates the text to display in the mod info widget when selected.
        :return: The text to display.
        """
        text = \
            f"""
{self.mod.display_name} ({self.mod.id})

{", ".join(self.mod.tags)}

{self.mod.description}


Author: {self.mod.author}
Version: {self.mod.version}
Made for game version: {self.mod.game_version}
Made for UMM version: {self.mod.manager_version}
            """

        return text