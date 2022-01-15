from src.ManagerGUI.ManagerGUI import ManagerGUI
from src.ModManager.ModManager import ModManager
from src.Logger.Logger import Logger

from PySide2.QtWidgets import QApplication
import sys


def test_basic():
    logger = Logger(logfile_name="test.log")
    manager = ModManager(logger=logger)
    manager.refresh()
    # manager.download_mod("TestMod")

    m1 = manager.get_mods()

    manager.add_filter_tag("Test")
    m2 = manager.get_mods()

    manager.set_filter_search("Test")
    m3 = manager.get_mods()

    manager.remove_filter_tag("Test")
    m4 = manager.get_mods()

    manager.add_filter_tag("Nothing")
    m5 = manager.get_mods()

    print([mod.display_name for mod in m1])
    print([mod.display_name for mod in m2])
    print([mod.display_name for mod in m3])
    print([mod.display_name for mod in m4])
    print([mod.display_name for mod in m5])


if __name__ == '__main__':
    app = QApplication(sys.argv)

    logger = Logger(logfile_name="latest.log", verbose=False)

    main_window = ManagerGUI(logger)

    main_window.show()

    sys.exit(app.exec_())
