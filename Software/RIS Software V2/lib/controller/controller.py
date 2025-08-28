import os
os.environ["QT_API"] = "pyside6"

from PySide6.QtCore import QObject, Signal, Slot
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Union # , Tuple, Dict, Callable
import numpy as np
import uuid
from datetime import datetime
from pathlib import Path
from collections import OrderedDict
import json

try:
    from EhMatable import EhMatable_E5810, EhMatable
    from RISinterface import RISinterface
except:
    from controller.EhMatable import EhMatable_E5810, EhMatable
    from controller.RISinterface import RISinterface

from RsInstrument import RsInstrument

# for testing and debugging
DEBUG = True
DEMO = False

###################################################################################################

@dataclass
class RISpattern:
    matrix: np.ndarray
    uid: str = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        object.__setattr__(self, "uid", str(uuid.uuid4()))

    def __eq__(self, other):
        if not isinstance(other, RISpattern):
            return NotImplemented
        return np.array_equal(self.matrix, other.matrix)

    def __str__(self):
        # Matrix als String aufbereiten
        matrix_str = " " + str(self.matrix)\
                        .replace("1", "████")\
                        .replace("0", "░░░░")\
                        .replace("[", "")\
                        .replace("]", "")
        return f"RisConfiguration (uid={self.uid})\n{matrix_str}"

@dataclass
class Measurement_config:
    freq_start_hz: float
    freq_stop_hz: float
    if_bandwidth_hz: float
    points: int
    ang_start_deg:float
    ang_stop_deg:float
    ang_step_deg:float
    power_dbm: float
    sweep_type: str = "LIN"
    averages: int = 5

    def save(self, fname: str):
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=4)

    @classmethod
    def load(cls, fname: str) -> "Measurement_config":
        with open(fname, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

#-------------------------------------------------------------------------------------------------#

class main_controller(QObject):

    start_measurement = Signal()
    stop_measurement = Signal()

    def __init__(self):
        super().__init__()
        self.data = pattern_handle(self)
        resource = "TCPIP::192.168.111.111::INSTR"

        self.RIS = RISinterface()
        
        if DEMO:
            self.VNA = VNA_demo()
            self.table = EhMatable_demo()
            self.RIS.set_Port("DEMO")
        else:
            self.VNA = VNA(resource)
            self.table = EhMatable("COM16")
            self.RIS.set_Port("COM9")

        self.table.reset()
        self.RIS.connect()

    @Slot(list)
    def measure(self, measurement:Measurement_config):
        self.start_measurement.emit()
        # prepare dir to save files
        run_dir = Path("./data") / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if DEMO:
            import shutil
            run_dir = Path("./data") / "test"
            if run_dir.exists():
                shutil.rmtree(run_dir)
        run_dir.mkdir(parents=True)

        measurement.save(str(run_dir / "measurement_config.json"))

        angle = np.arange(measurement.ang_start_deg,
                          measurement.ang_stop_deg,
                          measurement.ang_step_deg)
        
        pattern = self.data.unique_patterns()
        
        for p_idx, p in enumerate(pattern, start=1):
            
            pdir = run_dir / f"pattern_{p_idx:02d}"
            pdir.mkdir(exist_ok=True)
            np.savetxt(pdir / "pattern.csv",
                       p.matrix,
                       delimiter=",",
                       fmt="%.0d")
        
        for ang in angle:
            self.table.setAngle(ang)
        
            for p_idx, p in enumerate(pattern, start=1):
                
                self.RIS.write_pattern(p.matrix)
                
                trace_data = self.VNA.read_trace()
                
                # create path string and save
                pdir = run_dir / f"pattern_{p_idx:02d}"
                path = pdir / f"{ang:3.3f}deg.csv"
                trace_data.save(str(path))
                
                # raise NotImplementedError("test")
        self.stop_measurement.emit()

#-------------------------------------------------------------------------------------------------#

class pattern_handle(QObject):
    
    pattern_deleted = Signal(RISpattern)
    pattern_added = Signal(RISpattern)
    selected_pattern_changed = Signal(RISpattern)
    selected_pattern_edited = Signal(RISpattern)
    
    def __init__(self, parent:main_controller):
        super().__init__(parent=parent)
        
        self.ris_col_count  = 16
        self.ris_row_count   = 16
        
        self.akt_pattern_uid = None
        self.pattern: List[RISpattern] = []
        self.add_empty()
    
    #-------------------------------------------#
    def add_pattern(self, pattern:RISpattern, akt=True):
        uids = {p.uid for p in self.pattern}
        if pattern.uid not in uids:     # check if new pattern is already in list
            self.pattern.append(pattern)
            self.pattern_added.emit(pattern)
            if akt:
                self.akt_pattern_uid = pattern.uid
                self.selected_pattern_changed.emit(pattern)
    
    #-------------------------------------------#
    def add_empty(self) -> str:
        self.add_pattern(RISpattern(np.zeros((self.ris_row_count, self.ris_col_count), dtype=int)), akt=True)
        self.pattern_deleted.emit(self.get_selected_pattern())
    
    #-------------------------------------------#
    def duplicate_selected(self):
        return self.add_pattern(RISpattern(self.get_selected_pattern().matrix))

    #-------------------------------------------#
    def set_pattern(self, target_uid: str):
        if isinstance(target_uid, str):
            target_obj = self.find_pattern_by_uid(target_uid)
            if target_obj is None:
                raise IndexError("uid not found!")
            elif self.akt_pattern_uid != target_uid:
                self.akt_pattern_uid = target_uid
                if DEBUG: print()
                self.selected_pattern_changed.emit(target_uid)
        else:
            raise TypeError(f"a str(UID) is required not {type(pattern)}")

    #-------------------------------------------#
    def delet_pattern(self, uid):
        for p_idx, p in enumerate(self.pattern):
            if p.uid == uid:
                self.pattern.remove(p)
                if p_idx == 0:      # prevent list from getting empty
                    self.add_empty()
                else:
                    self.set_selected_pattern(self.pattern[p_idx-1].uid)
                self.pattern_deleted.emit(p)

    #-------------------------------------------#
    def set_selected_pattern(self, uid:str):
        uids = {p.uid for p in self.pattern}
        if uid in uids:     # check if new pattern is in list
            self.akt_pattern_uid = uid
            self.selected_pattern_changed.emit(self.get_selected_pattern())

    #-------------------------------------------#
    def get_selected_pattern(self) -> Optional["RISpattern"]:
        if not self.akt_pattern_uid:
            return None
        return self.find_pattern_by_uid(self.akt_pattern_uid)

    #-------------------------------------------#
    def get_selected_uid(self) -> Optional["str"]:
        if not self.akt_pattern_uid:
            return None
        return self.akt_pattern_uid
    
    #-------------------------------------------#
    def edit_selected(self, matrix:np.ndarray):
        selected_pattern = self.get_selected_pattern()
        selected_pattern.matrix = matrix
        self.selected_pattern_edited.emit(selected_pattern)
    
    #-------------------------------------------#
    def find_pattern_by_uid(self, uid: str) -> Optional["RISpattern"]:
        return next((p for p in self.pattern if p.uid == uid), None)

    #-------------------------------------------#
    def unique_patterns(self) -> list[RISpattern]:
        return self.pattern
        return list(OrderedDict.fromkeys(self.pattern)) #TODO TypeError: unhashable type: 'RISpattern' | implement with loop

#-------------------------------------------------------------------------------------------------#

class MeasurementResult:
    def __init__(self, freq_hz:np.ndarray, mag_dB:np.ndarray, points:int = 0):
        self.freq_hz = np.asarray(freq_hz).flatten()
        self.mag_db = np.asarray(mag_dB).flatten()
        if points == 0: points = len(freq_hz)
        self.points = points

    @classmethod
    def from_file(cls, fname):
        data = np.loadtxt(fname, delimiter=",", skiprows=1)
        freq_hz, mag_db = data[:, 0], data[:, 1]
        return cls(freq_hz, mag_db)

    def save(self, fname: str):
        if self.freq_hz.shape[0] != self.mag_db.shape[0]:
            raise ValueError("The lengths of freq_Hz and mag_dB are not the same!")
        data = np.column_stack((self.freq_hz, self.mag_db))
        np.savetxt(
            fname,
            data,
            delimiter=",",
            header="frequency [Hz], magnitude [dB]",
            fmt="%.9f"
        )


#-------------------------------------------------------------------------------------------------#

class VNA(RsInstrument):
    def __init__(self, resource_name:str):
        
        super().__init__(resource_name, True, False, "SelectVisa='rs'")
        self.write_str("SYST:DISP:UPD ON")
        # load preset
        self.write_str("SYST:PRES:USER:NAME \'C:\\Users\\Public\\Documents\\Rohde-Schwarz\\Vna\\RecallSets\\RIS_Projekt_FK.znx\'")
        self.write_str("SYST:PRES:USER ON")
        self.write_str("SYST:PRES:REM ON")
        self.write_str("*RST")
        
        # self.write_str("SENS:AVER:CLE")  # clear average TODO fix SCPI

    def read_trace(self):
        # self.write_str("SENS:AVER:CLE")  # clear average TODO fix SCPI
        self.write_str_with_opc("INIT",60000)  # restart sweep
        
        points_count = self.query_int('SENSe1:SWEep:POINts?')  # Request number of frequency points
        trace_data = self.query_str('CALC1:DATA? FDAT')  # Get measurement values for complete trace
        trace_array = np.array(list(map(float, trace_data.split(','))))  # Convert the received string into a tuple
        freq_list = self.query_str('CALC:DATA:STIM?')  # Get frequency list for complete trace
        freq_array = np.array(list(map(float, freq_list.split(','))))  # Convert the received string into a tuple

        return MeasurementResult(freq_array, trace_array, points_count)

#-------------------------------------------------------------------------------------------------#
#- DEMO classes ----------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------#

class VNA_demo:
    def __init__(self):
        pass
    def read_trace(self):
        return MeasurementResult.from_file("test.csv")

#-------------------------------------------------------------------------------------------------#

class EhMatable_demo():
    def __init__(self):
        self.limits = (0,361.0)  # Absolut Limits without damage of Hardware in degrees
        self.angle = 0.0
        self.stepsPerDegree = 1/(0.982/2)  # Engine steps to produce one degree turn
    def connect(self):
        return "success"

    def reset(self):
        self.angle = 0

    def getAngle(self):
        self.steppos = self.stepsPerDegree * self.angle
        return self.steppos, self.angle

    def setPosSteps(self, sollpos):
        sollpos = int(sollpos)
        if DEBUG: print("[EhMatable_demo] Moving to step pos", sollpos)

        diff = int(sollpos - self.steppos)
        if DEBUG: print("[EhMatable_demo] diff", diff)

        self.steppos = sollpos # Hardcoded as engine does not cout steps for now
        self.angle = self.steppos / self.stepsPerDegree
        print("[EhMatable_demo] ", self.steppos,self.angle)

        ### check position ####################################
        steps, angle = self.getAngle()
        if steps == sollpos:
            self.steppos = steps
        else:
            raise ValueError("[EhMatable_demo] Difference Target step pos and actual position " + str(steps) + " <-> " + str(sollpos))
        self.angle = self.steppos / self.stepsPerDegree
        return True

    def setAngle(self, deg: float):
        ang = self.getAngle()
        dif_deg = deg - ang[1]
        dest_step = ang[0] + int(dif_deg * self.stepsPerDegree)
        self.setPosSteps(dest_step)
        ang = self.getAngle()
        if DEBUG: print(f"[EhMatable_demo] angle: {ang[1]:.3f}° ({ang[0]:.0f} steps)")
        return ang
#-------------------------------------------------------------------------------------------------#