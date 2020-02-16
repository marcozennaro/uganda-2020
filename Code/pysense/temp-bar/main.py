# test sensor MPL3115A2: I2C Barometric Pressure/Altitude/Temperature Sensor
# use official library
#
# http://www.nxp.com/assets/documents/data/en/data-sheets/MPL3115A2.pdf
# https://docs.pycom.io/pycom_esp32/library/machine.I2C.html
#
from pysense import Pysense
from MPL3115A2 import MPL3115A2
import pycom
import micropython
import machine
import time

py = Pysense()
pressure = MPL3115A2(py)

while True:
    temperature = pressure.temp()
    altitude = pressure.alt()
    print("Temperature: {} Degrees  Altitude: {}".format(temperature, altitude))
    time.sleep(1)
