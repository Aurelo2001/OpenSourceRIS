# This Python file uses the following encoding: utf-8
import sys
import serial
import numpy as np

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QGridLayout, QVBoxLayout, QMenu, QListWidget, QStyle, QHeaderView
from PySide6.QtCore import QEvent
from PySide6.QtGui import QIcon

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

# import custom table class
from Toggletable import ToggleTable


###############################################################################
##### Mainwindow ##############################################################
###############################################################################

class MainWindow(QMainWindow):
    def __init__(self, RIS_controller, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.RIS_controller = RIS_controller

        self.ui.RIS_tab.setLayout(QVBoxLayout())
        self.ristable = ToggleTable(16,16)

        self.ui.RIS_tab.layout().addWidget(self.ristable)

        self.ristable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ristable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)


###############################################################################
##### RIS controller ##########################################################
###############################################################################

class RIS_controller:
    def __init__(self):
        # self.s = serial.Serial(
        #     port='COM7',
        #     baudrate=9600,
        #     bytesize=8,
        #     stopbits=serial.STOPBITS_ONE)
        # if self.s.isOpen():
        #     print("Serial Port opend")
        # else:
        #     print("Error: Serial Port failed to open")
        return


##### comunication ############################################################

    def set_pattern(self, ris_matrix=[]):

        if ris_matrix == []:
            ris_matrix = [[btn.state for btn in row] for row in self.ris_matrix]

        ris_matrix = [[btn.state for btn in row] for row in self.ris_matrix] # hotfix

        bit_list = [int(value) for row in ris_matrix for value in row]
        bit_string = "".join(map(str,bit_list))
        bit_int = int(bit_string, 2)
        hex_val = hex(bit_int)

        tx_str = "!"+str(hex_val)+"\n"

        print(tx_str)

        # self.s.write(tx_str)
        # TODO: timeout
        try:
            rx_msg = self.s.readline()
        except:
            rx_msg = ""

        return rx_msg


    # TODO: not implemented
    def get_pattern(self):
        return

    # TODO: not implemented
    def get_extVoltage(self):
        return

    # TODO: not implemented
    def reset(self):
        self.s.write("!Reset")
        return


###############################################################################


###############################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = RIS_controller()

    widget = MainWindow(controller)

    widget.show()

    sys.exit(app.exec())
