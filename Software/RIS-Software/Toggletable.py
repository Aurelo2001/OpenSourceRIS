from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QMenu
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor


class ToggleTable(QTableWidget):
###############################################################################
##### init ####################################################################
###############################################################################
    def __init__(self, rows, cols, RIS_controler_update_func, parent=None):
        super().__init__(rows, cols, parent)
        self.setWindowTitle("Farb-Toggle Table")
        self.resize(400, 300)
        self.init_table()
        self.installEventFilter(self)
        self.RIS_controler_update_func = RIS_controler_update_func

    def init_table(self):
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = QTableWidgetItem()
                # Unsichtbare Checkbox (als interner Status)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setData(Qt.UserRole, False)  # unser eigener Status: False = Aus
                item.setBackground(QColor("lightgray"))
                item.setText(str(row*16+col+1))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, col, item)

    def setStatusBarObject(self, StatusBar):
        self.statusbar = StatusBar

###############################################################################
##### state change functions ##################################################
###############################################################################

    # set state of all selected items to specific state or toggle each
    def set_selected_state(self, state:bool=None):

        for item in self.selectedItems():
            current_state = item.data(Qt.UserRole)
            new_state = not current_state

            if state is not None:   # toggle current state or set specific state
                new_state = state
            if new_state:
                item.setBackground(QColor("green"))
            else:
                item.setBackground(QColor("lightgray"))

            item.setData(Qt.UserRole, new_state)
            self.clearSelection()
        self.update_ris()

    def update_ris(self):
        state_matrix = [[int(self.item(row,col).data(Qt.UserRole)) for col in range(self.columnCount())] for row in range(self.rowCount())]
        if self.RIS_controler_update_func(state_matrix):
            try:
                self.statusbar
            except AttributeError:
                print("Warning: statusbar unknows, no message shown")
                pass
            else:
                self.statusbar.showMessage("RIS sucsessfully updated", 2000)
            return True
        return False


###############################################################################
##### event filter for context menu ###########################################
###############################################################################
    def eventFilter(self, object, event):
        def all_on():
            self.set_selected_state(True)
        def all_off():
            self.set_selected_state(False)
        def toggle():
            self.set_selected_state()

        if event.type() == QEvent.ContextMenu:

            txt_on,txt_off,txt_invert = "ON","OFF","invert"

            menu = QMenu()
            menu.addAction(txt_on, all_on)
            menu.addAction(txt_off, all_off)
            menu.addAction(txt_invert, toggle)

            menu.exec(event.globalPos())

            return True
        return super().eventFilter(object, event)