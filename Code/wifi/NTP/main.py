import machine
from network import WLAN
import time

wlan = WLAN(mode=WLAN.STA)

nets = wlan.scan()
for net in nets:
    if net.ssid == 'WALC-2017':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, 'UtecWalc17'), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break

rtc = machine.RTC()
rtc.init((2015, 1, 1, 1, 0, 0, 0, 0))
print("Before NTP adjust", time.localtime())
print('Set RTC using ntp.org')
rtc.ntp_sync("pool.ntp.org")
time.sleep_ms(1000)
print(rtc.now())
print('Time set!')
print("The time is now: ", time.localtime())
print('----------------- end set rtc using ntp.org')
