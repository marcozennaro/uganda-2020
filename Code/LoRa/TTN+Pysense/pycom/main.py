# ---------------------------------------------------------------------
# Lopy program to acquire data from pysense board
# and send them to TTN via LoraWan
# Ver 1.0 2019/03/25
# ---------------------------------------------------------------------
#
import machine
import pycom
from pysense import Pysense
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE
import micropython
import machine
from network import LoRa
import socket
import struct
import binascii
import ubinascii
import sys
import time
import utime

# pycom.heartbeat(False)
# pycom.rgbled(0x000000)

# ----------------- Pysense sensor initialization
py = Pysense()
# The MPL3115A2 returns height in meters.
# Mode may also be set to PRESSURE, returning a value in Pascals
# Sensor Data limits:
# Altitude: 20-bit: –698 to 11775 m
# Temperature: 12-bit: -40 C to 85 C
SensPress = MPL3115A2(py,mode=ALTITUDE)

# ----------------- activating LoRa
print("activating LoRa")
lora = LoRa(mode=LoRa.LORAWAN)
#
# key for pysense-001 , ABP activation
dev_addr = struct.unpack(">l", binascii.unhexlify('26011984'))[0]
nwk_swkey = binascii.unhexlify('5ECF005491EC779608B81BDD50D90C1D')
app_swkey = binascii.unhexlify('462175A1109541A7AF1342374F3628D7')
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
time.sleep(5)



print("start loop")
while True:
     # ----------------- get data from MPL3115A2 sensor
    temperature = SensPress.temperature()
    altitude = SensPress.altitude()
    # DEBUG
    print("Temperature: {} Degrees  Altitude: {}".format(temperature, altitude))
    #
    # ---------------------------------------------
    # PREPARE LORA MSG
    # ---------------------------------------------
    # The measurements to be sent on TTN must have one decimal place after the comma
    #
    # table of msg fields:
    # n | Id            | example   | lim. values           | lim rapr.    | n. bytes | start pos.
    # 1 | temperature   | 21.9      | -40.0 C to 85.0 C     | 0 .. 1250    | 2        | 0
    # 2 | altitude      | 118.4     | –698.0 to 11775.0 m   | 0 .. 124730  | 3        | 2
    # n. bytes payload: 5
    # Index range of array: 0..4
    msgLora = bytearray(5)
    # ----------------- initialize lora msg
    # set rapresentation of temperature value
    pos=0
    value = int( ( (temperature + 40.0 ) * 10.0 ) + 0.5 )
    msgLora[pos+0] = (value >> 8) & 0xff
    msgLora[pos+1] = (value) & 0xff

    # set rapresentation of altitude value
    pos=2
    value = int( ( (altitude + 698.0 ) * 10.0) + 0.5 )
    msgLora[pos+0] = (value >> 16) & 0xff
    msgLora[pos+1] = (value >> 8) & 0xff
    msgLora[pos+2] = (value) & 0xff
    #
    # ----------------- END OF LORA MSG PREPARATION
    # DEBUG
    print(msgLora)
    # ----------------- send msgLora to TTN via LoraWan
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    s.send(msgLora)                     # send data to TTN
    #
    print("----------------------------[END MSG TX LORA]")
    #
    # ---------------------------------------------
    #
    time.sleep(15)                      # wait 15 seconds
