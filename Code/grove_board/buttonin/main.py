# test digital connector J7/J8

from machine import Pin
import time
# make P11, P12 an input with the pull-up enabled
p1 = Pin('P11', mode=Pin.IN, pull=Pin.PULL_UP)
p2 = Pin('P12', mode=Pin.IN, pull=Pin.PULL_UP)
while True:
    print("{}-{}".format(p1(), p2()))
    time.sleep_ms(200)

