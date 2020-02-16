"""
---------------------------------------------------------------------
example of bg51 radiation sensor data acquisition

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
import time
import utime
import array
from tblmsvh import pulses2mSv

# radiation sensor to P17 input Pin
sigBg51 = Pin("P17", mode=Pin.IN, pull=None)

# buzzer to digital connector J7 or J8
#  J7 connector: to I/O Pin 'P12'     
#  J8 connector: to I/O Pin 'P11'     
buz = Pin('P11', mode=Pin.OUT)          # conn. J8
# buz = Pin('P12', mode=Pin.OUT)        # conn. J7

seconds = 0
fNewSec = 0
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
    ris = "{:6d}m {: >2.1f}s".format(min, sec)
    return(ris)

    
print("Start measurement:")
alarmTimer = Timer.Alarm(seconds_handler, 1, periodic=True)
# alarmTimer = Timer.Alarm(minutes_handler, 60, periodic=True)
sigBg51.callback(Pin.IRQ_RISING, riseBg51)
fBuzzer = 0
while True:
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
        fBuzzer = True
        buz.value(fBuzzer)
        timeBuz = utime.ticks_us()
    
    if fNewSec == True:
        # show data info
        fNewSec = False
        countsMin = pulses_min()
        # print('tm: {: >15}, min {:5d}, impulse {:8d} pulses/min: {:4d} msv/h {: >3.6f}'.format(MinSec(), minutes, counter, countsMin, pulses2mSv(1, countsMin)))
        print('{: >15}: Tot.pulses: {:8d} pulses/min: {:4d} msv/h {: >3.6f}'.format(MinSec(), counter, countsMin, pulses2mSv(1, countsMin)))
        # print('{}'.format(strCounts()))
    
    # check if buzzer is ON
    if fBuzzer:
        # buzzer ON. Check time buzzer ON
        if utime.ticks_diff(timeBuz, utime.ticks_us())>=1000:
            # buzzer off
            fBuzzer = False
            buz.value(fBuzzer)
