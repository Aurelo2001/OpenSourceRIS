import os
os.environ["QT_API"] = "pyside6"

import sys
sys.path.append("./lib")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot, QThread

from lib.main_window import mainwindow
from lib.controller import controller


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # c_thread = QThread()              # controler currently not threadsave
    c = controller.main_controller()
    # c.moveToThread(c_thread)
    # c_thread.start()

    w = mainwindow.MainWindow(c)

    c.start_measurement.connect(w.table.lock)
    c.stop_measurement.connect(w.table.unlock)

    w.measure_config.measure.connect(c.measure)

    w.show()
    sys.exit(app.exec())