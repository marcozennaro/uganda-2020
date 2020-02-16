import machine
import config
from network import WLAN
wlan = WLAN(mode=WLAN.STA, antenna=WLAN.INT_ANT)

print(config.ssid)

nets = wlan.scan()
for net in nets:
    if net.ssid == config.ssid:
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, config.password), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break

print(wlan.ifconfig())
