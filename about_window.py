import os
import logging

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap


# the about window is used to display program information to the user


class About_Window(QtWidgets.QMainWindow):

    # init the window
    def __init__(self):
        super(About_Window, self).__init__()

        # get the base path to where the source is.
        # this path is different when compiled
        __PROGRAM_NAME__ = "JDx Display App"
        __VERSION__ = "1.0.0"
        __AUTHOR__ = "Lucas Jameson"

        try:

            ui_file = os.path.join("about.ui")

            uic.loadUi(ui_file, self)

        except Exception as e:
            logging.warning(e)
            return

        # find the children and set them accordingly

        self.program_la = self.findChild(QtWidgets.QLabel, "program_la")
        self.version_la = self.findChild(QtWidgets.QLabel, "version_la")
        self.author_la = self.findChild(QtWidgets.QLabel, "author_la")
        self.logo_la = self.findChild(QtWidgets.QLabel, "logo_la")

        self.program_la.setText(f"Program: {__PROGRAM_NAME__}")
        self.version_la.setText(f"Version: {__VERSION__}")
        self.author_la.setText(f"Author: {__AUTHOR__}")

        logo_source = "Jewell_Instruments_Logo.jpg"

        image = QPixmap(logo_source)
        self.logo_la.setPixmap(image)
