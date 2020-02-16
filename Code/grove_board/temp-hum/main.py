"""
---------------------------------------------------------------------
Test1 grove temperature/humidity sensor DHT11
https://www.seeedstudio.com/Grove-TempHumi-Sensor-p-745.html
#
Author: Marco Rainone - Wireless Lab ICTP
email: mrainone@ictp.it
Ver: 0.1
Last Update: 01/05/2018
Based on this work:
https://github.com/JurassicPork/DHT_PyCom/tree/pulses_get
code released with MIT License (MIT)
---------------------------------------------------------------------
"""
# from:
# https://github.com/JurassicPork/DHT_PyCom/tree/pulses_get
#
import pycom
import time
from machine import Pin
from dth import DTH

# connect the grove temperature/humidity (DHT11) sensor to digital connector J7 or J8
#  J7 connector: to I/O Pin 'P12'     
#  J8 connector: to I/O Pin 'P11'     

# Instantiate the DHT class with these parameters:
# 1) the pin number
# 2) type of sensor: 0 for DTH11, 1 for DTH22
th = DTH('P11',0)

# loop to read temperature / humidity from DHT11
# 
time.sleep(2)
while True:
    # Call read() method, which will return DHTResult object with actual values and error code.
    result = th.read()
    if result.is_valid():
        print("Temperature: {} C".format(result.temperature))
        print("Humidity: {}%".format(result.humidity))
    else:
        print("Error reading sensor !")
    time.sleep(2)
    