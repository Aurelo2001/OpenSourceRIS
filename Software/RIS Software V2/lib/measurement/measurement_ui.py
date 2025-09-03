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
from measurement.measurement_config_panel import Measurement_config_GB
from measurement.presets import presets

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

        self.meas_conf = Measurement_config_GB(self)
        root_hbox.addWidget(self.meas_conf)

        ris_conf_widget = RisConfigManager(self._c, self)
        root_hbox.addWidget(ris_conf_widget)

        self.setMenuBar(QMenuBar(self))
        self.setStatusBar(QStatusBar(self))

        self.connect_signals()
        
        self.meas_conf.gb_preset.cmb_preset.setCurrentIndex(1)
        self.meas_conf.gb_preset.preset_checkbox.checkStateChanged.emit(Qt.CheckState.Checked)


    # Wire Signals --------------------------------------------------------------------------------
    def connect_signals(self) -> None:
        self.meas_conf.gb_preset.preset_checkbox.checkStateChanged.connect(self.preset_state)
        self.meas_conf.gb_preset.cmb_preset.activated.connect(self.preset_select)
        self.meas_conf.btn_start.clicked.connect(self.on_start_clicked)


    # Slots ---------------------------------------------------------------------------------------
    def preset_state(self, state:Qt.CheckState):
        state = not bool(state.value)
        self.meas_conf.gb_freq.setEnabled(state)
        self.meas_conf.gb_rot.setEnabled(state)
        self.meas_conf.gb_vna.setEnabled(state)
        self.meas_conf.gb_preset.cmb_preset.activated.emit(self.meas_conf.gb_preset.cmb_preset.currentIndex())


    def preset_select(self, idx:int):
        if presets[idx]["single_freq"]:
            self.meas_conf.tab_freq.setCurrentIndex(0)
            self.meas_conf.gb_freq_single.spn_freq.setValue(presets[idx]["freq_Hz"] * 1e-6)
        else:
            self.meas_conf.tab_freq.setCurrentIndex(1)
            self.meas_conf.gb_freq_sweep.spn_freq_start.setValue(presets[idx]["freq_start_Hz"] * 1e-6)
            self.meas_conf.gb_freq_sweep.spn_freq_stop.setValue(presets[idx]["freq_stop_Hz"] * 1e-6)
            self.meas_conf.gb_freq_sweep.spn_if_bw.setValue(presets[idx]["if_bw_Hz"] * 1e-3)
            self.meas_conf.gb_freq_sweep.spn_points.setValue(presets[idx]["points"])
            
        if presets[idx]["single_rot"]:
            self.meas_conf.tab_rot.setCurrentIndex(0)
            self.meas_conf.gb_rot_single.spn_rot.setValue(presets[idx]["rot_deg"])
        else:
            self.meas_conf.tab_rot.setCurrentIndex(1)
            self.meas_conf.gb_rot_sweep.spn_rot_start.setValue(presets[idx]["rot_start_deg"])
            self.meas_conf.gb_rot_sweep.spn_rot_stop.setValue(presets[idx]["rot_stop_deg"])
            self.meas_conf.gb_rot_sweep.spn_rot_step.setValue(presets[idx]["rot_step_deg"])
        
        self.meas_conf.gb_vna.spn_tx_power.setValue(presets[idx]["power_tx_dBm"])
        self.meas_conf.gb_vna.cmb_tx.setCurrentIndex(presets[idx]["port_tx"])
        self.meas_conf.gb_vna.cmb_rx.setCurrentIndex(presets[idx]["port_rx"])
        self.preset_changed.emit(idx)


    def on_start_clicked(self) -> None:
        kwargs = {}
        if self.meas_conf.tab_freq.currentIndex() == 0:
            kwargs["freq_hz"] = self.meas_conf.gb_freq_single.spn_freq.value() * 1e6
        else:
            kwargs["freq_start_hz"] = self.meas_conf.gb_freq_sweep.spn_freq_start.value() * 1e-6
            kwargs["freq_stop_hz"] = self.meas_conf.gb_freq_sweep.spn_freq_stop.value() * 1e-6
            kwargs["freq_step_hz"] = self.meas_conf.gb_freq_sweep.spn_if_bw.valute() * 1e-3
            kwargs["if_bw_hz"] = self.meas_conf.gb_freq_sweep.spn_points.value()
            kwargs["points"] = self.meas_conf.gb_freq_sweep.spn_points.value()
        
        if self.meas_conf.tab_rot.currentIndex() == 0:
            kwargs["rot_deg"] = self.meas_conf.gb_rot_single.spn_rot.value()
        else:
            kwargs["rot_start_deg"] = self.meas_conf.gb_rot_sweep.spn_rot_start.value()
            kwargs["rot_stop_deg"] = self.meas_conf.gb_rot_sweep.spn_rot_stop.value()
            kwargs["rot_step_deg"] = self.meas_conf.gb_rot_sweep.spn_rot_step.value()
        
        kwargs["power_dbm"] = self.meas_conf.gb_vna.spn_tx_power.value()
        kwargs["port_tx"] = self.meas_conf.gb_vna.cmb_tx.currentIndex()
        kwargs["port_rx"] = self.meas_conf.gb_vna.cmb_rx.currentIndex()
        
        measurement_conf = controller.Measurement_config(**kwargs)
        self.measure.emit(measurement_conf)
        self.statusBar().showMessage("Measurement started …", 1500)

    # def validate_inputs(self) -> bool:
    #     ok = True

    #     # Beispiel: Frequenz-Logik
    #     if self.spn_freq_start.value() >= self.spn_freq_stop.value():
    #         ok = False
    #         self._mark_invalid(self.spn_freq_start)
    #         self._mark_invalid(self.spn_freq_stop)
    #     else:
    #         self._clear_invalid(self.spn_freq_start)
    #         self._clear_invalid(self.spn_freq_stop)

    #     # Beispiel: Rotation
    #     if self.spn_rot_start.value() >= self.spn_rot_stop.value():
    #         ok = False
    #         self._mark_invalid(self.spn_rot_start)
    #         self._mark_invalid(self.spn_rot_stop)
    #     else:
    #         self._clear_invalid(self.spn_rot_start)
    #         self._clear_invalid(self.spn_rot_stop)

    #     # … weitere Checks hier …

    #     # Start-Button nur freigeben, wenn alles ok
    #     self.btn_start.setEnabled(ok)
    #     return ok


    # def _mark_invalid(self, widget):
    #     palette = widget.palette()
    #     palette.setColor(QPalette.Base, QColor("#ffcccc"))
    #     widget.setPalette(palette)

    # def _clear_invalid(self, widget):
    #     widget.setPalette(QApplication.palette())




# start as standalone -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    c = controller.main_controller()
    
    w = MeasurementWindow(controller=c)
    w.show()
    sys.exit(app.exec())
