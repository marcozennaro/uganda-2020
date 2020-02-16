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
from drvsi1145 import SI1145
import time

# --------------------------------------------------------
# main
#
i2c = I2C(0, I2C.MASTER, baudrate=100000)
sensor = SI1145(objI2C=i2c)

while True:
    uv = sensor.read_uv()
    vi = sensor.read_visible()
    ir = sensor.read_ir()
    pr = sensor.read_prox()
    print('UV Index : {}'.format(uv))
    print('Vis + IR : {}'.format(vi))
    print('IR       : {}'.format(ir))
    print('Proximity: {}'.format(pr))

    time.sleep(1)
