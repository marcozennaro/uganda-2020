# Some useful functions "ufun":

from network import WLAN
import machine
import math
import pycom
import sys
import time
import ucrypto

RED = 0xFF0000
YELLOW = 0xFFFF33
GREEN = 0x007F00
OFF = 0x000000

def random_in_range(l=0,h=1000):
    r1 = ucrypto.getrandbits(32)
    r2 = ((r1[0]<<24)+(r1[1]<<16)+(r1[2]<<8)+r1[3])/4294967295.0
    return math.floor(r2*h+l)

def set_led_to(color=GREEN):
    pycom.heartbeat(False) # Disable the heartbeat LED
    pycom.rgbled(color)

def flash_led_to(color=GREEN, t1=1):
    set_led_to(color)
    time.sleep(t1)
    set_led_to(OFF)

def connect_to_wifi(wifi_ssid, wifi_passwd):
    wlan = WLAN(mode=WLAN.STA)

    for ltry in range(3):
        print("Connecting to: "+wifi_ssid+". Try "+str(ltry))
        nets = wlan.scan()
        for net in nets:
            if net.ssid == wifi_ssid:
                print('Network '+wifi_ssid+' found!')
                wlan.connect(net.ssid, auth=(net.sec, wifi_passwd), timeout=5000)
                while not wlan.isconnected():
                    machine.idle() # save power while waiting
                break
        if wlan.isconnected():
            break
        else:
            print('Cannot find network '+wifi_ssid)
            flash_led_to(RED, 1)
    
    if not wlan.isconnected():
        print('Cannot connect to network '+wifi_ssid+'. Quitting!!!')
        sys.exit(1)
    else:
        print('WLAN connection succeeded!')
        flash_led_to(GREEN, 1)
        print (wlan.ifconfig())

