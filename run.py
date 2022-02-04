from src.ManagerGUI.ManagerGUI import ManagerGUI
from src.Logger.Logger import Logger

from PySide2.QtWidgets import QApplication
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)

    logger = Logger(logfile_name="latest.log", verbose=False)

    main_window = ManagerGUI(logger)

    main_window.show()

    sys.exit(app.exec_())
