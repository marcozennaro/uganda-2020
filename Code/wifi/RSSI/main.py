import machine
from network import WLAN
wlan = WLAN(mode=WLAN.STA)

nets = wlan.scan()
print(nets)

while True:
    for net in nets:
        print(net.ssid, net.rssi)
