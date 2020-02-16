# read data from grove moisture sensor
# see:
# https://docs.pycom.io/chapter/firmwareapi/pycom/machine/ADC.html
#
import machine
import time

# analog connectors on grove expansion board
# J5 (P15), J6 (P16)
adc = machine.ADC()             # create an ADC object
apin = adc.channel(pin='P15')   # create an analog pin on P15 (J5 connector)
while True:
    val = apin()                # read an analog value
    print("Analog read: {}".format(val))
    time.sleep(1)
    