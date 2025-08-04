import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QDockWidget, QApplication, QLabel, QVBoxLayout, QWidget


try:    # import if main.py is executed
    from .Toggletable import ToggleTable
    from .RIScontroller import RIScontroller
    from .rissimulator_ui import RISsimulator_ui
except ImportError:     # import if mainwindow.py is executed
    from lib.Toggletable import ToggleTable
    from lib.RIScontroller import RIScontroller
    from lib.rissimulator_ui import RISsimulator_ui


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # initialize QMainWindow
        self.centre = QMainWindow(self)
        self.centre.setWindowFlags(Qt.Widget)

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
        self.toggletable = ToggleTable(16,16,self.set_RISmask)
        self.ris_siumulator_ui = RISsimulator_ui()

        # configure table dock
        self.dock_toggletable.setWidget(self.toggletable)
        self.dock_toggletable.setFloating(False)
        self.dock_toggletable.topLevelChanged.connect(self.on_top_level_changed)
        self.centre.addDockWidget(Qt.LeftDockWidgetArea, self.dock_toggletable)

        # configure communication dock
        self.dock_ris_com.setWidget(self.ris_controller)
        self.dock_ris_com.setFloating(False)
        self.dock_ris_com.topLevelChanged.connect(self.on_top_level_changed)
        self.centre.addDockWidget(Qt.LeftDockWidgetArea, self.dock_ris_com)
        
        # configure simulation dock
        self.dock_ris_sim.setWidget(self.ris_siumulator_ui)
        self.dock_ris_sim.setFloating(False)
        self.dock_ris_sim.topLevelChanged.connect(self.on_top_level_changed)
        self.centre.addDockWidget(Qt.LeftDockWidgetArea, self.dock_ris_sim)

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

    def set_RISmask(self, mask):
        self.ris_controller.interface.set_pattern(mask)
        self.ris_siumulator_ui.set_mask_bool(mask)

    # TODO: dockwidget einfügen per funktion -> mehr übersicht -> weniger code doppelt
    # def add_dock(self, main_widget, dock_content, name):
    #     dock = QDockWidget(name, main_widget)
    #     dock.setWidget(dock_content)
    #     dock.setFloating(False)
    #     dock.topLevelChanged.connect()
    #     main_widget.addDockWidget(Qt.LeftDockWidgetArea, dock)



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
    window = MainWindow()
    window.setGeometry(500, 50, 600, 400)
    window.show()
    sys.exit(app.exec())