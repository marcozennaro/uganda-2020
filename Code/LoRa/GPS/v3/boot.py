from machine import UART
import machine
from pytrack import Pytrack
import utime
import pycom

start = utime.ticks_us()
uart = UART(0, baudrate=115200)
os.dupterm(uart)

machine.main('main.py')

end = utime.ticks_us()
took = end - start
print("boot.py ... done in: {} uSec".format(took))
