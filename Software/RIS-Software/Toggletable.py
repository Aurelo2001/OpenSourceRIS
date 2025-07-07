from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QMenu
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor


class ToggleTable(QTableWidget):
###############################################################################
##### init ####################################################################
###############################################################################
    def __init__(self, rows, cols, parent=None):
        super().__init__(rows, cols, parent)
        self.setWindowTitle("Farb-Toggle Table")
        self.resize(400, 300)
        self.init_table()
        # self.cellClicked.connect(self.toggle_cell)
        self.installEventFilter(self)

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


###############################################################################
##### state change functions ##################################################
###############################################################################

    # toggle clicked cell state between on/off
    def toggle_cell(self, row, col):
        item = self.item(row, col)
        current_state = item.data(Qt.UserRole)
        new_state = not current_state
        item.setData(Qt.UserRole, new_state)
        if new_state:
            item.setBackground(QColor("green"))
        else:
            item.setBackground(QColor("lightgray"))
        self.clearSelection()

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