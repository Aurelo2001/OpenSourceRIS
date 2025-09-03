from __future__ import annotations
import os
os.environ["QT_API"] = "pyside6"
from typing import Tuple
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QDoubleSpinBox, QSpinBox, QComboBox,
    QSizePolicy, QSpacerItem, QStatusBar, QMenuBar, QFrame, QCheckBox, QStackedWidget, QTabWidget
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Signal, Qt
import sys

from lib.measurement.presets import presets

# helper ------------------------------------------------------------------------------------------
def _make_row_frame(parent: QWidget) -> Tuple[QFrame, QHBoxLayout]:
    """Erzeugt einen flachen QFrame + HBox für eine Standard-Zeile."""
    frame = QFrame(parent)
    size_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
    frame.setSizePolicy(size_pol)
    frame.setMinimumHeight(20)
    frame.setMaximumHeight(20)

    h = QHBoxLayout(frame)
    h.setContentsMargins(-1, 0, -1, 0)
    return frame, h

def _make_row_double(
    parent: QWidget,
    label_text: str,
    suffix: str,
    minimum: float | None,
    maximum: float | None,
    value: float | None,
    tooltip: str | None = None,
    decimals: int = 2,
    single_step: float | None = None,
) -> Tuple[QFrame, QDoubleSpinBox]:
    """Zeile mit QLabel links + QDoubleSpinBox rechts + Expander dazwischen."""
    frame, h = _make_row_frame(parent)

    lbl = QLabel(label_text, frame)
    h.addWidget(lbl)

    h.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    spn = QDoubleSpinBox(frame)
    spn.setMinimumWidth(80)
    spn.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
    spn.setDecimals(decimals)
    if minimum is not None:
        spn.setMinimum(minimum)
    if maximum is not None:
        spn.setMaximum(maximum)
    if value is not None:
        spn.setValue(value)
    spn.setSuffix(suffix)
    if single_step is not None:
        spn.setSingleStep(single_step)
    if tooltip:
        frame.setToolTip(tooltip)

    h.addWidget(spn)
    return frame, spn

def _make_row_int(
    parent: QWidget,
    label_text: str,
    minimum: int | None,
    maximum: int | None,
    value: int | None,
    tooltip: str | None = None,
) -> Tuple[QFrame, QSpinBox]:
    """Zeile mit QLabel links + QSpinBox rechts + Expander dazwischen."""
    frame, h = _make_row_frame(parent)

    lbl = QLabel(label_text, frame)
    h.addWidget(lbl)
    h.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    spn = QSpinBox(frame)
    spn.setMinimumWidth(80)
    spn.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
    if minimum is not None:
        spn.setMinimum(minimum)
    if maximum is not None:
        spn.setMaximum(maximum)
    if value is not None:
        spn.setValue(value)
    if tooltip:
        frame.setToolTip(tooltip)

    h.addWidget(spn)
    return frame, spn

def _make_row_combo(
    parent: QWidget,
    label_text: str,
    items: list[str],
    tooltip: str | None = None,
    current_text: str | None = None,
    item_tooltip: list[str] | None = None,
) -> Tuple[QFrame, QComboBox]:
    """Zeile mit QLabel links + QComboBox rechts + Expander dazwischen."""
    frame, h = _make_row_frame(parent)

    lbl = QLabel(label_text, frame)
    h.addWidget(lbl)
    h.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    cmb = QComboBox(frame)
    cmb.setMinimumWidth(80)
    cmb.addItems(items)
    if current_text:
        cmb.setCurrentText(current_text)
    if tooltip:
        frame.setToolTip(tooltip)

    if item_tooltip:
        for idx, tooltip in enumerate(item_tooltip):
            cmb.setItemData(idx, tooltip, Qt.ToolTipRole)

    h.addWidget(cmb)
    return frame, cmb

# ui ----------------------------------------------------------------------------------------------

class Measurement_config_GB(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Measurement parameters", parent)
        self.setMaximumWidth(250)

        vbox = QVBoxLayout(self)

        # Preset
        self.gb_preset = GB_preset(parent=self)
        vbox.addWidget(self.gb_preset)

        # Frequency
        self.gb_freq = QGroupBox("Frequency", parent=self)
        freq_layout = QVBoxLayout(self.gb_freq)
        self.tab_freq = QTabWidget(parent=self.gb_freq)
        self.tab_freq.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.gb_freq_single = GB_freq_single()
        self.tab_freq.addTab(self.gb_freq_single, "point")
        self.gb_freq_sweep = GB_freq_sweep()
        self.tab_freq.addTab(self.gb_freq_sweep, "sweep")
        freq_layout.addWidget(self.tab_freq)
        vbox.addWidget(self.gb_freq)

        # Rotation
        self.gb_rot = QGroupBox("Rotation", parent=self)
        rot_layout = QVBoxLayout(self.gb_rot)
        self.tab_rot = QTabWidget(parent=self.gb_rot)
        self.tab_rot.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.gb_rot_single = GB_rotation_single()
        self.tab_rot.addTab(self.gb_rot_single, "point")
        self.gb_rot_sweep = GB_rotation_sweep()
        self.tab_rot.addTab(self.gb_rot_sweep, "sweep")
        rot_layout.addWidget(self.tab_rot)
        vbox.addWidget(self.gb_rot)

        # VNA
        self.gb_vna = GB_vna(parent=self)
        vbox.addWidget(self.gb_vna)

        # Spacer (füllt Resthöhe)
        vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Start-Button
        self.btn_start = QPushButton("start measurement", self)
        vbox.addWidget(self.btn_start)



# build classes for different panels --------------------------------------------------------------

class GB_preset(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Preset", parent)
        grid = QGridLayout(self)
        
        # 1) toggle preset
        self.preset_checkbox = QCheckBox(
            parent = self,
            text = "Use VNA Preset",
        )
        self.preset_checkbox.setChecked(True)
        grid.addWidget(self.preset_checkbox, 0, 0, 1, 1)
        
        # 2) preset selection
        self.preset_frame, self.cmb_preset = _make_row_combo(
            parent=self,
            label_text="Preset:",
            items=[preset["name"] for preset in presets],
            tooltip="Used preset in VNA",
            current_text="Single Freq & Position",
            item_tooltip=[preset["description"] for preset in presets],
        )
        grid.addWidget(self.preset_frame, 1, 0, 1, 1)

#------------------------------------------------------------------------------

class GB_freq_sweep(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        grid = QGridLayout(self)
        # 1) Start
        self.freq_start_frame, self.spn_freq_start = _make_row_double(
            parent=self,
            label_text="Start:",
            suffix="MHz",
            minimum=0.009,
            maximum=8500.0,
            value=5150.0,
            decimals=2,
            tooltip="Start frequency of the measurement"
        )
        grid.addWidget(self.freq_start_frame, 0, 0, 1, 1)
        # 2) Stop
        self.freq_stop_frame, self.spn_freq_stop = _make_row_double(
            parent=self,
            label_text="Stop:",
            suffix="MHz",
            minimum=0.009,
            maximum=8500.0,
            value=5875.0,
            decimals=2,
            tooltip="Stop frequency of the measurement"
        )
        grid.addWidget(self.freq_stop_frame, 2, 0, 1, 1)
        # 3) IF bandwidth
        self.freq_stepsize_frame, self.spn_if_bw = _make_row_double(
            parent=self,
            label_text="IF bandwidth:",
            suffix="kHz",
            minimum=0.001,
            maximum=10.0,
            value=0.1,
            decimals=3,
            tooltip="Controls measurement speed vs. noise: narrower is cleaner, wider is faster."
        )
        grid.addWidget(self.freq_stepsize_frame, 5, 0, 1, 1)
        # 4) Points
        self.vna_points_frame, self.spn_points = _make_row_int(
            parent=self,
            label_text="Points:",
            minimum=101,
            maximum=10001,
            value=401,
            tooltip="Controls frequency resolution vs. sweep time: more points = finer, slower."
        )
        grid.addWidget(self.vna_points_frame, 6, 0, 1, 1)

class GB_freq_single(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        grid = QGridLayout(self)
        # 1) Start
        self.freq_frame, self.spn_freq = _make_row_double(
            parent=self,
            label_text="Freqeuncy:",
            suffix="MHz",
            minimum=0.009,
            maximum=8500.0,
            value=5150.0,
            decimals=2,
            tooltip="Frequency of the measurement"
        )
        grid.addWidget(self.freq_frame, 1, 0, 1, 1)

#------------------------------------------------------------------------------

class GB_rotation_sweep(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        grid = QGridLayout(self)
        # Start °
        self.rotation_start_frame, self.spn_rot_start = _make_row_double(
            parent=self,
            label_text="Start:", suffix="°", minimum=0.0, maximum=360.0,
            value=0.0, tooltip="Start angle of the messurement", decimals=0
        )
        grid.addWidget(self.rotation_start_frame, 0, 0, 1, 1)
        # Stop °
        self.rotation_stop_frame, self.spn_rot_stop = _make_row_double(
            parent=self,
            label_text="Stop:", suffix="°", minimum=0.0, maximum=360.0,
            value=180.0, tooltip="Stop angle of the messurement", decimals=0
        )
        grid.addWidget(self.rotation_stop_frame, 2, 0, 1, 1)
        # Stepsize °
        self.rotation_stepsize_frame, self.spn_rot_step = _make_row_double(
            parent=self,
            label_text="Stepsize:", suffix="°", minimum=0.1, maximum=180.0,
            value=1.0, tooltip="Stepsize for the rotation", decimals=1, single_step=0.1
        )
        grid.addWidget(self.rotation_stepsize_frame, 3, 0, 1, 1)

class GB_rotation_single(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        grid = QGridLayout(self)
        self.rotation_frame, self.spn_rot = _make_row_double(
            parent=self,
            label_text="Start:", suffix="°", minimum=0.0, maximum=360.0,
            value=0.0, tooltip="Start angle of the messurement", decimals=0
        )
        grid.addWidget(self.rotation_frame, 1, 0, 1, 1)

#------------------------------------------------------------------------------

class GB_vna(QGroupBox):
    def __init__(self, title="VNA", parent=None):
        super().__init__(title, parent)
        grid = QGridLayout(self)
        # Tx
        self.vna_tx_frame, self.cmb_tx = _make_row_combo(
            parent=self,
            label_text="Tx:",
            items=["Port1", "Port2", "Port3", "Port4"],
            tooltip="Used port for transmitting antenna",
            current_text="Port2",
        )
        grid.addWidget(self.vna_tx_frame, 0, 0, 1, 1)
        # Rx
        self.vna_rx_frame, self.cmb_rx = _make_row_combo(
            parent=self,
            label_text="Rx:",
            items=["Port1", "Port2", "Port3", "Port4"],
            tooltip="Used port for recriving antenna",
            current_text="Port1",
        )
        grid.addWidget(self.vna_rx_frame, 1, 0, 1, 1)
        # Tx Power
        self.vna_txpower_frame, self.spn_tx_power = _make_row_double(
            parent=self,
            label_text="Tx Power:", suffix="dBm", minimum=-100.0, maximum=27.0,
            value=-20.0, tooltip="Used transmit power for this measurement", decimals=0
        )
        grid.addWidget(self.vna_txpower_frame, 2, 0, 1, 1)



# start as standalone -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    w = QMainWindow()
    
    w.setCentralWidget(Measurement_config_GB(w))
    w.show()
    
    sys.exit(app.exec())