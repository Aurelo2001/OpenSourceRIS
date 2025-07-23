from lib.com_sim import RISSimulatorSerial
import serial
import serial.tools.list_ports


###################################################################################################
#### class definition #############################################################################
###################################################################################################
class RISinterface:
    def __init__(self):
        self.connected = False
        self.Port = []


###################################################################################################
##### functions ###################################################################################
###################################################################################################
    def setPort(self, port):
        self.Port = port
        if len(port) != 1:
            return (True, f"COM port set to: {port}")
        else:
            return (True, f"DEMO mode activated, no COM port found.")


    def get_available_ports(self) -> tuple[bool, list]:
        ports = serial.tools.list_ports.comports()
        if len(ports) != 0:
            return (True, ports)
        else:
            return (False, [])


#### communication functions ######################################################################
    def connect(self) -> tuple[bool, str]:
        if self.connected:
            return (True, "RIS already connected")
        else:
            if self.Port != "DEMO":
                self.ser = serial.Serial(
                    port= self.Port,
                    baudrate=9600,
                    bytesize=8,
                    stopbits=serial.STOPBITS_ONE)
            else:
                self.ser = RISSimulatorSerial()

            if self.ser.isOpen():
                self.connected = True
                return (True, "connection established")
            else:
                return (False, "connection failed")


    def disconnect(self) -> tuple[bool, str]:
        if self.connected:      # wenn Verbindung besteht
            if self.ser.isOpen():
                self.ser.close()
            self.connected = False
            return (True, "RIS disconnected")
        else:                   # wenn keine verbindung besteht
            return (True, "No RIS connected")
        return (False, "Error: disconnection Failed")


    def set_pattern(self, state_matrix:list[list[int]]) -> tuple[bool, str]:
        bit_list = [int(value) for row in state_matrix for value in row]
        bit_string = "".join(map(str,bit_list))
        bit_int = int(bit_string, 2)
        tx_str = f"!{bit_int:#0{66}x}\n"

        self.ser.write(tx_str.encode())
        # TODO: timeout
        try:
            rx_msg = self.ser.readline(1).decode()
        except:
            rx_msg = ""

        if rx_msg == "#OK\n":
            return True
        else:
            return False


    def get_pattern(self) -> tuple[bool, str]:                      # TODO: table update missing
        self.ser.write("?pattern".encode())
        rx_msg = self.ser.readline(1).decode()
        if len(rx_msg) == 68:
            print(rx_msg[3:-1])
            return (True, rx_msg[3:-1])
        else:
            return (False, "Error: read Pattern failed!")


    def get_extVoltage(self) -> tuple[bool, str]:
        self.ser.write("?vext".encode())
        rx_msg = self.ser.readline(1).decode()[:-1]
        return (True, rx_msg)


    def get_serialnumber(self) -> tuple[bool, str]:
        self.ser.write("?SerialNo".encode())
        rx_msg = self.ser.readline(1).decode()[:-1]
        return (True, rx_msg)


    def reset(self) -> tuple[bool, list[str]]:        # TODO: kanzen string zurückliefern
        self.ser.write("!Reset".encode())
        rx_msg = []
        for _ in range(8):
            rx_msg.append(self.ser.readline(10).decode()[:-1])
            print(rx_msg[-1])
            if rx_msg[-1] == "#READY!":
                return (True, rx_msg)
        return (False, ["Error: Reset failed!"])

