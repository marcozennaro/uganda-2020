from machine import SD
import os
import time

# VERSION 1
# Writing a file in /flash folder
file_path = '/flash/log'

try:
    os.listdir('/flash/log')
    print('/flash/log file already exists.')
except OSError:
    print('/flash/log file does not exist. Creating it ...')
    os.mkdir('/flash/log')

name = '/my_first_file.log'

# Writing
with open(file_path + name, 'w') as f:
    f.write('Testing write operations in a file.')

# Reading
with open(file_path + name, 'r') as f:
    print(f.readall())
