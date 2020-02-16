# test sensor MPL3115A2: I2C Barometric Pressure/Altitude/Temperature Sensor
# http://www.nxp.com/assets/documents/data/en/data-sheets/MPL3115A2.pdf
# https://docs.pycom.io/pycom_esp32/library/machine.I2C.html

from machine import I2C
import time

MPL3115Address = const(0x60)                # address MPL3115A2

OSTbit = const(0x01)
ALTbit = const(0x80)

# see REGISTER DESCRIPTION, pag 18 datasheet
STATUS = const(0x00)                # Sensor status register

OUT_P_MSB = const(0x01)             # Pressure data out MSB
OUT_P_CSB = const(0x02)
OUT_P_LSB = const(0x03)

OUT_T_MSB = const(0x04)             # Temperature data out MSB 
OUT_T_LSB = const(0x05)

DR_STATUS = const(0x05)             # Data ready status information

WHO_AM_I = const(0x0C)              # Device identification register (always 0xC4)                  

PT_DATA_CFG = const(0x13)           # Data event flag configuration

CTRL_REG1 = const(0x26)             # Modes, oversampling
CTRL_REG2 = const(0x27)             # Acquisition time step
CTRL_REG3 = const(0x28)             # Interrupt pin configuration
CTRL_REG4 = const(0x29)             # Interrupt enables
CTRL_REG5 = const(0x2A)             # Interrupt output pin assignment

OFF_P = const(0x2B)                 # Pressure offset correction register
OFF_T = const(0x2C)                 # Temperature offset correction register
OFF_H = const(0x2D)                 # Altitude offset correction register 

# reads one byte over I2C
def IIC_Read(regAddr):
    data = bytearray(1)
    counter = 0
    nBytes = 0
    while True:
        nBytes = i2c.readfrom_mem_into(MPL3115Address, regAddr, data)
        if nBytes == 1:
            break
        counter = counter + 1
        if(counter > 500):
            # Error out after max of 512ms for a read
            return(0x00)
        time.sleep_ms(1)            # wait 1msec
    return(data[0])

# writes one byte to I2C
def IIC_Write(regAddr, value):
    wr = bytearray(1)
    wr[0] = value
    counter = 0
    nBytes = 0
    while True:
        nBytes = i2c.writeto_mem(MPL3115Address, regAddr, wr)
        if nBytes == 1:
            break
        counter = counter + 1
        if(counter > 500):
            # Error out after max of 512ms for a read
            return(0x00)
        time.sleep_ms(1)            # wait 1msec
    return(wr[0])

# Software resets the MPL3115A2.
# It must be in standby to change most register settings
def DeviceReset():
    # page 34
    # during reset the I2C communication system is reset 
    # to avoid accidental corrupted data access
    wr = bytearray(1)
    wr[0] = 0x04                        # Set RST (bit 2) to 1
    try:
        i2c.writeto_mem(MPL3115Address, CTRL_REG1, wr)      
    except:
        pass
    
    time.sleep_ms(10)
    counter = 0
    while True:
        value = IIC_Read(CTRL_REG1)     # Read contents of register CTRL_REG1
        if (value & 0x04) == 0x00:
            break
        counter = counter + 1
        if(counter > 500):
            return False
    
    return True
    
# Sets the MPL3115A2 to standby mode.
# In standby mode you can change most register settings
def DeviceStandby():
    value = IIC_Read(CTRL_REG1)     # Read contents of register CTRL_REG1
    value = value & 0xFE            # Set SBYB (bit 0) to 0
    IIC_Write(CTRL_REG1, value) 

# Sets the MPL3115A2 to active mode.
# Needs to be in this mode to output data
def DeviceActive():
    value = IIC_Read(CTRL_REG1)     # Read contents of register CTRL_REG1
    value = value | 0x01            # Set SBYB (bit 0) to 1
    IIC_Write(CTRL_REG1, value) 

# set offset correction
def SetOffsetCorrection(RegOff, value):
    if ((RegOff<OFF_P) or (RegOff>OFF_H)):
        return
    IIC_Write(RegOff, value) 

# convert temp degrees to offset
def Temp2Offset(degrees):
    offs = int(degrees * 16.0)
    return(offs)
    
# Sets the over sample rate. 
# Call with a rate from 0 to 7. 
# See page 33 for table of ratios.
# Datasheet calls for 128 but you can set it from 1 to 128 samples. 
# The higher the oversample rate the greater the time between data samples.
def setOversampleRate(sampleRate):
    if(sampleRate > 7): 
        sampleRate = 7              # OS cannot be larger than 0b.0111
    sampleRate = sampleRate << 3    # Align it for the CTRL_REG1 register
  
    value = IIC_Read(CTRL_REG1)     # Read contents of register CTRL_REG1
    value = value & 0xC7            # B11000111: Clear out old OS bits
    value = value | sampleRate      # Mask in new OS bits
    IIC_Write(CTRL_REG1, value) 

# Enables the pressure and temp measurement event flags so that we can
# test against them. 
# This is recommended in datasheet during setup.
def enableEventFlags():
    IIC_Write(PT_DATA_CFG, 0x07)    # Enable all three pressure and temp event flags 
    
# Sets the mode to Altimeter
# uses: CTRL_REG1, ALT bit
def setModeAltimeter():
    DeviceStandby()                     # put device in standby mode to allow write to registers
    value = IIC_Read(CTRL_REG1)         # Read current settings
    value = value | 0x80                # Set ALT bit
    IIC_Write(CTRL_REG1, value)         
    DeviceActive()                      # Set to active to start reading

# Sets the mode to Barometer
# uses: CTRL_REG1, ALT bit
def setModeBarometer():
    DeviceStandby()                     # put device in standby mode to allow write to registers
    value = IIC_Read(CTRL_REG1)         # Read current settings
    value = value & 0x7F                # Clear ALT bit
    IIC_Write(CTRL_REG1, value)
    DeviceActive()                      # Set to active to start reading

    
# Clears then sets the OST bit which causes the sensor to immediately take another reading
# Needed to sample faster than 1Hz
def toggleOneShot():
    DeviceActive()                      # Set to active to start reading
    value = IIC_Read(CTRL_REG1)         # Read current settings
    value = value & 0xFD                # Clear OST bit (bit 1)
    IIC_Write(CTRL_REG1, value)       
    
    value = IIC_Read(CTRL_REG1)         # Read current settings to be safe
    value = value | 0x02                # Set OST bit
    IIC_Write(CTRL_REG1, value)       

def readTemperature():
    if(IIC_Read(STATUS) & 0x02 == 0):
        # Toggle the OST bit causing the sensor to immediately take another reading
        toggleOneShot()
    # Wait for TDR bit, indicates we have new temp data
    counter = 0
    while( (IIC_Read(STATUS) & 0x02) == 0):
        counter = counter + 1
        if(counter > 600):
            # Error out after max of 512ms for a read
            return(-400)
        time.sleep_ms(1)

    # Read temperature registers
    data = bytearray(2)
    counter = 0
    nBytes = 0
    while True:
        nBytes = i2c.readfrom_mem_into(MPL3115Address, OUT_T_MSB, data)
        if nBytes == 2:
            break
        counter = counter + 1
        if(counter > 500):
            # Error out after max of 512ms for a read
            return(0x00)
        time.sleep_ms(1)            # wait 1msec

    msb = data[0]
    lsb = data[1]

    value = (msb << 8) | lsb
    # Convert the data to 12-bits
    temp = (value) >> 4
    if((msb & 0x80) == 0x80):
        # the temperature is negative
        temp = ~(temp) + 1  

    # Toggle the OST bit causing the sensor to immediately take another reading
    toggleOneShot()

    # temperature in degrees
    temperature = float(temp) / 16.0
    return(temperature)
    
# Returns the number of meters above sea level
# Returns -1 if no new data is available
def readAltitude():
    toggleOneShot()         # Toggle the OST bit causing the sensor to immediately take another reading

    # Wait for PDR bit, indicates we have new data
    counter = 0
    while( (IIC_Read(STATUS) & 0x02) == 0):
        counter = counter + 1
        if(counter > 600):
            # Error out after max of 512ms for a read
            return(-1)
        time.sleep_ms(1)

    # Read pressure registers
    data = bytearray(3)
    counter = 0
    nBytes = 0
    while True:
        nBytes = i2c.readfrom_mem_into(MPL3115Address, OUT_P_MSB, data)
        if nBytes == 3:
            break
        counter = counter + 1
        if(counter > 500):
            # Error out after max of 512ms for a read
            return(0x00)
        time.sleep_ms(1)            # wait 1msec

    msb = data[0]
    csb = data[1]
    lsb = data[2]

    value = (msb << 16) | (csb << 8) | lsb
    value = value >> 4
    Height = float(value) / 16.0
    return(Height)

# Returns Reads the current pressure in Pa
# Returns -1 if no new data is available
def readPressure():
    # Check PDR bit, if it's not set then toggle OST
    if(IIC_Read(STATUS) & 0x04 == 0):
        # Toggle the OST bit causing the sensor to immediately take another reading
        toggleOneShot()

    # Wait for PDR bit, indicates we have new pressure data
    counter = 0
    while( (IIC_Read(STATUS) & 0x04) == 0):
        counter = counter + 1
        if(counter > 600):
            # Error out after max of 512ms for a read
            return(-1)
        time.sleep_ms(1)

    # Read pressure registers
    data = bytearray(3)
    counter = 0
    nBytes = 0
    while True:
        nBytes = i2c.readfrom_mem_into(MPL3115Address, OUT_P_MSB, data)
        if nBytes == 3:
            break
        counter = counter + 1
        if(counter > 500):
            # Error out after max of 512ms for a read
            return(0x00)
        time.sleep_ms(1)            # wait 1msec

    msb = int(data[0])
    csb = int(data[1])
    lsb = int(data[2])

    value = (msb << 16) | (csb << 8) | lsb
    # Pressure is an 18 bit number with 2 bits of decimal.
    value = value >> 4
    pres = float(value)
    pressure = (pres / 4.0) / 1000.0
    return(pressure)
    
# =================================
#
# https://docs.pycom.io/pycom_esp32/library/machine.I2C.html
# i2c.init(mode, *, baudrate=100000, pins=(SDA, SCL))
# i2c = I2C(0, I2C.MASTER, baudrate=100000)
# i2c = I2C(0, I2C.MASTER, baudrate=100000, pins=('P22', 'P21'))      # Initialize the I2C bus
i2c = I2C(0, I2C.MASTER, pins=('P22', 'P21'))      # Initialize the I2C bus

# test of communication: Read the WHO_AM_I register, this is a good test of communication
while True:
    deviceID = IIC_Read(WHO_AM_I)           # Read WHO_AM_I register
    if deviceID == 0xC4:
        break
    print("MPL3115A2 deviceID: 0x{:02X} != 0xC4".format(deviceID))
    time.delay(1)

print("MPL3115A2 deviceID: 0x{:02X}".format(deviceID))

if DeviceReset():                           # Start off by resetting all registers to the default
    print("Reset operation completed")
else:
    print("Sensor reset problem!!!")

DeviceStandby()                             # Must be in standby to change registers

setOversampleRate(7)                        # Set Oversample to the recommended 128
enableEventFlags()                          # Enable all three pressure and temp event flags
SetOffsetCorrection(OFF_P, 0)               # set pressure offset correction
SetOffsetCorrection(OFF_T, Temp2Offset(-5.34))  # set temperature offset correction
SetOffsetCorrection(OFF_H, 0)               # set altitude offset correction

### # MPL3115A2 address, 0x60(96)
### # Select control register, 0x26(38)
### #       0xB9(185)   Active mode, OSR = 128, Altimeter mode
### IIC_Write(CTRL_REG1, 0xB9)
### # MPL3115A2 address, 0x60(96)
### # Select data configuration register, 0x13(19)
### #       0x07(07)    Data ready event enabled for altitude, pressure, temperature
### IIC_Write(PT_DATA_CFG, 0x07)
### # MPL3115A2 address, 0x60(96)
### # Select control register, 0x26(38)
### #       0xB9(185)   Active mode, OSR = 128, Altimeter mode
### IIC_Write(CTRL_REG1, 0xB9)
DeviceActive()                              # Set to active to start reading

time.sleep(1)

while True:
    # ---------------------------- get pressure
    setModeBarometer()
    pressure = readPressure()
    #### # MPL3115A2 address, 0x60(96)
    #### # Select control register, 0x26(38)
    #### #       0x39(57)    Active mode, OSR = 128, Barometer mode
    #### wr = bytearray(1)
    #### wr[0] = 0x39
    #### i2c.writeto_mem(MPL3115Address, 0x26, wr)
    #### time.sleep(1)
    #### 
    #### # MPL3115A2 address, 0x60(96)
    #### # Read data back from 0x00(00), 4 bytes
    #### # status, pres MSB1, pres MSB, pres LSB
    #### data2 = bytearray(3)
    #### data2 = i2c.readfrom_mem(MPL3115Address, 0x01, 3)
    #### # print(data2)                  # for debug
    #### # Convert data2 to 20-bits
    #### pres = ((data2[0] * 65536) + (data2[1] * 256) + (data2[2] & 0xF0)) / 16
    #### pressure = (pres / 4.0) / 1000.0

    # ---------------------------- get altitude
    #### # MPL3115A2 address, 0x60(96)
    #### # Select control register, 0x26(38)
    #### #       0x39 | 0x80    Active mode, OSR = 128, Barometer mode
    #### wr[0] = 0xB9
    #### i2c.writeto_mem(MPL3115Address, 0x26, wr)
    #### time.sleep(1)
    #### 
    #### # MPL3115A2 address, 0x60(96)
    #### # Read data back from 0x00(00), 4 bytes
    #### # status, pres MSB1, pres MSB, pres LSB
    #### data2 = bytearray(3)
    #### data2 = i2c.readfrom_mem(MPL3115Address, 0x01, 3)
    #### # print(data2)                  # for debug
    #### Height = ((data2[0] * 65536) + (data2[1] * 256) + (data2[2] & 0xF0)) / 16
    #### altitude = float(Height) / 16.0
    
    setModeAltimeter()
    altitude = readAltitude()
    
    # ---------------------------- get temperature
    cTemp = readTemperature()
    fTemp = cTemp * 1.8 + 32
    
    # Output data to screen
    print("Pressure : {0:.2f} kPa".format(pressure))
    print("Altitude : {0:.2f} m".format(altitude))
    print("Temperature in Celsius  :  {0:.2f} C".format(cTemp))
    print("Temperature in Fahrenheit  :  {0:.2f} F".format(fTemp))

    time.sleep(1)
