# This Python file uses the following encoding: utf-8
import sys
import serial
import numpy as np

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QGridLayout, QVBoxLayout, QMenu, QListWidget, QStyle, QHeaderView, QLabel
from PySide6.QtCore import QEvent
from PySide6.QtGui import QIcon

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

# import custom table class
from Toggletable import ToggleTable

from test import RISSimulatorSerial


###############################################################################
##### RIS controller ##########################################################
###############################################################################

class RIS_controller:
    def __init__(self):
        self.connected = False

###############################################################################
##### functions ###############################################################
###############################################################################

    def connect(self):
        if self.connected:
            return (True, "RIS already connected")
        else:
            self.ser = RISSimulatorSerial(  # TODO: replace test class with seriel.Serial
                # port='COM7',
                # baudrate=9600,
                # bytesize=8,
                # stopbits=serial.STOPBITS_ONE
                )
            if self.ser.isOpen():
                self.connected = True
                return (True, "connection established")
            else:
                return (False, "connection failed")

    def disconnect(self):
        if self.connected:      # wenn Verbindung besteht
            if self.ser.isOpen():
                self.ser.close()
            self.connected = False
            return (True, "RIS disconnected")
        else:                   # wenn keine verbindung besteht
            return (True, "No RIS connected")
        return (False, "Error: disconnection Failed")

    def set_pattern(self, state_matrix:list[list[int]]):

        bit_list = [int(value) for row in state_matrix for value in row]
        bit_string = "".join(map(str,bit_list))
        bit_int = int(bit_string, 2)
        tx_str = f"!{bit_int:#0{66}x}\n"

        self.ser.write(tx_str.encode())
        # TODO: timeout
        try:
            rx_msg = self.ser.readline(1)
        except:
            rx_msg = ""

        if rx_msg.decode() == "#OK\n":
            return True
        else:
            return False

    # TODO: not implemented
    def get_pattern(self):
        return

    # TODO: not implemented
    def get_extVoltage(self):
        return

    # TODO: not implemented
    def reset(self):
        self.ser.write("!Reset".encode())
        return


###############################################################################


###############################################################################
##### Mainwindow ##############################################################
###############################################################################
class MainWindow(QMainWindow):
    def __init__(self, controller: RIS_controller, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.RIS_controller = controller

        # init RIS tab
        self.ui.RIS_tab.setLayout(QVBoxLayout())

        self.ristable = ToggleTable(16,16, self.RIS_controller.set_pattern)
        self.ristable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ristable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.RIS_tab.layout().addWidget(self.ristable)

        # init statusbar
        self.statbar = self.statusBar()
        self.statbarMsgtime = 3000
        self.Lable_connected = QLabel("RIS: disconnected")
        self.statbar.setStyleSheet("""
            QStatusBar {
                background-color: #f0f0f0;
                color: #333;
                border-top: 1px solid #ccc;
                padding: 4px;
            }
            QStatusBar QLabel {
            }
        """)
        self.statbar.addPermanentWidget(self.Lable_connected)

        self.ristable.setStatusBarObject(self.statbar)

        # init controll tab
        self.ui.PB_connect.clicked.connect(self.PB_connect_func)
        self.ui.PB_disconnect.clicked.connect(self.PB_disconnect_func)


    def PB_connect_func(self):
        res, msg = self.RIS_controller.connect()
        if res:
            self.statbar.showMessage(msg, self.statbarMsgtime)
            self.Lable_connected.setText("RIS: connected")
            self.ui.PB_connect.setEnabled(False)
            self.ui.PB_disconnect.setEnabled(True)
        else:
            self.statbar.showMessage(msg, self.statbarMsgtime)
            self.Lable_connected.setText("RIS: disconnected")
            self.Lable_connected.setText("RIS: disconnected")
            self.ui.PB_connect.setEnabled(True)
            self.ui.PB_disconnect.setEnabled(False)


    def PB_disconnect_func(self):
        res, msg = self.RIS_controller.disconnect()
        if res:
            self.statbar.showMessage(msg, self.statbarMsgtime)
            self.Lable_connected.setText("RIS: disconnected")
            self.ui.PB_connect.setEnabled(True)
            self.ui.PB_disconnect.setEnabled(False)
        else:
            self.statbar.showMessage(msg, self.statbarMsgtime)

###############################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = RIS_controller()

    # print(controller.ser.write("?pattern".encode("ascii")))

    widget = MainWindow(controller)

    widget.show()

    sys.exit(app.exec())
