"""
---------------------------------------------------------------------
test grove sunlight sensor
https://www.seeedstudio.com/Grove-Sunlight-Sensor-p-2530.html

Author: Marco Rainone - Wireless Lab ICTP
email: mrainone@ictp.it
Ver: 0.1
Last Update: 29/04/2018
Based on the work by: 
   - Nelio Goncalves Godoi (neliogodoi@yahoo.com.br)
   - Joe Gutting (2014) (https://github.com/THP-JOE/Python_SI1145)
---------------------------------------------------------------------
"""


from machine import I2C
# for grove sunlight sensor
from drvsi1145 import SI1145
# for grove oled display
from ssd1308 import SSD1308_I2C
from writer import Writer
# Font
import myfont

import gc
import time

# --------------------------------------------------------
# main
#
# initialize sensor & display oled
# https://docs.pycom.io/pycom_esp32/library/machine.I2C.html
i2c = I2C(0, I2C.MASTER, baudrate=100000)
sensor = SI1145(objI2C=i2c)

# use grove oled display
grove_oled_display = SSD1308_I2C(objI2C=i2c)
display = Writer(grove_oled_display, myfont)
gc.collect()            # free ram

Writer.set_clip(True, True)

while True:
    uv = sensor.read_uv()
    vi = sensor.read_visible()
    ir = sensor.read_ir()
    pr = sensor.read_prox()
    str1 = '{} {}'.format(uv, vi)
    str2 = '{} {}'.format(ir, pr)

    gc.collect()            # free ram
    
    # display strings
    
    # write str1
    display.set_textpos(0, 4)            # set position (row, col)
    display.printstring(str1)
    gc.collect()            # free ram
    # write str2
    display.set_textpos(25, 20)          # set position (row, col)
    display.printstring(str2)

    display.show()
    gc.collect()            # free ram
    
    time.sleep(1)
