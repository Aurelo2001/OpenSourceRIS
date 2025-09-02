from __future__ import annotations
import os
os.environ["QT_API"] = "pyside6"
from typing import Tuple
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QGroupBox, QLabel, QPushButton, QDoubleSpinBox, QSpinBox, QComboBox,
    QSizePolicy, QSpacerItem, QStatusBar, QMenuBar, QFrame, QCheckBox, QStackedWidget
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Signal, Qt
import sys
sys.path.append('.\\lib')

from controller import controller
from measurement.ris_config_widget import RisConfigManager
from presets import presets

#-------------------------------------------------------------------------------------------------#

class MeasurementWindow(QMainWindow):

    measure = Signal(controller.Measurement_config)
    preset_changed = Signal(int)

    def __init__(self, controller:controller.main_controller, parent=None) -> None:
        super().__init__(parent)
        
        self._c = controller
        
        self._c.stop_measurement.connect(QApplication.beep)
        self._c.measurement_msg.connect(lambda text: self.statusBar().showMessage(text, 3000))
        
        self.setWindowTitle("Measurement settings")
        self.resize(953, 600)

        central = QWidget(self)
        root_hbox = QHBoxLayout(central)
        self.setCentralWidget(central)

        left_panel = self.build_left_panel()
        root_hbox.addWidget(left_panel)

        ris_conf_widget = RisConfigManager(self._c, self)
        root_hbox.addWidget(ris_conf_widget)

        self.setMenuBar(QMenuBar(self))
        self.setStatusBar(QStatusBar(self))

        self.connect_signals()
        
        self.preset_checkbox.checkStateChanged.emit(Qt.CheckState.Checked)


    # Wire Signals --------------------------------------------------------------------------------
    def connect_signals(self) -> None:
        self.preset_checkbox.checkStateChanged.connect(self.preset_state)
        self.cmb_preset.activated.connect(self.preset_select)
        self.spn_freq_start.valueChanged.connect(self.validate_inputs)
        self.spn_freq_stop.valueChanged.connect(self.validate_inputs)
        self.spn_rot_start.valueChanged.connect(self.validate_inputs)
        self.spn_rot_stop.valueChanged.connect(self.validate_inputs)
        self.btn_start.clicked.connect(self.on_start_clicked)


    # Slots ---------------------------------------------------------------------------------------
    def preset_state(self, state:Qt.CheckState):
        state = bool(state.value)
        self.gb_freq.setEnabled(state)
        self.gb_rot.setEnabled(state)
        self.gb_vna.setEnabled(state)
        self.cmb_preset.activated.emit(self.cmb_preset.currentIndex())


    def preset_select(self, idx:int):
        if presets[idx]["single_freq"]:
            test = self.gb_freq.setPage()
        else:
            self.spn_freq_start.setValue(presets[idx]["freq_start_Hz"] * 1e-6)
            self.spn_freq_stop.setValue(presets[idx]["freq_stop_Hz"] * 1e-6)
            self.spn_if_bw.setValue(presets[idx]["if_bw_Hz"] * 1e-3)
            self.spn_points.setValue(presets[idx]["points"])
            
        if presets[idx]["single_rot"]:
            test = self.gb_rot.children()
        else:
            self.spn_rot_start.setValue(presets[idx]["rot_start_deg"])
            self.spn_rot_stop.setValue(presets[idx]["rot_stop_deg"])
            self.spn_rot_step.setValue(presets[idx]["rot_step_deg"])
        
        self.spn_tx_power.setValue(presets[idx]["power_tx_dBm"])
        self.cmb_tx.setCurrentIndex(presets[idx]["port_tx"])
        self.cmb_rx.setCurrentIndex(presets[idx]["port_rx"])
        self.preset_changed.emit(idx)


    def on_start_clicked(self) -> None:
        measurement_conf = controller.Measurement_config(
            freq_start_hz =     self.spn_freq_start.value()*1e6,
            freq_stop_hz =      self.spn_freq_stop.value()*1e6,
            if_bandwidth_hz =   self.spn_if_bw.value()*1e3,
            points =            self.spn_points.value(),
            ang_start_deg =     self.spn_rot_start.value(),
            ang_stop_deg =      self.spn_rot_stop.value(),
            ang_step_deg =      self.spn_rot_step.value(),
            power_dbm =         self.spn_tx_power.value(),
            )
        
        self.measure.emit(measurement_conf)
        self.statusBar().showMessage("Measurement started …", 1500)

    def validate_inputs(self) -> bool:
        ok = True

        # Beispiel: Frequenz-Logik
        if self.spn_freq_start.value() >= self.spn_freq_stop.value():
            ok = False
            self._mark_invalid(self.spn_freq_start)
            self._mark_invalid(self.spn_freq_stop)
        else:
            self._clear_invalid(self.spn_freq_start)
            self._clear_invalid(self.spn_freq_stop)

        # Beispiel: Rotation
        if self.spn_rot_start.value() >= self.spn_rot_stop.value():
            ok = False
            self._mark_invalid(self.spn_rot_start)
            self._mark_invalid(self.spn_rot_stop)
        else:
            self._clear_invalid(self.spn_rot_start)
            self._clear_invalid(self.spn_rot_stop)

        # … weitere Checks hier …

        # Start-Button nur freigeben, wenn alles ok
        self.btn_start.setEnabled(ok)
        return ok


    def _mark_invalid(self, widget):
        palette = widget.palette()
        palette.setColor(QPalette.Base, QColor("#ffcccc"))
        widget.setPalette(palette)

    def _clear_invalid(self, widget):
        widget.setPalette(QApplication.palette())


    # Builders ------------------------------------------------------------------------------------
    def build_left_panel(self) -> QGroupBox:

        outer_gb = QGroupBox("Measurement parameters", self)
        outer_gb.setMaximumWidth(250)

        outer_vbox = QVBoxLayout(outer_gb)

        # Preset
        self.gb_preset = self.build_preset_group(parent=outer_gb)
        outer_vbox.addWidget(self.gb_preset)

        # Frequency
        self.gb_freq = self.build_frequency_group(parent=outer_gb)
        outer_vbox.addWidget(self.gb_freq)

        # Rotation
        self.gb_rot = self.build_rotation_group(parent=outer_gb)
        outer_vbox.addWidget(self.gb_rot)

        # VNA
        self.gb_vna = self.build_vna_group(parent=outer_gb)
        outer_vbox.addWidget(self.gb_vna)

        # Spacer (füllt Resthöhe)
        outer_vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Start-Button
        self.btn_start = QPushButton("Start", outer_gb)
        outer_vbox.addWidget(self.btn_start)

        return outer_gb

    # Preset ----------------------------------------------------------------------------
    
    def build_preset_group(self, parent: QWidget) -> QGroupBox:
        
        gb = QGroupBox("Preset", parent)
        grid = QGridLayout(gb)
        
        # 1) toggle preset
        self.preset_checkbox = QCheckBox(
            parent = gb,
            text = "Use VNA Preset",
        )
        self.preset_checkbox.setChecked(True)
        grid.addWidget(self.preset_checkbox, 0, 0, 1, 1)
        
        # 2) preset selection
        self.preset_frame, self.cmb_preset = self._make_row_combo(
            parent=gb,
            label_text="Preset:",
            items=[preset["name"] for preset in presets],
            tooltip="Used preset in VNA",
            current_text="Single Freq & Position",
            item_tooltip=[preset["description"] for preset in presets],
        )
        grid.addWidget(self.preset_frame, 1, 0, 1, 1)
        
        return gb
        
        

    # Frequency -------------------------------------------------------------------------
    def build_frequency_group(self, parent: QWidget) -> QGroupBox:

        gb = QGroupBox(parent)
        stack = QStackedWidget(gb)
        gb_1 = QGroupBox("Frequency", stack)
        gb_2 = QGroupBox("Frequency", stack)
        grid_1 = QGridLayout(gb_1)
        grid_2 = QGridLayout(gb_2)

        stack.addWidget(gb_1)
        stack.addWidget(gb_2)

        # 1) Start
        self.freq_start_frame, self.spn_freq_start = self._make_row_double(
            parent=gb_1,
            label_text="Start:",
            suffix="MHz",
            minimum=0.009,
            maximum=8500.0,
            value=5150.0,
            decimals=2,
            tooltip="Start frequency of the measurement"
        )
        grid_1.addWidget(self.freq_start_frame, 0, 0, 1, 1)

        # 2) Stop
        self.freq_stop_frame, self.spn_freq_stop = self._make_row_double(
            parent=gb_1,
            label_text="Stop:",
            suffix="MHz",
            minimum=0.009,
            maximum=8500.0,
            value=5875.0,
            decimals=2,
            tooltip="Stop frequency of the measurement"
        )
        grid_1.addWidget(self.freq_stop_frame, 2, 0, 1, 1)

        # 3) IF bandwidth
        self.if_bw_frame, self.spn_if_bw = self._make_row_double(
            parent=gb_1,
            label_text="IF bandwidth:",
            suffix="kHz",
            minimum=0.001,
            maximum=10.0,
            value=0.1,
            decimals=3,
            tooltip="Controls measurement speed vs. noise: narrower is cleaner, wider is faster."
        )
        grid_1.addWidget(self.if_bw_frame, 5, 0, 1, 1)

        # 4) Points
        self.vna_points_frame, self.spn_points = self._make_row_int(
            parent=gb_1,
            label_text="Points:",
            minimum=101,
            maximum=10001,
            value=401,
            tooltip="Controls frequency resolution vs. sweep time: more points = finer, slower."
        )
        grid_1.addWidget(self.vna_points_frame, 6, 0, 1, 1)

        # 1) Start
        self.freq_frame, self.spn_freq = self._make_row_double(
            parent=gb_2,
            label_text="Freqency:",
            suffix="MHz",
            minimum=0.009,
            maximum=8500.0,
            value=5512.5,
            decimals=2,
            tooltip="Frequency for the measurement"
        )
        grid_2.addWidget(self.freq_frame, 0, 0, 1, 1)
        
        return gb

    # Rotation --------------------------------------------------------------------------
    def build_rotation_group(self, parent: QWidget) -> QGroupBox:
        """
        GroupBox 'Rotation':
          - Start       (°, int,  min:0,   max:360, step:1,   default:0)
          - Stop        (°, int,  min:0,   max 360, step:1,   default 180)
          - Stepsize    (°, float min:0.1, max 180, step:0.1, default 1.0)
        """
        gb = QGroupBox("Rotation", parent)
        grid = QGridLayout(gb)

        # Start °
        self.rotation_start_frame, self.spn_rot_start = self._make_row_double(
            parent=gb,
            label_text="Start:", suffix="°", minimum=0.0, maximum=360.0,
            value=0.0, tooltip="Start angle of the messurement", decimals=0
        )
        grid.addWidget(self.rotation_start_frame, 0, 0, 1, 1)

        # Stop °
        self.rotation_stop_frame, self.spn_rot_stop = self._make_row_double(
            parent=gb,
            label_text="Stop:", suffix="°", minimum=0.0, maximum=360.0,
            value=180.0, tooltip="Stop angle of the messurement", decimals=0
        )
        grid.addWidget(self.rotation_stop_frame, 2, 0, 1, 1)

        # Stepsize °
        self.rotation_stepsize_frame, self.spn_rot_step = self._make_row_double(
            parent=gb,
            label_text="Stepsize:", suffix="°", minimum=0.1, maximum=180.0,
            value=1.0, tooltip="Stepsize for the rotation", decimals=1, single_step=0.1
        )
        grid.addWidget(self.rotation_stepsize_frame, 3, 0, 1, 1)

        return gb

    # VNA --------------------------------------------------------------------------------
    def build_vna_group(self, parent: QWidget) -> QGroupBox:
        """
        GroupBox 'VNA' mit drei Zeilen:
          - Rx: Combo (Port1..Port4, current 'Port2')
          - Tx: Combo (Port1..Port4, current 'Port1')
          - Tx Power: DoubleSpin (-100..27 dBm, default -10)
        Tooltips & Labels wie in deiner .ui.
        """
        gb = QGroupBox("VNA", parent)
        grid = QGridLayout(gb)

        # Tx
        self.vna_tx_frame, self.cmb_tx = self._make_row_combo(
            parent=gb,
            label_text="Tx:",
            items=["Port1", "Port2", "Port3", "Port4"],
            tooltip="Used port for transmitting antenna",
            current_text="Port2",
        )
        grid.addWidget(self.vna_tx_frame, 0, 0, 1, 1)
        
        # Rx
        self.vna_rx_frame, self.cmb_rx = self._make_row_combo(
            parent=gb,
            label_text="Rx:",
            items=["Port1", "Port2", "Port3", "Port4"],
            tooltip="Used port for recriving antenna",
            current_text="Port1",
        )
        grid.addWidget(self.vna_rx_frame, 1, 0, 1, 1)

        # Tx Power
        self.vna_txpower_frame, self.spn_tx_power = self._make_row_double(
            parent=gb,
            label_text="Tx Power:", suffix="dBm", minimum=-100.0, maximum=27.0,
            value=-20.0, tooltip="Used transmit power for this measurement", decimals=0
        )
        grid.addWidget(self.vna_txpower_frame, 2, 0, 1, 1)

        return gb

    # Row Helper/Factory --------------------------------------------------------------------------
    def _make_row_frame(self, parent: QWidget) -> Tuple[QFrame, QHBoxLayout]:
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
        self,
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
        frame, h = self._make_row_frame(parent)

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
        self,
        parent: QWidget,
        label_text: str,
        minimum: int | None,
        maximum: int | None,
        value: int | None,
        tooltip: str | None = None,
    ) -> Tuple[QFrame, QSpinBox]:
        """Zeile mit QLabel links + QSpinBox rechts + Expander dazwischen."""
        frame, h = self._make_row_frame(parent)

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
        self,
        parent: QWidget,
        label_text: str,
        items: list[str],
        tooltip: str | None = None,
        current_text: str | None = None,
        item_tooltip: list[str] | None = None,
    ) -> Tuple[QFrame, QComboBox]:
        """Zeile mit QLabel links + QComboBox rechts + Expander dazwischen."""
        frame, h = self._make_row_frame(parent)

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





class SwitchableGroupBox(QGroupBox):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        layout = QVBoxLayout(self)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)

    def addPage(self, widget: QWidget) -> int:
        return self.stack.addWidget(widget)

    def setPage(self, index: int):
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)






# start as standalone -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    c = controller.main_controller()
    
    w = MeasurementWindow(controller=c)
    w.show()
    sys.exit(app.exec())
