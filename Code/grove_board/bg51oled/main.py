"""
---------------------------------------------------------------------
example of bg51 radiation sensor data acquisition
Display radiation info in oled display
Author: Marco Rainone - Wireless Lab ICTP
email: mrainone@ictp.it
Ver: 0.1
Last Update: 01/05/2018
code released with MIT License (MIT)
---------------------------------------------------------------------
"""

import machine
from machine import Pin
from machine import Timer
from machine import I2C
import time
import utime
import array
from tblmsvh import pulses2mSv
# for grove oled display
from ssd1308 import SSD1308_I2C
from writer import Writer
# Font
import myfont
import gc


# radiation sensor to P17 input Pin
sigBg51 = Pin("P17", mode=Pin.IN, pull=None)

# buzzer to digital connector J7 or J8
#  J7 connector: to I/O Pin 'P12'     
#  J8 connector: to I/O Pin 'P11'     
buz = Pin('P11', mode=Pin.OUT)          # conn. J8
# buz = Pin('P12', mode=Pin.OUT)        # conn. J7

seconds = 0
fNewSec = 0
tmUpdateOled = 0                        # time update display in sec
fUpdateOled = False
minutes = 0
oldcounter = 0
actCnt = 0
counter = 0
tm_init_app = utime.ticks_ms()
tm_start = tm_init_app
tm_end = tm_start
# array of unsigned short. It it used as queue to store the pulses count for every second 
countsSec = array.array('H',(0 for i in range(0,60)))
# counts for minutes
countsMin = 0

# using the data queue countsSec, calculates the number of pulses read in one minute
def pulses_min():
    global countsSec
    counts = 0
    for i in range(0,60):
        counts = counts + countsSec[i]
    return counts

# used to debug: print values on countsSec queue
def strCounts():
    str = ""
    for i in range(0,60):
        str = str + "{}".format(countsSec[i])
    return str
    
# BG51 rise signal interrupt routine.
# experimentally it has been estimated that the duration of the increment
# instruction (Mean time) is 5.965us
def riseBg51(pin):
    global counter
    counter = counter + 1

# timer interrupt handler: increment of one second
def seconds_handler(alarm):
    global seconds
    global minutes
    global countsSec
    global actCnt
    global fNewSec
    global tmUpdateOled
    global fUpdateOled
    # global countsMin
    # countsMin = pulses_min()
    seconds += 1
    if seconds>=60:
        minutes += 1
        seconds=0
    # countsSec[seconds] = 0
    countsSec[seconds] = actCnt
    actCnt = 0
    fNewSec = True
    tmUpdateOled += 1
    if tmUpdateOled >= 2:
        tmUpdateOled = 0
        fUpdateOled = True      

def buzzerON_timer(alarm):
    global buz
    buz.value(0)
    Timer.Alarm(buzzerOFF_timer, ms=5, periodic=False)

def buzzerOFF_timer(alarm):
    global fBuzzer
    fBuzzer = False
    
def minutes_handler(alarm):
    global minutes
    global countsMin
    minutes += 1
    countsMin = 0

def MinSec():
    global tm_init_app
    dtime_ms = utime.ticks_diff(tm_init_app, utime.ticks_ms())
    # return min, sec
    min = dtime_ms // 60000
    sec = dtime_ms % 60000
    sec = sec / 1000
    # ris = "{:6d}m {: >2.1f}s".format(min, sec)
    ris = "{}m {: >2.1f}s".format(min, sec)
    return(ris)

# initialize display oled
# https://docs.pycom.io/pycom_esp32/library/machine.I2C.html
i2c = I2C(0, I2C.MASTER, baudrate=100000)
# use grove oled display
grove_oled_display = SSD1308_I2C(objI2C=i2c)
display = Writer(grove_oled_display, myfont)
gc.collect()            # free ram
Writer.set_clip(True, True)
    
print("Start measurement:")
alarmTimer = Timer.Alarm(seconds_handler, 1, periodic=True)
# buzTimer = Timer.Alarm(buzzerON_timer, us=1000, periodic=True)
# alarmTimer = Timer.Alarm(minutes_handler, 60, periodic=True)
sigBg51.callback(Pin.IRQ_RISING, riseBg51)
fBuzzer = False
while True:
    gc.collect()            # free ram

    # check if new minute
    if utime.ticks_diff(tm_start, tm_end) >= 60000:
        # changed minutes
        tm_start = tm_end
        # ----------------------------------------------------
        # here log data or transfer info
        
        # end
        # ----------------------------------------------------
        # spostato in minutes_handler countsMin = 0
        
    # check if new pulses
    if counter != oldcounter:
        machine.disable_irq()
        # add pulses
        tm_end = utime.ticks_ms()
        incPulses = counter - oldcounter
        actCnt = actCnt + incPulses
        oldcounter = counter
        machine.enable_irq()
        # buzzer ON and set timer
        # fBuzzer = True
        # buz.value(fBuzzer)
        # timeBuz = utime.ticks_us()
        buz.value(1)
        for i in range(0,10):
            pass
        buz.value(0)
        for i in range(0,200):
            pass
        # if fBuzzer == False:
        #     fBuzzer = True
        #     buz.value(1)
        #     Timer.Alarm(buzzerON_timer, ms=1, periodic=False)
        # time.sleep_us(200)
    # buz.value(0)
    
    if fNewSec == True:
        # show data info
        fNewSec = False
        countsMin = pulses_min()
        strTime = "{}".format(MinSec())
        strCounts = '{}'.format(countsMin)
        msv_h = pulses2mSv(1, countsMin)
        strMsv_h = '{: >3.6f}'.format(msv_h)
        
        if seconds %2 == 0:
            # if seconds even, update display
            # show full info on repl terminal
            # print('{: >15}: Tot.pulses: {:8d} pulses/min: {:4d} msv/h {: >3.6f}'.format(MinSec(), counter, countsMin, pulses2mSv(1, countsMin)))
            print('{: >15}: Tot.pulses: {:8d} puls/min: {} mSv/h: {}'.format(strTime, counter, strCounts, strMsv_h))
        else:
            # seconds odd, update oled
            display.set_textpos(0, 4)            # set position (row, col)
            display.printstring(strTime)
            gc.collect()            # free ram
            display.set_textpos(22, 4)           # set position (row, col)
            display.printstring(strCounts)
            gc.collect()            # free ram
            display.set_textpos(42, 4)           # set position (row, col)
            display.printstring(strMsv_h)
            gc.collect()            # free ram
            display.show()
            gc.collect()            # free ram
        
        # print('{}'.format(strCounts()))
    
    # check if buzzer is ON
    # if fBuzzer:
    #     # buzzer ON. Check time buzzer ON
    #     if utime.ticks_diff(timeBuz, utime.ticks_us())>=200:
    #         # buzzer off
    #         fBuzzer = False
    #         buz.value(fBuzzer)
