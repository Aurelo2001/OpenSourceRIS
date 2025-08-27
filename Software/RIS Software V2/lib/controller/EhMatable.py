'''
Parent Class for all Turntable Hardware in the Microwave lab

defines an (abstract) turntable class that acts as parent for specific turntables
it also acts as a generic synthetic table

S. Peik, July 2019

'''
import pyvisa as visa
from numpy import nan, abs, sinc, array, log10, sqrt, power
from numpy.random import normal
from time import sleep
# from readchar import readkey,readchar # install with sudo pip3 install readchar
import matplotlib.pyplot as plt

DEBUG = False

try:
    from Turntable import Turntable
    from checkserialports import *
except:
    from controller.Turntable import Turntable
    from controller.checkserialports import *
    



class EhMatable(Turntable):


    def __init__(self, dev=None, ethernet = False):
        super().__init__()
        self.comport = dev
        self.name = 'EhMa Antenna Positioner'
        self.portname = self.comport
        self.connect(self.comport)
        self.limits = (0,361.0)  # Absolut Limits without damage of Hardware in degrees
        self.angle = 0.0
        self.stepsPerDegree = 1/(0.982/2)  # Engine steps to produce one degree turn
        self.buffersize = 1024  # serial buffer in bytes
        self.angularVelocity = 360./20.   # maximum angular velocity in degrees per second, useful for wait loops
        self.stepsPerRev = self.stepsPerDegree * 360
        self.stepspeed = 0.08  ## approx delay for performing one userstep for animations
        self.inmovement = False
        self.UARTBuffersize = 32  # Size of fifo in uart
        self.ethernet = ethernet   # True if Agilent Gateway Ethernet used


    def connect(self,fixport = '',ipaddress = "192.168.111.210"):
        success = False
        self.ethernet = False
        ports = [fixport]
        if DEBUG: print(self.ethernet)
        print('Ports to Check:',ports)
        for port in ports:
            print("Connecting to Table at port", port)
            try:
                if not self.ethernet:
                    print("Connect direct serial")
                    self.serconn = serial.Serial(port=ports[0], baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)
                    print("--connected--")
                    self.serconn.flushOutput()  #
                    self.serconn.flushInput()   #
                    line = self.serconn.readline()
                else:
                    print("Connect via Ethernet")
                    rm = visa.ResourceManager()
                    con = "TCPIP::" + ipaddress + "::COM1"
                    tester_A = rm.get_instrument(con, timeout=1000)
                    if DEBUG: print(tester_A)

                count = 0
                while not b"A 0" in line:
                    #self.serconn.write(b'v\r\n') # query Version
                    line = self.serconn.readline()
                    print("Recieved a ",line)
                    count += 1
                    if count >5:
                        print("Count reached 5, raise Exception")
                        #raise ConnectionRefusedError
                        return "Cannot Connect Time Out"

                if not b"A 0" in line:
                    print('ERROR: Cannot identify a EhMa Table at ',port)
                    return "Error Cannot identify a EhMa Table at" +port
                line = "V 1.2 with degree fix Aug 2019"
                success = "Success"
                self.portname = port
                break
            except Exception as mess:
                print("Connection to Table failed at",port)
                print("Error:", mess.args[0])
                print(mess.args[1])
                if mess.args[0] == 13:
                    message = "Permission to " + port + " denied \n \nCheck if user is in group dialout"
                else:
                    message = "Connection to " + port + " failed \n Check USB Cable \n Is EM Table Power on?"
                print(">>>>>>>> ",message)
        if success:
            print(self.name," connected in version ", line )
            return "success"
        else:
            return "Error"+message



   ########################################################################
    def waitForOk(self):
        self.serconn.flushInput()
        self.inwaitforok = True
        line = ""
        counter = 0
        #print("Wait for OK")
        while("K" not in str(line)):
            try:
                line = self.serconn.readline()
            except:
                print("Serial Read Error in OK Loop !!!!")
            #print("in OK loop:", line)
            counter +=1
            if counter >15:
                raise(ValueError, "No OK coming")
        #print("OK")
        self.inwaitforok = False

    ########################################################################
    def flush(self):
        self.serconn.flushOutput()
        self.serconn.flushInput()

    ########################################################################
    def reset(self):
        self.serconn.flushOutput()
        self.serconn.flushInput()
        self.serconn.write(b'Z\r\n')
        self.waitForOk()
        self.positionEnginesteps = 0
        self.angle = 0
        try:
            data = (self.serconn.readline().rstrip()).decode('ascii')  # CR entfernen
        except:
            pass
        self.serconn.flushOutput()
        self.serconn.flushInput()
        self.waitForOk()
        sleep(0.2)
        print("Reset EhMa Table Done")

    ########################################################################
    def setPosition(self,step):
        # not implemented yet !!!
        self.positionEnginesteps = step
        self.angle = self.positionEnginesteps/self.stepsPerDegree


    # implemented by F. Katenkamp ----------------------------------------------------------------#
    def setAngle(self, deg: float):
        ang = self.getAngle()
        dif_deg = deg - ang[1]
        dest_step = ang[0] + int(dif_deg * self.stepsPerDegree)
        self.setPosSteps(dest_step)
        ang = self.getAngle()
        if DEBUG: print(f"[TABLE] angle: {ang[1]:.3f}° ({ang[0]:.0f} steps)")
        return ang

    def setPosSteps(self, sollpos):
        '''
        Set the angle of the table in step position
        :param target step position:
        :return: success
        '''

        STEPS_PER_PULS = 1
        sollpos = int(sollpos)
        if DEBUG: print("Moving to step pos", sollpos)

        diff = int(sollpos - self.steppos)
        if DEBUG: print("diff", diff)
        if diff > 0:
            cmd = b"+"
        else:
            cmd = b"-"
        ### loop through steps ################################
        for i in range(abs(diff)):
            self.serconn.write(cmd)
            if DEBUG: print("*", end="")
            ## wait after buffer is full
            if i > 0 and i % self.UARTBuffersize == 0:
                self.waitForOk()
        print()
        self.steppos = sollpos # Hardcoded as engine does not cout steps for now
        self.angle = self.steppos / self.stepsPerDegree
        print(self.steppos,self.angle)

        ### check position ####################################
        self.waitForOk()
        steps, angle = self.getAngle()
        if steps == sollpos:
            self.steppos = steps
        else:
            raise ValueError("Difference Target step pos and actual position " + str(steps) + " <-> " + str(sollpos))
        self.angle = self.steppos / self.stepsPerDegree
        return True

    ########################################################################
    def stepLeft(self,steps=1):
        #print(steps)
        if self.overLimits(self.angle + steps/self.stepsPerDegree): return False
        self.inmovement = True
        for i in range(steps):
            self.serconn.write(b'+\r\n')
            self.waitForOk()
            self.positionEnginesteps += 1
        self.angle = self.positionEnginesteps/self.stepsPerDegree
        self.inmovement = False
        return True

    ########################################################################
    def stepRight(self,steps=1):
        if self.overLimits(self.angle - steps/self.stepsPerDegree): return False
        self.inmovement = True
        for i in range(steps):
            self.serconn.write(b'-\r\n')
            self.waitForOk()
            self.positionEnginesteps -= 1
        self.angle = self.positionEnginesteps/self.stepsPerDegree
        self.inmovement = False
        return True

        ###########################################################################

    def getMeasurement(self, channel=1):
        '''
        Get the current power measurement of the sensor of channel 1 or 2
        :param channel: channel number
        :return: values in dBm
        '''

        P,angle,success = self.readPowerValue()
        PdBm1 = 10*log10(P/1e-3)
        PdBm2 = 10*log10(P/1e-3)
        PdBm1_str = str(PdBm1)
        PdBm2_str = str(PdBm2)
        #if PdBm1 > -18: PdBm1_str =  "-15"
        #if PdBm1 < -70: PdBm1_str = "-70"
        #if PdBm2 > -18: PdBm2_str = "-15"
        #if PdBm2 < -70: PdBm2_str = "-70"
        if DEBUG: print("PdBm", PdBm1)
        return (PdBm1, PdBm2)

    def getAngle(self):
        '''
        Gets the hardware position of table
        :return: angle in steps, angle in degrees
        '''
        self.steppos = self.stepsPerDegree * self.angle
        return self.steppos, self.angle

    def fullRun(self, nr_of_measpoints):
        '''
        Perform a full run on the table without Python interaction
        '''
        self.reset()
        #sleep(3)
        anglelist = []
        powerlist = []
        print("START FULL RUN")
        enginesteps_per_meas = int(360 * self.stepsPerDegree / nr_of_measpoints + 0.5)
        if DEBUG: print("ESPM:",enginesteps_per_meas)
        self.serconn.flushInput()
        self.serconn.flushOutput()
        degrees = -999
        while degrees <= 360:
            counter = 0
            print(counter)
            if degrees != self.angle:  # still moving
                P, degrees, success = self.readPowerValue()
                counter += 1
                if counter > 50:
                    raise RuntimeError("Position Mismatch")
            if DEBUG: print("MEASUREMENT ----------------------------- ", degrees, self.angle, P)
            anglelist.append(self.angle)
            powerlist.append(P)
            if degrees + enginesteps_per_meas / self.stepsPerDegree <= 361:
                if DEBUG: print("Move steps", enginesteps_per_meas)
                self.stepLeft(enginesteps_per_meas)
                if DEBUG: print("New Angle:", self.angle)
            else:
                break

        # self.stepRight(enginesteps_per_meas)  ## Go back i bit
        return array(anglelist), array(powerlist)

    ##########################################################################
    def readPowerValue(self, usefakedata = False):
        '''
        Get Data from Table

        Returns:
        --------
        P = float
                 Power in W
        '''
        rawdata = "None"
        try:
            data = "---"
            self.serconn.flushInput()
            while data[0:2] != "A ":
                rawdata = self.serconn.readline()
                if len(rawdata) == 0:
                    print("Timeout occured")
                    raise ConnectionRefusedError
                    return 0,0, 'Timeout'
                if DEBUG: print(rawdata)
                try:
                    data = (rawdata.rstrip()).decode('ascii')  # CR entfernen
                except:
                    continue
                if (not data):  data = "-"
                if "OK" in data:
                    #return 0,0, 'Received an OK in Value Read, this should not happen'
                    #raise ValueError("Received an OK in Value Read, this should not happen! data:"+data)
                    #print("Received an OK in Value Read, this should not happen! data:"+data)
                    pass
            winkel, V = self.ConvertToAngleVoltage(data)
            if V < 0.6:
               return 0,0, 'No active Power detector connected, check detector'
            # PdBm= -(V-0.55)/0.025     # V-b/m     ,   Geradengleichung x=y-b/m
            PdBm = -(V - 0.6488) / 0.0246  # nach MatLab, Messung mit ZX47-60+
            P = 1e-3 * power(10, (PdBm / 10))  # P in mW
            # print(P)
            if DEBUG: print("theta= {0:3.1f} deg V= {1:2.2f} V P= {2:3.2f} dBm P= {3:4.3f} nW".format(winkel, V, PdBm, (P * 1e9)))
            success = 'Ok'
        except: #Exception as inst:
            print("ReadPowerValue: Received Invalid Data:", rawdata)
            # raise ValueError("Received invalid Data: "+str(data))
            P = 0
            success = 'Invalid Data'
            winkel = -999
        self.steppos = self.stepsPerDegree * self.angle
        return P, self.angle, success

    ###### Convert LD Table Value into Voltage ######################
    def ConvertToAngleVoltage(self, line):
        '''
        Convert the Leybold String received from the table into a human readable format with angle and voltage
      Convert the Arduino String received from the table into a human readable format with angle and voltage

       | Datenwort ist formatiert wie folgt:
       | A 34,238, 125
       | 34,  Winkel in halben Grad
       | 238, ADC-Messwert als Integer
       | 125  ADC-Temperaturwert als Integer

        Returns
        --------
          winkel: Angle in degrees
          voltage
        '''

        datalist = line.split(',')
        rohwinkel = datalist[0]  # read angle raw
        rohwinkel = rohwinkel[1:]  # strip leading A
        #print("===>>",line)
        winkel = float(rohwinkel) / self.stepsPerDegree

        rohwert = datalist[1]  # read voltage raw
        if (int(rohwert) > 150000000):
            print("*******************************")
            print("********* OVERFLOW ************")
            print("*******************************")

        voltage=float(5./1023)*float(rohwert)    # Spannung in V
        return winkel, voltage


class Serial_thru_E5810():

    def __init__(self, device):
        self.device = device

    def readline(self):
        event = self.device.read_raw()
        return event

    def write(self,text):
        if DEBUG: print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Write to Table: ", text)
        self.device.write_raw(text)

    def flushInput(self):
        self.device.clear()
        return

    def flushOutput(self):
        return



class EhMatable_E5810(EhMatable):
    '''
    Connect to the Ehma Table thru E5810 DingsBums
    '''

    def __init__(self):
        super().__init__()
        self.comport = "E5810"
        pass


    def connect(self,fixport = ''):
        success = False
        try:
            rm = visa.ResourceManager()
            ipaddress = "192.168.111.210"
            con = "TCPIP::" + ipaddress + "::COM1"
            self.e5810 = rm.open_resource(con, timeout=1000)
            print("--connected--")
            self.portname = "E5810"
            self.serconn = Serial_thru_E5810(self.e5810)
            line = self.serconn.readline()
            count = 0
            while not b"A 0" in line:
                #self.serconn.write(b'v\r\n') # query Version
                line = self.serconn.readline()
                print("Received a ",line)
                count += 1
                if count >5:
                    print("Count reached 5, raise Exception")
                    #raise ConnectionRefusedError
                    return "Cannot Connect Time Out"

            if not b"A 0" in line:
                print('ERROR: Cannot identify a EhMa Table at E5810')
                return "Error Cannot identify a EhMa Table at E5810"
            line = "V 1.2 with degree fix Aug 2019"
            success = "Success"
            self.portname = "E5810"

        except Exception as mess:
            print("Connection to Table via E5810 failed ")
            print("Error:", mess)
            exit()
            print(mess.args[1])
        if success:
            print(self.name," connected in version ", line )
            return "success"
        else:
            return "Error"+mess

##################################################################################
##################################################################################

if __name__ == '__main__':

    mytable = EhMatable_E5810()
    success = mytable.connect(fixport='ethernet')
    if not success: exit()

    if False:
        mytable.reset()
        sleep(1)
        mytable.stepLeft(int(40*mytable.stepsPerDegree))
        sleep(1)
        mytable.stepRight(int(10*mytable.stepsPerDegree))
        sleep(1)
    for i in range(50000000):
        r = mytable.readPowerValue()
        print('Result:',r )

    ### do full run ############################################
    if False:
        alist, plist = mytable.fullRun(36)
        fig, ax = plt.subplots()
        ax.plot(alist, 10 * log10(plist))
        ax.set_xlabel('Angle in Degrees')
        ax.set_ylabel('Power in dBW')
        plt.show()
