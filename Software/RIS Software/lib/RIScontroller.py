import sys

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QObject, QEvent

import time

from RIScontroller_ui import RIScontroller_ui
from RISinterface import RISinterface

class RIScontroller(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = RIScontroller_ui()
        self.ui.setupUi(self)

        self.interface = RISinterface()
        self.debugoutput = bool(self.ui.CB_Debug.checkState())      # overwrites default to sync
        self.interface.setPort(self.ui.CB_port.currentText())       # overwrites default to sync

        self.ui.PB_connect.clicked.connect(self.wrap_connect)
        self.ui.PB_disconnect.clicked.connect(self.wrap_disconnect)
        self.ui.PB_readpattern.clicked.connect(self.wrap_readPattern)
        self.ui.PB_readserial.clicked.connect(self.wrap_readSerial)
        self.ui.PB_readVoltage.clicked.connect(self.wrap_readVoltage)
        self.ui.PB_reset.clicked.connect(self.wrap_reset)

        self.ui.CB_port.activated.connect(self.wrap_setPort)
        self.ui.CB_Debug.stateChanged.connect(self.setDebugOutput)

        self.ui.CB_port.popupAboutToBeShown.connect(self.wrap_updatePorts)


#### wrapper functions to print debug output in QTextEdit #########################################
    def wrap_connect(self):
        result, text = self.interface.connect()

        self.ui.PB_connect.setEnabled(not result)
        self.ui.PB_disconnect.setEnabled(result)

        self.ui.PB_reset.setEnabled(result)
        self.ui.PB_readVoltage.setEnabled(result)
        self.ui.PB_readpattern.setEnabled(result)
        self.ui.PB_readserial.setEnabled(result)

        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + text
            self.ui.TE_Debug.append(msg)
        return result


    def wrap_disconnect(self):
        result, text = self.interface.disconnect()

        self.ui.PB_connect.setEnabled(result)
        self.ui.PB_disconnect.setEnabled(not result)

        self.ui.PB_reset.setEnabled(not result)
        self.ui.PB_readVoltage.setEnabled(not result)
        self.ui.PB_readpattern.setEnabled(not result)
        self.ui.PB_readserial.setEnabled(not result)

        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + text
            self.ui.TE_Debug.append(msg)
        return result


    def wrap_readPattern(self):
        result, text = self.interface.get_pattern()

        if result:      # TODO: hex to matrix for printing
            text = text

        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + text
            self.ui.TE_Debug.append(msg)

        return True


    def wrap_readSerial(self):
        result, text = self.interface.get_serialnumber()
        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + text
            self.ui.TE_Debug.append(msg)
        return result


    def wrap_readVoltage(self):
        result, text = self.interface.get_extVoltage()
        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + text
            self.ui.TE_Debug.append(msg)
        return result


    def wrap_reset(self):
        result, text_list = self.interface.reset()
        if self.debugoutput:
            for text in text_list:
                msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] RIS-Rx: " + text
                self.ui.TE_Debug.append(msg)
        return result


    def wrap_setPort(self, index):
        result, text = self.interface.setPort(self.ui.CB_port.itemText(index))
        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + text
            self.ui.TE_Debug.append(msg)
        return result


    def wrap_updatePorts(self):
        result, ports = self.interface.get_available_ports()
        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + "update COM ports"
            self.ui.TE_Debug.append(msg)

        if result:
            self.ui.CB_port.blockSignals(True)
            self.ui.CB_port.clear()
            for port, desc, hwid in sorted(ports):
                self.ui.CB_port.addItem(port)
                print("{}: {} [{}]".format(port, desc, hwid))
            self.ui.CB_port.addItem("DEMO")
            self.ui.CB_port.blockSignals(False)

        return result


    def setDebugOutput(self, val):
        msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + "Debuggoutput {}".format("enabled" if val else "disabled")
        self.ui.TE_Debug.append(msg)
        self.debugoutput = val
        return val


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = RIScontroller()
    widget.show()
    sys.exit(app.exec())
