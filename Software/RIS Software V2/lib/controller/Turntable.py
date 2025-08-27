'''
Parent Class for all Turntable Hardware in the Microwave lab

defines an (abstract) turntable class that acts as parent for specific turntables
it also acts as a generic synthetic table

S. Peik, July 2019

'''

from numpy import nan, abs, sinc, array, log10, sqrt
from numpy.random import normal,randint
from time import sleep
#from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import matplotlib.pyplot as plt



class Turntable():

    def __init__(self, name ="Generic Table"):

        self.limits = (0.0,370.0)  # Absolut Limits without damage of Hardware in degrees
        self.stepsPerDegree = 2 #1.86   # Engine steps to produce one degree turn
        self.buffersize = 1024  # serial buffer in bytes
        self.positionEnginesteps = 0  # position in engine steps
        self.positionDegrees = self.positionEnginesteps/self.stepsPerDegree
        self.isconnected = False
        self.isSynthetic = True
        self.inmovement = False
        self.insleep = False
        self.name = name
        self.portname = "None"
        self.errorMessage = ""
        self.name = 'Synthetic Table'
        self.version = 'Generic Table Version 1.0.0'
        self.degreeSteps = []
        self.degreeSteps_steps = []
        self.stepspeed = 0.005   # time it takes for one engine step in the simulated table
        self.angularVelocity =  1/self.stepspeed # maximum angular velocity in degrees per second, useful for wait loops
        self.noise = 0.05
        self.broken = False

    def connect(self,port=None):
        if port !=None:
            print("This is the abstract class, port spec "+port+ " not used")
        print(self.name,"Table connected to abstract Generic Synthetic Table")
        self.isSynthetic = True
        return 'success'

    def reset(self):
        self.inmovement = True
        try:
            print("Moving Back!!!")
            sleep(self.positionDegrees/self.angularVelocity)
            print("-- Done --")
        except:
            pass
        self.inmovement = False
        self.positionEnginesteps = 0
        self.positionDegrees = self.positionEnginesteps / self.stepsPerDegree

    def setPosition(self,step):
        self.positionEnginesteps = step
        self.positionDegrees = self.positionEnginesteps/self.stepsPerDegree

    def stepLeft(self,steps=1):
        if self.overLimits(self.positionEnginesteps + steps): return False
        self.inmovement = True
        self.positionEnginesteps += steps
        self.positionDegrees = self.positionEnginesteps/self.stepsPerDegree
        sleep(self.stepspeed)
        self.inmovement = False
        return True

    def stepRight(self,steps=1):
        if self.overLimits(self.positionEnginesteps - steps): return False
        self.inmovement = True
        self.positionEnginesteps -= steps
        self.positionDegrees = self.positionEnginesteps/self.stepsPerDegree
        sleep(self.stepspeed)
        self.inmovement = False
        return True

    def overLimits(self, newposition):
        #print("checkoverlimit",newposition, self.limits)
        if newposition/self.stepsPerDegree > self.limits[1]:
            self.errorMessage = "OVER ANGLE LIMIT"
            print(self.errorMessage, newposition/self.stepsPerDegree)
            return self.errorMessage
        if newposition/self.stepsPerDegree < self.limits[0]:
            self.errorMessage = "UNDER ANGLE LIMIT"
            print(self.errorMessage, newposition/self.stepsPerDegree)
            return self.errorMessage
        return False

    def readPowerValue(self):
        '''
        Reads the measured power of the sensor and return value in W
        :return: power in W (float)
        '''
        sleep(.01)
        angle = self.positionDegrees
        angle = angle - 360 * (angle > 180) # set angle to -180 to 180 degree range
        Efield =  sqrt(0.5e-5) * abs(sinc(4.5 * (angle - 5.0) / 180))
        Efield += sqrt(1e-6)  * normal(0, self.noise)
        P = Efield ** 2

        ### Simulate broken Tabledata ####################
        if self.broken:
            sleep(0.1)
            zufall = randint(0,300)
            if zufall == 42: self.broken = False
            return 0, 0, 'Simulated Error'

        if False:  ## Simulate Errors #############
            zufall = randint(0,100)
            if zufall == 42:
                self.broken = True
                sleep(0.2)
                return 0,0, 'Simulated Error'

        return P, self.positionDegrees, 'Ok'

    def flush(self):
        pass

##################################################################################
##################################################################################

if __name__ == '__main__':
    mytable = Turntable()
    success = mytable.connect('/dev/ttyXXX0')
    print("Success:", success)
    P = mytable.readPowerValue()
    #print(mytable.positionEnginesteps,mytable.positionDegrees,P)

    mytable.reset()
    data = []
    for step in range(0,800):
        success = mytable.stepLeft()
        if not success:
            print("No Success, end scan due to", mytable.errorMessage)
            mytable.errorMessage = "" # reset error
            break
        P = mytable.readPowerValue()
        data.append([mytable.positionDegrees,P])
        print(mytable.positionEnginesteps, mytable.positionDegrees, P)

    ## Plot result ###################################################
    array = array(data)
    plt.plot(array[:,0],10*log10(array[:,1]))
    plt.show()


