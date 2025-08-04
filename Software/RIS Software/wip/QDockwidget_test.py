from PySide6.QtWidgets import QMainWindow, QApplication, QDockWidget, QTextEdit
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Hauptinhalt
        self.setCentralWidget(QTextEdit("Hauptfenster"))

        # Dock-Widget erstellen
        self.dock = QDockWidget("Dock", self)
        self.dock.setWidget(QTextEdit("Andockbares Fenster"))
        self.dock.setFloating(False)

        # Signal verbinden
        self.dock.topLevelChanged.connect(self.on_top_level_changed)

        # Zum Fenster hinzufügen
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

    def on_top_level_changed(self, floating):
        """Wenn das Dock-Fenster abgedockt wird (floating=True), Fenster-Buttons aktivieren"""
        dock = self.sender()
        if floating:
            # Fenster-Flags setzen: mit Min/Max/Schließen-Buttons
            dock.setWindowFlags(Qt.CustomizeWindowHint |
                                Qt.Window |
                                Qt.WindowMinimizeButtonHint |
                                Qt.WindowMaximizeButtonHint |
                                Qt.WindowCloseButtonHint | 
                                Qt.Window)
            dock.show()  # Notwendig nach setWindowFlags()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec_())