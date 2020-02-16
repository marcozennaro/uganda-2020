"""
---------------------------------------------------------------------
Driver for grove sunlight sensor (sensor: si
https://www.seeedstudio.com/Grove-Sunlight-Sensor-p-2530.html
Author: Marco Rainone - Wireless Lab ICTP
email: mrainone@ictp.it
Ver: 0.1
Last Update: 29/04/2018
Based on the work by: 
   - Nelio Goncalves Godoi (neliogodoi@yahoo.com.br)
   - Joe Gutting (2014) (https://github.com/THP-JOE/Python_SI1145)
---------------------------------------------------------------------
"""
from machine import I2C
import time

# sensor Si1145 - Silicon Labs
# datasheet:
# https://www.silabs.com/documents/public/data-sheets/Si1145-46-47.pdf

# COMMANDS
SI1145_PARAM_QUERY                      = const(0x80)
SI1145_PARAM_SET                        = const(0xA0)
SI1145_NOP                              = const(0x00)
SI1145reset                             = const(0x01)
SI1145_BUSADDR                          = const(0x02)
SI1145_PS_FORCE                         = const(0x05)
SI1145_ALS_FORCE                        = const(0x06)
SI1145_PSALS_FORCE                      = const(0x07)
SI1145_PS_PAUSE                         = const(0x09)
SI1145_ALS_PAUSE                        = const(0x0A)
SI1145_PSALS_PAUSE                      = const(0x0B)
SI1145_PS_AUTO                          = const(0x0D)
SI1145_ALS_AUTO                         = const(0x0E)
SI1145_PSALS_AUTO                       = const(0x0F)
SI1145_GET_CAL                          = const(0x12)

# Parameters:
SI1145_PARAM_I2CADDR                    = const(0x00)
SI1145_PARAM_CHLIST                     = const(0x01)
SI1145_PARAM_CHLIST_ENUV                = const(0x80)
SI1145_PARAM_CHLIST_ENAUX               = const(0x40)
SI1145_PARAM_CHLIST_ENALSIR             = const(0x20)
SI1145_PARAM_CHLIST_ENALSVIS            = const(0x10)
SI1145_PARAM_CHLIST_ENPS1               = const(0x01)
SI1145_PARAM_CHLIST_ENPS2               = const(0x02)
SI1145_PARAM_CHLIST_ENPS3               = const(0x04)

SI1145_PARAM_PSLED12SEL                 = const(0x02)
SI1145_PARAM_PSLED12SEL_PS2NONE         = const(0x00)
SI1145_PARAM_PSLED12SEL_PS2LED1         = const(0x10)
SI1145_PARAM_PSLED12SEL_PS2LED2         = const(0x20)
SI1145_PARAM_PSLED12SEL_PS2LED3         = const(0x40)
SI1145_PARAM_PSLED12SEL_PS1NONE         = const(0x00)
SI1145_PARAM_PSLED12SEL_PS1LED1         = const(0x01)
SI1145_PARAM_PSLED12SEL_PS1LED2         = const(0x02)
SI1145_PARAM_PSLED12SEL_PS1LED3         = const(0x04)

SI1145_PARAM_PSLED3SEL                  = const(0x03)
SI1145_PARAM_PSENCODE                   = const(0x05)
SI1145_PARAM_ALSENCODE                  = const(0x06)

SI1145_PARAM_PS1ADCMUX                  = const(0x07)
SI1145_PARAM_PS2ADCMUX                  = const(0x08)
SI1145_PARAM_PS3ADCMUX                  = const(0x09)
SI1145_PARAM_PSADCOUNTER                = const(0x0A)
SI1145_PARAM_PSADCGAIN                  = const(0x0B)
SI1145_PARAM_PSADCMISC                  = const(0x0C)
SI1145_PARAM_PSADCMISC_RANGE            = const(0x20)
SI1145_PARAM_PSADCMISC_PSMODE           = const(0x04)

SI1145_PARAM_ALSIRADCMUX                = const(0x0E)
SI1145_PARAM_AUXADCMUX                  = const(0x0F)

SI1145_PARAM_ALSVISADCOUNTER            = const(0x10)
SI1145_PARAM_ALSVISADCGAIN              = const(0x11)
SI1145_PARAM_ALSVISADCMISC              = const(0x12)
SI1145_PARAM_ALSVISADCMISC_VISRANGE     = const(0x20)

SI1145_PARAM_ALSIRADCOUNTER             = const(0x1D)
SI1145_PARAM_ALSIRADCGAIN               = const(0x1E)
SI1145_PARAM_ALSIRADCMISC               = const(0x1F)
SI1145_PARAM_ALSIRADCMISC_RANGE         = const(0x20)

SI1145_PARAM_ADCCOUNTER_511CLK          = const(0x70)

SI1145_PARAM_ADCMUX_SMALLIR             = const(0x00)
SI1145_PARAM_ADCMUX_LARGEIR             = const(0x03)

# REGISTERS:
SI1145_REG_PARTID                       = const(0x00)
SI1145_REG_REVID                        = const(0x01)
SI1145_REG_SEQID                        = const(0x02)

SI1145_REG_INTCFG                       = const(0x03)
SI1145_REG_INTCFG_INTOE                 = const(0x01)
SI1145_REG_INTCFG_INTMODE               = const(0x02)

SI1145_REG_IRQEN                        = const(0x04)
SI1145_REG_IRQEN_ALSEVERYSAMPLE         = const(0x01)
SI1145_REG_IRQEN_PS1EVERYSAMPLE         = const(0x04)
SI1145_REG_IRQEN_PS2EVERYSAMPLE         = const(0x08)
SI1145_REG_IRQEN_PS3EVERYSAMPLE         = const(0x10)

SI1145_REG_IRQMODE1                     = const(0x05)
SI1145_REG_IRQMODE2                     = const(0x06)

SI1145_REG_HWKEY                        = const(0x07)
SI1145_REG_MEASRATE0                    = const(0x08)
SI1145_REG_MEASRATE1                    = const(0x09)
SI1145_REG_PSRATE                       = const(0x0A)
SI1145_REG_PSLED21                      = const(0x0F)
SI1145_REG_PSLED3                       = const(0x10)
SI1145_REG_UCOEFF0                      = const(0x13)
SI1145_REG_UCOEFF1                      = const(0x14)
SI1145_REG_UCOEFF2                      = const(0x15)
SI1145_REG_UCOEFF3                      = const(0x16)
SI1145_REG_PARAMWR                      = const(0x17)
SI1145_REG_COMMAND                      = const(0x18)
SI1145_REG_RESPONSE                     = const(0x20)
SI1145_REG_IRQSTAT                      = const(0x21)
SI1145_REG_IRQSTAT_ALS                  = const(0x01)

SI1145_REG_ALSVISDATA0                  = const(0x22)
SI1145_REG_ALSVISDATA1                  = const(0x23)
SI1145_REG_ALSIRDATA0                   = const(0x24)
SI1145_REG_ALSIRDATA1                   = const(0x25)
SI1145_REG_PS1DATA0                     = const(0x26)
SI1145_REG_PS1DATA1                     = const(0x27)
SI1145_REG_PS2DATA0                     = const(0x28)
SI1145_REG_PS2DATA1                     = const(0x29)
SI1145_REG_PS3DATA0                     = const(0x2A)
SI1145_REG_PS3DATA1                     = const(0x2B)
SI1145_REG_UVINDEX0                     = const(0x2C)
SI1145_REG_UVINDEX1                     = const(0x2D)
SI1145_REG_PARAMRD                      = const(0x2E)
SI1145_REG_CHIPSTAT                     = const(0x30)

# I2C Address:
SI1145_ADDR                             = const(0x60)

class SI1145(object):

    def __init__(self, objI2C=None, i2cAddr=None):
        if objI2C is None:
            raise ValueError('An I2C object is required.')
        else:
            self.i2c = objI2C
            
        if i2cAddr is None:
            self.addr = SI1145_ADDR
        else:
            self.addr = i2cAddr
        # si1145 initialization:
        self.reset()
        self.calibration()

    def reset(self):
        self.i2c.writeto_mem(self.addr, SI1145_REG_MEASRATE0, bytes([0x00]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_MEASRATE1, bytes([0x00]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_IRQEN,     bytes([0x00]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_IRQMODE1,  bytes([0x00]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_IRQMODE2,  bytes([0x00]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_INTCFG,    bytes([0x00]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_IRQSTAT,   bytes([0xFF]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_COMMAND,   bytes([0x01]), addrsize=8)
        time.sleep_ms(10)
        self.i2c.writeto_mem(self.addr, SI1145_REG_HWKEY,     bytes([0x17]), addrsize=8)
        time.sleep_ms(10)

    def write_parameter(self, address, parameter, value):
        self.i2c.writeto_mem(self.addr,SI1145_REG_PARAMWR, bytes([value]), addrsize=8)
        self.i2c.writeto_mem(self.addr,SI1145_REG_COMMAND, bytes([parameter | 0xA0]), addrsize=8)
        data = self.i2c.readfrom_mem(self.addr, SI1145_REG_PARAMRD, 1)
        return data

    def calibration(self):
        # Enable UVindex measurement coefficients:
        self.i2c.writeto_mem(self.addr, SI1145_REG_UCOEFF0, bytes([0x29]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_UCOEFF1, bytes([0x89]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_UCOEFF2, bytes([0x02]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_UCOEFF3, bytes([0x00]), addrsize=8)
        # Enable UV sensor
        self.write_parameter(self.addr, SI1145_PARAM_CHLIST, 0x80 | 0x20 | 0x10 | 0x01)
        # Enable interrupt on every sample
        self.i2c.writeto_mem(self.addr, SI1145_REG_INTCFG,  bytes([0x01]), addrsize=8)
        self.i2c.writeto_mem(self.addr, SI1145_REG_IRQEN,   bytes([0x01]), addrsize=8)
        # ****************************** Prox Sense 1
        # Program LED current
        self.i2c.writeto_mem(self.addr, SI1145_REG_PSLED21, bytes([0x03]), addrsize=8)
        self.write_parameter(self.addr, SI1145_PARAM_PS1ADCMUX,      0x03)
        # Prox sensor #1 uses LED #1
        self.write_parameter(self.addr, SI1145_PARAM_PSLED12SEL,     0x01)
        # Fastest clocks, clock div 1
        self.write_parameter(self.addr, SI1145_PARAM_PSADCGAIN,      0x00)
        # Take 511 clocks to measure
        self.write_parameter(self.addr, SI1145_PARAM_PSADCOUNTER,    0x70)
        # in prox mode, high range
        self.write_parameter(self.addr, SI1145_PARAM_PSADCMISC,      0x20 | 0x04)
        # Fastest clocks, clock div 1
        self.write_parameter(self.addr, SI1145_PARAM_ALSIRADCGAIN,   0x00)
        # Take 511 clocks to measure
        self.write_parameter(self.addr, SI1145_PARAM_ALSIRADCOUNTER, 0x70)
        # in high range mode
        self.write_parameter(self.addr, SI1145_PARAM_ALSIRADCMISC,   0x20)
        # fastest clocks, clock div 1
        self.write_parameter(self.addr, SI1145_PARAM_ALSVISADCGAIN,  0x00)
        # Take 511 clocks to measure
        self.write_parameter(self.addr, SI1145_PARAM_ALSVISADCOUNTER,0x70)
        # in high range mode (not normal signal)
        self.write_parameter(self.addr, SI1145_PARAM_ALSIRADCMISC,   0x20)
        # measurement rate for auto
        self.i2c.writeto_mem(self.addr, SI1145_REG_MEASRATE0,        bytes([0xFF]), addrsize=8)
        # auto run
        self.i2c.writeto_mem(self.addr, SI1145_REG_COMMAND,          bytes([0x0F]), addrsize=8)

    # read word little endian
    def readU16LE(self, address, register):
        data = self.i2c.readfrom_mem(address, register, 2, addrsize=8)
        result = ((data[1] << 8) | (data[0] & 0xFF))
        return result

    def read_uv(self):
        return self.readU16LE(self.addr,  0x2C) / 100

    def read_visible(self):
        return self.readU16LE(self.addr,  0x22)

    def read_ir(self):
        return self.readU16LE(self.addr,  0x24)

    def read_prox(self):
        return self.readU16LE(self.addr,  0x26)
