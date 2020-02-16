# test Ambient light sensor LTR-329ALS-01
# http://optoelectronics.liteon.com/en-global/Home/index
#
from pysense import Pysense
from LTR329ALS01 import LTR329ALS01
import math
import pycom
import micropython
import machine
import time

# Convert raw data in CH0 & CH1 registers to lux
# Input:
# CHRegs: register values, results of lux() function
# returns the resulting lux calculation
#         lux = -1 IF EITHER SENSOR WAS SATURATED (0XFFFF) OR CHRegs[0] == 0x0000
def raw2Lux(CHRegs):
    # initial setup.
    # The initialization parameters in LTR329ALS01.py are:
    # gain: ALS_GAIN_1X, integration time: ALS_INT_100
    #
    gain = 0                        # gain: 0 (1X) or 7 (96X)
    integrationTimeMsec = 100       # integration time in ms

    # Determine if either sensor saturated (0xFFFF)
    # If so, abandon ship (calculation will not be accurate)
    if ((CHRegs[0] == 0xFFFF) or (CHRegs[1] == 0xFFFF)):
        lux = -1
        return(lux)
    # to calc correctly ratio, the CHRegs[0] must be != 0
    if (CHRegs[0] == 0x0000):
        lux = -1
        return(lux)
    
    # Convert from unsigned integer to floating point
    d0 = float(CHRegs[0])
    d1 = float(CHRegs[1])

    # We will need the ratio for subsequent calculations
    ratio = d1 / d0;

    # Normalize for integration time
    d0 = d0 * (402.0/integrationTimeMsec)
    d1 = d1 * (402.0/integrationTimeMsec)

    # Normalize for gain
    if (gain == 0):
        d0 = d0 * 16
        d1 = d1 * 16

    # Determine lux per datasheet equations:
    if (ratio < 0.5):
        lux = 0.0304 * d0 - 0.062 * d0 * math.pow(ratio,1.4)
        return(lux)

    if (ratio < 0.61):
        lux = 0.0224 * d0 - 0.031 * d1
        return(lux)

    if (ratio < 0.80):
        lux = 0.0128 * d0 - 0.0153 * d1
        return(lux)

    if (ratio < 1.30):
        lux = 0.00146 * d0 - 0.00112 * d1
        return(lux)

    lux = 0.0           # if (ratio > 1.30)
    return(lux)

# -----------------------------------------------------------

py = Pysense()
ambientLight = LTR329ALS01(py)              # class 
while True:
    data = []
    # get 16 bit CH0 & CH1 registers
    data = ambientLight.lux()
    # print CH0 & CH1 registers
    LuxValue = raw2Lux(data)
    print("Read Ambient Light registers: {}   Lux: {}".format(data, LuxValue))
    time.sleep(1)
