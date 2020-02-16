from network import LoRa
import binascii
import struct

lora = LoRa(mode=LoRa.LORAWAN)

dev_addr = struct.unpack(">l", binascii.unhexlify('26041479'))[0]
nwk_swkey = binascii.unhexlify('8D026AA5E78EAE928977FA904041C708')
app_swkey = binascii.unhexlify('F0F87E520086F452F21EF7CF2AAE2A49')

lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

import socket
import time

while True:
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

    s.setblocking(False)
    s.send(bytes([1, 2, 3]))
    s.settimeout(5.0) # configure a timeout value of 3 seconds
    try:
       rx_pkt = s.recv(64)   # get the packet received (if any)
       print(rx_pkt)
    except socket.timeout:
      print('Waiting to send new packet')
