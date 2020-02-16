"""
---------------------------------------------------------------------
Test1 grove OLED display
http://wiki.seeedstudio.com/Grove-OLED_Display_0.96inch/
Show time read from time.sodaq.net

Author: Marco Rainone - Wireless Lab ICTP
email: mrainone@ictp.it
Ver: 0.1
Last Update: 29/04/2018
code released with MIT License (MIT)
---------------------------------------------------------------------
"""
# I2C connection 128x64 grove oled display to lopy
#    Pyb ----------- SSD
#    Gnd ----------- Gnd   27  black
#    3v3 ----------- Vin   26  red
#    Y10 ----------- DATA  11  white
#    Y9  ----------- CLK   12  yellow


import machine
from network import WLAN
import time
import socket
import utime

from machine import I2C
from ssd1308 import SSD1308_I2C
from writer import Writer
import gc
import ucollections
import utime
import time

gc.enable()         # enable garbage collector

# Fonts
import myfont

# --------------------------------------------------
# width, height oled display in pixel
WIDTH = const(128)
HEIGHT = 64

# --------------------------------------------------
# Main
#
# ---------------------------------------------------------
# initialize display oled
# https://docs.pycom.io/pycom_esp32/library/machine.I2C.html
i2c = I2C(0, I2C.MASTER, baudrate=100000)

# use grove oled display
grove_oled_display = SSD1308_I2C(i2c)
display = Writer(grove_oled_display, myfont)
gc.collect()            # free ram

# ---------------------------------------------------------
# setup wifi to read time
#
wlan = WLAN(mode=WLAN.STA)

# ssid = 'Vodafone-34172459'                            # <--- WIFI network name
# password = 'DwTXJxgq0mZ03zVRMhM2qsrSoUOIk8qW'                    # <--- WIFI network password
ssid = 'FabLab'                            # <--- WIFI network name
password = 'MakerFaire'                    # <--- WIFI network password

nets = wlan.scan()
for net in nets:
    if net.ssid == ssid:
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, password), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break
rtc = machine.RTC()
rtc.init((2015, 1, 1, 1, 0, 0, 0, 0))
print("Before network time adjust", rtc.now())
print('Setting RTC using Sodaq time server')
time.sleep(2)
s=socket.socket()
addr = socket.getaddrinfo('time.sodaq.net', 80)[0][-1]
s.connect(addr)
s.send(b'GET / HTTP/1.1\r\nHost: time.sodaq.net\r\n\r\n')
ris=s.recv(1024).decode()
s.close()
print("----------------- Web page read:")
print(ris)
print("--------------------------------")
rows = ris.split('\r\n')            # transform string in list of strings
seconds = rows[7]
print("After network time adjust")
rtc.init(utime.localtime(int(seconds)))
print(rtc.now())

# ---------------------------------------------------------
gc.collect()            # free ram

Writer.set_clip(True, True)
# Writer.set_textpos(20, 20)
# Writer._printchar(' ')
# wri2.printstring("A")
# ------------------
# ok
# for x in range(20, 127):
#     for y in range(20, 63):
#         ssd.pixel(x,y, 1)            # display pixel
# for n in range(30, 50):
#     ssd.pixel(n,n, 0)                # display pixel
# ------------------
# Writer._printchar('B')
# set position to write msg

count = 0
while True:
    # print("---------------------------------[{}".format(count))
    count = count+1
    # read timer
    now = time.time()
    dtr = time.localtime(now)
    
    strDate = "{0:04d}/{1:02d}/{2:02d}\n".format(dtr[0], dtr[1], dtr[2])
    if ((count & 1) == 1):
        strTime = "{0:02d}:{1:02d}:{2:02d}\n".format(dtr[3], dtr[4], dtr[5])
    else:
        strTime = "{0:02d} {1:02d} {2:02d}\n".format(dtr[3], dtr[4], dtr[5])
    gc.collect()            # free ram
        
    print("Time [{}]: {},{},{},{},{},{}".format(count, dtr[0], dtr[1], dtr[2], dtr[3], dtr[4], dtr[5]))
    
    gc.collect()            # free ram
    
    # display strings
    
    # write date
    display.set_textpos(0, 4)            # set position (row, col)
    display.printstring(strDate)
    gc.collect()            # free ram
    # write time
    display.set_textpos(32, 20)          # set position (row, col)
    display.printstring(strTime)

    display.show()
    gc.collect()            # free ram
    
    time.sleep_ms(250)

