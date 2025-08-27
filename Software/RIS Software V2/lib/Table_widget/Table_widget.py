import os
os.environ["QT_API"] = "pyside6"
import sys
sys.path.append('.\\lib')
from typing import Literal

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QSizePolicy, QHeaderView, QApplication
from PySide6.QtCore import Qt, QEvent, QSize, Signal, Slot
from PySide6.QtGui import QColor, QShortcut, QKeySequence

import numpy as np
try:
    from controller import controller
except:
    from lib.controller import controller

class Table_widget(QTableWidget):

    # init ----------------------------------------------------------------------------------------
    def __init__(self, controller:controller.main_controller, parent=None):
        self._c = controller
        self._c.data.selected_pattern_changed.connect(self.set_pattern)
        self._c.data.selected_pattern_edited.connect(self.set_pattern)

        super().__init__(self._c.data.ris_row_count, self._c.data.ris_col_count, parent)

        self.unlock()

        self.setWindowTitle("RIS pattern controll")

        # size and resizing parameters
        self.resize(800, 600)
        self.setMinimumSize(QSize(720, 480))
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # building table
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = QTableWidgetItem()
                # create an invisible checkbox that acts as a button with an internal status
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setData(Qt.UserRole, False)  # custom status: False = OFF
                item.setBackground(QColor("lightgray"))
                item.setText(str(row*(col+1)+col+1))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, col, item)

        self._setup_shortcuts()

        self.installEventFilter(self)

    @Slot()
    def lock(self):
        """Lock the table so user interaction is blocked."""
        self._locked = True
        # Auswahl komplett verhindern
        self.setSelectionMode(QTableWidget.NoSelection)
        # Optional: Kontextmenü deaktivieren
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.setToolTip("locked! measurement in progress")
        self.viewport().setCursor(Qt.ForbiddenCursor)

    @Slot()
    def unlock(self):
        """Unlock the table so user can interact again."""
        self._locked = False
        # Standard-Auswahl wieder aktivieren
        self.setSelectionMode(QTableWidget.ExtendedSelection)
        # Kontextmenü wieder zulassen
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.setToolTip("")
        self.viewport().unsetCursor()

    def is_locked(self) -> bool:
        return self._locked

    # create shortcuts ----------------------------------------------------------------------------
    def _setup_shortcuts(self) -> None:
        """
        Registriert unsichtbare Tastenkürzel (QShortcut) für diese Tabelle.
        Alle Shortcuts lösen Methoden der Klasse aus, ohne sichtbare UI-Elemente.
        """

        # Wichtig: Referenzen halten, damit die Shortcuts nicht vom GC eingesammelt werden.
        # (Falls du das objektorientierter willst, leg sie als Attribute an, z. B. self.sc_invert = ...)
        self._shortcuts: list[QShortcut] = []

        def add_sc(key: str, callback) -> None:
            def wrapper():
                if not self._locked:
                    callback()
            sc = QShortcut(QKeySequence(key), self)
            # Kontext:
            #   - WidgetShortcut: nur wenn dieses Widget Fokus hat
            #   - WindowShortcut: überall im Fenster
            #   - ApplicationShortcut: app-weit
            #   - WidgetWithChildrenShortcut: dieses Widget + Kinder (praktisch für QTableWidget)
            sc.setContext(Qt.WidgetWithChildrenShortcut)
            sc.activated.connect(wrapper)
            self._shortcuts.append(sc)

        # Alle Zellen schalten (nutzt deine neue apply_state_to_all-Methode)
        add_sc("Ctrl+Shift+I", lambda: self.set_pattern_all('invert'))
        add_sc("Ctrl+Shift+1", lambda: self.set_pattern_all('on'))
        add_sc("Ctrl+Shift+0", lambda: self.set_pattern_all('off'))

        # Beispiel: Debug-Ausgabe der aktuellen Pattern
        add_sc("Ctrl+Shift+R", lambda: self.set_pattern_random())



    # state change functions ----------------------------------------------------------------------

    @Slot(controller.RISpattern)
    def set_pattern(self, pattern:controller.RISpattern):
        self.clearSelection()
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                new_state = False if pattern.matrix[r][c]==0 else True
                self.item(r,c).setData(Qt.UserRole, new_state)
                self.item(r,c).setBackground(QColor("green") if new_state else QColor("lightgray"))

    def set_pattern_all(self, action:Literal["on", "off", "invert"]):
        if action not in ('on', 'off', 'invert'):
            raise ValueError("action must be one of: 'on', 'off', 'invert'")
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                if action == 'on':
                    new_state = True
                elif action == 'off':
                    new_state = False
                else:  # 'invert'
                    new_state = not self.item(r,c).data(Qt.UserRole)
                self.item(r,c).setData(Qt.UserRole, new_state)
                self.item(r,c).setBackground(QColor("green") if new_state else QColor("lightgray"))
        self.update_ris()

    def set_pattern_random(self):
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                new_state = bool(np.random.choice([0,1]))
                self.item(r,c).setData(Qt.UserRole, new_state)
                self.item(r,c).setBackground(QColor("green") if new_state else QColor("lightgray"))
        self.update_ris()

    # set state of all selected items to specific state or toggle each
    def set_selected_state(self, action:Literal["on", "off", "invert"]):
        if action not in ('on', 'off', 'invert'):
            raise ValueError("action must be one of: 'on', 'off', 'invert'")
        for item in self.selectedItems():
            current_state = item.data(Qt.UserRole)
            if action == 'on':
                new_state = True
            elif action == 'off':
                new_state = False
            else:  # 'invert'
                new_state = not current_state
            if new_state != current_state:
                item.setData(Qt.UserRole, new_state)
                item.setBackground(QColor("green") if new_state else QColor("lightgray"))
            self.clearSelection()
        self.update_ris()


    def update_ris(self):
        self._c.data.edit_selected(np.array([[int(self.item(row,col).data(Qt.UserRole)) for col in range(self.columnCount())] for row in range(self.rowCount())]))

    def get_pattern(self) -> controller.RISpattern:
        return controller.RISpattern(np.array([
            [int(self.item(r, c).data(Qt.UserRole)) for c in range(self.columnCount())]
            for r in range(self.rowCount())
        ], dtype=int))

###############################################################################
##### event filter for context menu ###########################################
###############################################################################
    def eventFilter(self, object, event):
        if self._locked:
            if event.type() in (QEvent.ContextMenu, QEvent.MouseButtonPress, QEvent.KeyPress):
                return True
        if event.type() == QEvent.ContextMenu:
            menu = QMenu()
            menu.addAction("ON",      lambda: self.set_selected_state("on"))
            menu.addAction("OFF",     lambda: self.set_selected_state("off"))
            menu.addAction("invert",  lambda: self.set_selected_state("invert"))
            menu.exec(event.globalPos())
            return True
        return super().eventFilter(object, event)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    
    c = controller.main_controller()
    w = Table_widget(c)

    w.show()

    sys.exit(app.exec())