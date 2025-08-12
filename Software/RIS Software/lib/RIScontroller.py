import sys
sys.path.append("./")

from PySide6.QtWidgets import QApplication, QWidget

import time

from lib.RIScontroller_ui import RIScontroller_ui
from lib.RISinterface import RISinterface

class RIScontroller(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = RIScontroller_ui()
        self.ui.setupUi(self)

        self.interface = RISinterface()
        self.debugoutput = bool(self.ui.CB_Debug.checkState())      # overwrites default to sync

        self.wrap_updatePorts()
        self.ui.CB_port.setCurrentIndex(0)

        self.interface.set_Port(self.ui.CB_port.currentText())       # overwrites default to sync

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
        self.ui.CB_port.setEnabled(not result)
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
        self.ui.CB_port.setEnabled(result)
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
        result, text = self.interface.read_pattern()

        if result:      # TODO: hex to matrix for printing
            text = text
            pattern = self.mask_print_bool(text)
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] currently set pattern:\n          " + pattern.replace("\n","\n          ")
            self.ui.TE_Debug.append(msg)

        # if self.debugoutput:
        #     msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + text
        #     self.ui.TE_Debug.append(msg)

        return True


    def wrap_readSerial(self):
        result, text = self.interface.read_serialnumber()
        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + text
            self.ui.TE_Debug.append(msg)
        return result


    def wrap_readVoltage(self):
        result, text = self.interface.read_extVoltage()
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
        result, text = self.interface.set_Port(self.ui.CB_port.itemText(index))
        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + text
            self.ui.TE_Debug.append(msg)
        return result


    def wrap_updatePorts(self):
        result, ports = self.interface.get_RIS_devices()
        if self.debugoutput:
            msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + "update COM ports"
            self.ui.TE_Debug.append(msg)

        if result:
            self.ui.CB_port.blockSignals(True)
            self.ui.CB_port.clear()
            for port, desc, hwid in sorted(ports):
                self.ui.CB_port.addItem(port)
                # print("{}: {} [{}]".format(port, desc, hwid))
            self.ui.CB_port.addItem("DEMO")
            self.ui.CB_port.blockSignals(False)
            self.ui.CB_port.setCurrentIndex(0)

        return result


    def setDebugOutput(self, val):
        msg = "[" + time.strftime("%H:%M:%S", time.localtime()) + "] " + "Debuggoutput {}".format("enabled" if val else "disabled")
        self.ui.TE_Debug.append(msg)
        self.debugoutput = val
        return val


    def mask_print_bool(self, pattern):
        """
        Gibt das aktuelle Aktivitätsmuster des RIS als Textgrafik aus.
        ░░░ = inaktiv, ███ = aktiv
        """
        # Schritt 1: Hex-String in Binär-String konvertieren (256 Bits, also 64 * 4)
        binary_string = bin(int(pattern, 16))[2:].zfill(256)

        # Schritt 2: In eine 16x16 Liste umwandeln
        bit_matrix = [
            [int(bit) for bit in binary_string[i * 16:(i + 1) * 16]]
            for i in range(16)
        ]
        # for row in self.element_mask:
        line = ""
        for row in bit_matrix:
            for active in row:
                line += "███ " if active else "░░░ "
            line += "\n"
        return line

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = RIScontroller()
    widget.show()
    sys.exit(app.exec())
