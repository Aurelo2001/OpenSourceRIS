import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QMainWindow, QDockWidget, QApplication, QLabel, QVBoxLayout, QWidget


try:    # import if main.py is executed
    from .Toggletable import ToggleTable
    from .RIScontroller import RIScontroller
except ImportError:     # import if mainwindow.py is executed
    from Toggletable import ToggleTable
    from RIScontroller import RIScontroller


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # initialize QMainWindow
        self.centre = QMainWindow(self)
        self.centre.setWindowFlags(QtCore.Qt.Widget)

        # configure options of QMainWindow's Docks
        self.centre.setDockOptions(
            QMainWindow.AnimatedDocks |
            QMainWindow.AllowTabbedDocks
        )

        self.setCentralWidget(self.centre)

        # add a QDockWidget for each Widget
        self.dock_toggletable = QDockWidget('RIS', self.centre)
        self.dock_ris_com = QDockWidget('Kommunication', self.centre)
        self.dock_ris_sim    = QDockWidget('Simulation',      self.centre)

        # initialise Widgets for the QDockWidgets
        self.ris_controller = RIScontroller()
        self.toggletable = ToggleTable(16,16,self.ris_controller.interface.set_pattern)
        # TODO self.ris_siumulator = RISsimulator()

        # configure table dock
        self.dock_toggletable.setWidget(self.toggletable)
        self.centre.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_toggletable)

        # configure communication dock
        self.dock_ris_com.setWidget(self.ris_controller)
        self.centre.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_ris_com)
        
        # configure simulation dock
        self.dock_ris_sim.setWidget(QLabel("not jet implemented",alignment=QtCore.Qt.AlignCenter))  # TODO: replace QLable witch self.ris_siumulator
        self.centre.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_ris_sim)

        # stack all docks in MainWindow
        self.centre.tabifyDockWidget(self.dock_toggletable, self.dock_ris_com)
        self.centre.tabifyDockWidget(self.dock_ris_com, self.dock_ris_sim)

        # set shown dock when first opend
        self.dock_ris_com.raise_()

        # add menu with "Quit"
        self.menuBar().addMenu('File').addAction('Quit', self.close)

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
        self.setStatusBar(self.statbar)
        self.toggletable.setStatusBarObject(self.statbar)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(500, 50, 600, 400)
    window.show()
    sys.exit(app.exec())