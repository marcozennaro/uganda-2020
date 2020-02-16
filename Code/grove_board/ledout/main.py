# test led
import time

from machine import Pin
out1 = Pin('P11', mode=Pin.OUT)     # conn. J8
out2 = Pin('P12', mode=Pin.OUT)     # conn. J7
out1.value(1)
out2.value(1)
time.sleep(1)

while True:
    out1.toggle()
    out2.toggle()
    time.sleep(1)
