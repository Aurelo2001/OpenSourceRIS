import os
os.environ["QT_API"] = "pyside6"

import sys
sys.path.append('.lib')
from typing import Literal

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QMainWindow, QDockWidget, QApplication, QLabel, QVBoxLayout, QWidget, QMenu, QHBoxLayout, QToolButton
from PySide6.QtGui import QShortcut, QKeySequence

from Table_widget.Table_widget import Table_widget
from measurement.measurement_ui import MeasurementWindow

import numpy as np


try:
    from controller import controller
except:
    from lib.controller import controller


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super(MainWindow, self).__init__()

        self._c = controller 
        # initialize QMainWindow
        self.central = QMainWindow(self)
        self.central.setWindowFlags(Qt.Widget)

        # configure options of QMainWindow's Docks
        self.central.setDockOptions(
            QMainWindow.AnimatedDocks |
            QMainWindow.AllowTabbedDocks
        )

        self.setCentralWidget(self.central)
        # Docks direkt an DIESES MainWindow hängen
        self.table = Table_widget(self._c, self)
        self.dock_table = self._make_dock("RIS control table", self.table)
        self.central.addDockWidget(Qt.LeftDockWidgetArea, self.dock_table)

        self.measure_config = MeasurementWindow(self._c, self)
        self.dock_measure = self._make_dock("Measurement settings", self.measure_config)
        self.central.addDockWidget(Qt.LeftDockWidgetArea, self.dock_measure)

        self.central.tabifyDockWidget(self.dock_table, self.dock_measure)
        self.dock_table.raise_()

        self.menuBar().addMenu("File").addAction("Quit", self.close)

    def _make_dock(self, title, widget):
        dock = QDockWidget(title, self.central)
        dock.setWidget(widget)
        dock.setFeatures(
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetClosable
        )
        dock.topLevelChanged.connect(self.on_top_level_changed)
        return dock

    @Slot(bool)
    def on_top_level_changed(self, floating):
        """Wenn das Dock-Fenster abgedockt wird (floating=True), Fenster-Buttons aktivieren"""
        dock = self.sender()
        if floating:
            # Fenster-Flags setzen: mit Min/Max/Schließen-Buttons
            dock.setWindowFlags(Qt.CustomizeWindowHint |
                                Qt.Window |
                                Qt.WindowMinimizeButtonHint |
                                Qt.WindowMaximizeButtonHint |
                                Qt.WindowCloseButtonHint)
            dock.show()  # Notwendig nach setWindowFlags()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    c = controller.main_controller()
    
    window = MainWindow(c)
    window.show()
    sys.exit(app.exec())





