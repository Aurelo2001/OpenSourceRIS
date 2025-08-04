
import sys
sys.path.append("./")

import serial.tools
import numpy as np
from lib.RISinterface import RISinterface

io = RISinterface()

_, ports = io.get_RIS_devices()

# for port in ports:
#     print("device: ", port.device)
#     print("name: ", port.name)
#     print("description: ", port.description)
#     print("hwid: ", port.hwid)
#     print("vid: ", port.vid)
#     print("pid: ", port.pid)
#     print("serial_number: ", port.serial_number)
#     print("location: ", port.location)
#     print("manufacturer: ", port.manufacturer)
#     print("product: ", port.product)
#     print("interface: ", port.interface)



print(io.set_Port("COM9"))
print(io.connect())
print(io.reset()[1])

# print(io.write_pattern(list(np.ones(shape=(16,16)))))
# print(io.write_pattern(list(np.zeros(shape=(16,16)))))
print(io.write_pattern(list(np.random.choice([0,1], size=(16,16)))))

print(io.read_pattern()[1])
print(io.read_extVoltage()[1])
print(io.read_serialnumber()[1])