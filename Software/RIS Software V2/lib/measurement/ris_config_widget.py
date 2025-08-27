from __future__ import annotations

import sys
sys.path.append('.\\lib')

from PySide6.QtWidgets import QApplication

from Table_widget import Table_widget

from controller import controller

"""
RIS Configuration Manager for PySide6
-------------------------------------

This module provides a drop-in QWidget that manages multiple RIS configurations
built on top of your existing `Table_widget` (matrix editor).

Features
- Bottom horizontal list of configurations with rectangular live previews only.
- Add, duplicate, delete configurations (buttons stacked vertically at left of the list).
- One large editable table that always reflects the *currently selected* config.
- Edits in the large table auto-sync back to the active configuration + preview.
"""

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout,
    QMessageBox, QSizePolicy
)


class RisConfigManager(QWidget):
    
    def __init__(self, controller:controller.main_controller, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("RIS Config Manager")
        self._c = controller
        self._c.data.pattern_added.connect(self._append_config)
        self._c.data.pattern_deleted.connect(self._update_patern_list)
        self._c.data.selected_pattern_edited.connect(self._selected_edited)
        # self._c.data.selected_pattern_changed.connect(self._on_list_selection_changed)
        
        self._current_uid: Optional[str] = None
        
        # Big table
        self.table = Table_widget.Table_widget(controller=self._c)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Horizontal list
        self.list = QListWidget()
        self.list.setViewMode(QListWidget.IconMode)
        self.list.setResizeMode(QListWidget.Adjust)
        self.list.setMovement(QListWidget.Static)
        self.list.setFlow(QListWidget.LeftToRight)
        self.list.setWrapping(False)
        self.list.setIconSize(QSize(self._c.data.ris_col_count * 6, self._c.data.ris_row_count * 4))
        self.list.setFixedHeight(self._c.data.ris_row_count * 4 + 30)
        self.list.currentItemChanged.connect(self._on_list_selection_changed)
        
        # Buttons stacked vertically on the left of the list
        self.btn_add = QPushButton("Add")
        self.btn_dup = QPushButton("Duplicate")
        self.btn_del = QPushButton("Delete")
        
        self.btn_add.clicked.connect(lambda: self._c.data.add_empty())
        self.btn_dup.clicked.connect(lambda: self._c.data.duplicate_selected())
        self.btn_del.clicked.connect(lambda: self._c.data.delet_pattern(self._c.data.get_selected_uid()))
        
        btn_col = QVBoxLayout()
        for b in (self.btn_add, self.btn_dup, self.btn_del):
            btn_col.addWidget(b)
        
        list_row = QHBoxLayout()
        list_row.addLayout(btn_col)
        list_row.addWidget(self.list)
        
        # Layout composition: vertical, table on top, list+buttons below
        root = QVBoxLayout(self)
        root.addWidget(self.table)
        root.addLayout(list_row)
        
        self._append_config(self._c.data.get_selected_pattern())
    
    #-------------------------------------------#
    def _update_patern_list(self):
        self.list.clear()
        self.list.blockSignals(True)
        for p in self._c.data.pattern:
            self._append_config(p)
        self.list.blockSignals(False)
    
    #-------------------------------------------#
    def _append_config(self, pattern: controller.RISpattern):
        item = QListWidgetItem()
        item.setData(Qt.UserRole, pattern.uid)
        item.setIcon(self._pixmap_icon(pattern.matrix))
        self.list.addItem(item)
        
        self.list.setCurrentItem(item)
    
    # #-------------------------------------------#
    # @Slot()
    # def add_empty(self):
    #     new_id = self._c.data.add_empty()
    #     self._append_config(new_id)
    
    #-------------------------------------------#
    @Slot()
    def delete_selected(self):
        row = self.list.currentRow()
        if row < 0:
            return
        reply = QMessageBox.question(self, "Delete configuration", "Remove the selected configuration?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        uid = self.list.item(row).data(Qt.UserRole)
        self.list.takeItem(row)
        if self.list.count():
            self.list.setCurrentRow(min(row, self.list.count() - 1))
        else:
            self._current_uid = None
            self.table.set_matrix(np.zeros((self._c.data.ris_row_count, self._c.data.ris_col_count), dtype=int))
    
    #-------------------------------------------#
    @Slot("QListWidgetItem*", "QListWidgetItem*")
    def _on_list_selection_changed(self, cur: QListWidgetItem | None, prev: QListWidgetItem | None):
        if cur is None:
            return
        uid = cur.data(Qt.UserRole)
        self._c.data.set_selected_pattern(uid)
        cfg = self._c.data.get_selected_pattern()
        if not cfg:
            return
        self.table.set_pattern(cfg)

    #-------------------------------------------#
    @Slot(np.ndarray)
    def _selected_edited(self, pattern: controller.RISpattern):
        row = self.list.currentRow()
        if row >= 0:
            self.list.item(row).setIcon(self._pixmap_icon(pattern.matrix))
    
    #-------------------------------------------#
    def _pixmap_icon(self, matrix: np.ndarray,
                    cell_w_px: int = 6, cell_h_px: int = 4) -> QPixmap:
        rows, cols = matrix.shape
        w, h = cols * cell_w_px, rows * cell_h_px
        pm = QPixmap(w, h)
        pm.fill(Qt.transparent)
        painter = QPainter(pm)
        try:
            for r in range(rows):
                for c in range(cols):
                    on = bool(matrix[r, c])
                    painter.fillRect(
                        c * cell_w_px,
                        r * cell_h_px,
                        cell_w_px,
                        cell_h_px,
                        QBrush(QColor("green") if on else QColor("lightgray")),
                    )
            pen = QPen(QColor("black"))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(0, 0, w - 1, h - 1)
        finally:
            painter.end()
        return pm
    
#-------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    app = QApplication(sys.argv)

    c = controller.main_controller()

    w = RisConfigManager(controller=c)
    w.show()
    sys.exit(app.exec())

