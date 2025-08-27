import re
import threading
from queue import Queue

class RISSimulatorSerial:
    def __init__(self):
        self._rx_queue = Queue()
        self._tx_log = []
        self._closed = False
        self.pattern = 0x0000000000000000000000000000000000000000000000000000000000000000
        self.vext = 5.00
        self.serialno = " 42"
        self.bt_key = None
        self.lock = threading.RLock()
        self._booted = True

    def write(self, data: bytes):
        with self.lock:
            self._tx_log.append(data)
            line = data.decode('ascii', errors='ignore').strip().lower()
            print(f"[RISSimulator] Received: {line}")
            if not line:
                return
            if not self._booted:
                return

            if line.startswith("!0x"):
                try:
                    hexdata = line[3:]
                    if len(hexdata) != 64:
                        raise ValueError("Invalid pattern length")
                    self.pattern = int(hexdata, 16)
                    self._enqueue("#OK\n")
                except ValueError:
                    pass  # invalid pattern → no response
            elif line == "?pattern":
                pattern_hex = f"{self.pattern:064X}"
                self._enqueue(f"#0X{pattern_hex}\n")
            elif line == "?vext":
                self._enqueue(f"#{self.vext:.2f} V\n")
            elif line == "?serialno":
                self._enqueue(f"#SerNo:{self.serialno}\n")
            elif line == "!reset":
                self._booted = False
                threading.Timer(0.5, self._boot_ready).start()
            elif line.startswith("!bt-key"):
                self.bt_key = line[len("!bt-key"):].strip()
                self._enqueue("#OK\n")
            else:
                pass  # unknown command → no response

    def _boot_ready(self):
        self._enqueue("\n")
        self._enqueue("Open Source RIS\n")
        self._enqueue("Firmware version: 1.1\n")
        self._enqueue("Serial no.:  12\n")
        self._enqueue("Row count: 16\n")
        self._enqueue("Column count: 16\n")
        self._enqueue("\n")
        self._enqueue("#READY!\n")
        self._booted = True

    def _enqueue(self, msg: str):
        self._rx_queue.put(msg.encode("ascii"))

    def readline(self, timeout=1.0) -> bytes:
        try:
            return self._rx_queue.get(timeout=timeout)
        except:
            return b""

    @property
    def in_waiting(self):
        return self._rx_queue.qsize()

    def close(self):
        self._closed = True

    def isOpen(self):
        return not self._closed

    def get_tx_log(self):
        return self._tx_log