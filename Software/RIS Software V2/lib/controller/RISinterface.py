import sys
sys.path.append("./lib")


try:
    from com_sim import RISSimulatorSerial
except:
    from controller.com_sim import RISSimulatorSerial

import serial
import serial.tools.list_ports

# list of RIS serial-uart chip serial numbers
FILTER_LIST = ["D3A371JNA"]

###################################################################################################
#### class definition #############################################################################
###################################################################################################
class RISinterface:
    def __init__(self):
        self.connected = False
        self.Port = None
        self.demo = True

###################################################################################################
##### functions ###################################################################################
###################################################################################################
    def set_Port(self, port: str):
        if not self.connected:                                  # check if connection is activ
            if port.capitalize() == "DEMO":
                self.Port = None
                self.demo =True
                return (True, f"DEMO mode activated.")
            else:
                result, ports = self.get_RIS_devices()          # get list of available RIS devices
                if result:                                      # if RIS found
                    if any(p.name == port for p in ports):      # if requested port matches RIS
                        self.Port = port
                        self.demo = False
                        return (True, f"COM port set to: {self.Port}")
                else:                                           # no RIS found
                    self.Port = None
                    self.demo = True
                    return (True, f"No RIS Device found! DEMO mode activated.")
        else:                                                   # connection active, port cannot be changed
            return (False, f"Port switch failed: Connection is still open.")


    def get_RIS_devices(self) -> tuple[bool, list]:
        all_ports = serial.tools.list_ports.comports()
        ports = [
            port for port in all_ports
            if port.serial_number is not None and any(filter in port.serial_number for filter in FILTER_LIST)
        ]
        if len(ports) != 0:
            return (True, ports)
        else:
            return (False, [])


#### communication functions ######################################################################
    def connect(self) -> tuple[bool, str]:
        if self.connected:
            return (True, "RIS already connected")
        else:
            if self.demo:
                self.ser = RISSimulatorSerial()
            else:
                self.ser = serial.Serial(
                    port= self.Port,
                    baudrate=115200,
                    bytesize=8,
                    stopbits=serial.STOPBITS_ONE)
            # checking connection
            if self.ser.isOpen():
                self.connected = True
                return (True, "connection established")
            else:
                self.connect = False
                return (False, "connection failed")


    def disconnect(self) -> tuple[bool, str]:
        if self.connected:
            if self.ser.isOpen():
                self.ser.close()
            self.connected = False
            return (True, "RIS disconnected")
        else:
            return (True, "No RIS connected")
        return (False, "Error: disconnection Failed")


    def write_pattern(self, state_matrix:list[list[int]]) -> tuple[bool, str]:
        bit_list = [int(value) for row in state_matrix for value in row]
        bit_string = "".join(map(str,bit_list))
        bit_int = int(bit_string, 2)
        tx_str = f"!{bit_int:#0{66}x}\n"

        self.ser.write(tx_str.encode())
        # TODO: timeout
        try:
            rx_msg = self.ser.readline().decode()
        except:
            rx_msg = ""

        if rx_msg == "#OK\n":
            return True
        else:
            return False


    def read_pattern(self) -> tuple[bool, str]:
        self.ser.write("?pattern\n".encode())
        rx_msg = self.ser.readline().decode()
        if len(rx_msg) == 68:
            return (True, rx_msg[3:-1])
        else:
            return (False, "Error: read Pattern failed!")


    def read_extVoltage(self) -> tuple[bool, str]:
        self.ser.write("?vext\n".encode())
        rx_msg = self.ser.readline().decode()[:-1]
        return (True, rx_msg)


    def read_serialnumber(self) -> tuple[bool, str]:
        self.ser.write("?SerialNo\n".encode())
        rx_msg = self.ser.readline().decode()[:-1]
        return (True, rx_msg)


    def reset(self) -> tuple[bool, list[str]]:
        self.ser.write("!Reset\n".encode())
        rx_msg = []
        for _ in range(8):
            rx_msg.append(self.ser.readline().decode()[:-1])
            if rx_msg[-1] == "#READY!":
                return (True, rx_msg)
        return (False, ["Error: Reset failed!"])

