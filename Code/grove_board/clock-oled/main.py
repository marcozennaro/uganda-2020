# =====================================================================
# MicroPython SSD1308 OLED driver, I2C interface
# based on these projects:
# https://github.com/peterhinch/micropython-samples
# https://developer.mbed.org/users/wim/code/SSD1308_128x64_I2C/
# code released with MIT License (MIT)
#

from micropython import const
import time
import framebuf

# This is the I2C address (8 bit)
#  There are two possible addresses: with D/C# (pin 13) grounded, the address is 0x78,
#  with D/C# tied high it is 0x7A. Assume grounded by default.
SSD1308_SA0                = const(0x78)
SSD1308_SA1                = const(0x7A)
SSD1308_DEF_SA             = SSD1308_SA0

# Display dimensions
ROWS                       = const(64)
COLUMNS                    = const(128)
PAGES                      = (ROWS // 8)
MAX_PAGE                   = (PAGES - 1)
MAX_ROW                    = (ROWS - 1)
MAX_COL                    = (COLUMNS - 1)

# Character dimensions 8x8 font
# CHARS                      = (COLUMNS / FONT8x8_WIDTH)

# Command and Datamode 
COMMAND_MODE               = const(0x80)    # continuation bit is set!
DATA_MODE                  = const(0x40)

# Commands and Parameter defines
SET_LOWER_COLUMN           = const(0x00)    # = const( with lower nibble  (Page mode only)
SET_HIGHER_COLUMN          = const(0x10)    # = const( with higher nibble (Page mode only)

HORIZONTAL_ADDRESSING_MODE = const(0x00)
VERTICAL_ADDRESSING_MODE   = const(0x01)
PAGE_ADDRESSING_MODE       = const(0x02)
SET_MEMORY_ADDRESSING_MODE = const(0x20)    # takes one byte as given above

SET_COLUMN_ADDRESS         = const(0x21)    # takes two bytes, start address and end address of display data RAM
SET_PAGE_ADDRESS           = const(0x22)    # takes two bytes, start address and end address of display data RAM

# Command maybe unsupported by SSD1308
FADE_INTERVAL_8_FRAMES     = const(0x00)
FADE_INTERVAL_16_FRAMES    = const(0x01)
FADE_INTERVAL_24_FRAMES    = const(0x02)
FADE_INTERVAL_32_FRAMES    = const(0x03)
FADE_INTERVAL_64_FRAMES    = const(0x07)
FADE_INTERVAL_128_FRAMES   = const(0x0F)
FADE_BLINK_DISABLE         = const(0x00)
FADE_OUT_ENABLE            = const(0x20)
BLINK_ENABLE               = const(0x30)
SET_FADE_BLINK             = const(0x23)    # takes one byte
                                            #  bit5-4 = 0, fade/blink mode
                                            #  bit3-0 = Time interval in frames 

SET_DISPLAY_START_LINE     = const(0x40)    # = const( with a row number 0-63 to set start row. (Reset = 0)

SET_CONTRAST               = const(0x81)    # takes one byte, 0x00 - 0xFF

SET_SEGMENT_REMAP_0        = const(0xA0)    # column address 0 is mapped to SEG0 (Reset)
SET_SEGMENT_REMAP_127      = const(0xA1)    # column address 127 is mapped to SEG0

SET_DISPLAY_GDDRAM         = const(0xA4)    # restores display to contents of RAM
SET_ENTIRE_DISPLAY_ON      = const(0xA5)    # turns all pixels on, does not affect RAM

SET_NORMAL_DISPLAY         = const(0xA6)    # a databit of 1 indicates pixel 'ON'
SET_INVERSE_DISPLAY        = const(0xA7)    # a databit of 1 indicates pixel 'OFF'

SET_MULTIPLEX_RATIO        = const(0xA8)    # takes one byte, from 16xMUX to 64xMUX (MUX Ratio = byte+1; Default 64)

EXTERNAL_IREF              = const(0x10)
INTERNAL_IREF              = const(0x00)
SET_IREF_SELECTION         = const(0xAD)    # sets internal or external Iref

SET_DISPLAY_POWER_OFF      = const(0xAE)
SET_DISPLAY_POWER_ON       = const(0xAF)

PAGE0                      = const(0x00)
PAGE1                      = const(0x01)
PAGE2                      = const(0x02)
PAGE3                      = const(0x03)
PAGE4                      = const(0x04)
PAGE5                      = const(0x05)
PAGE6                      = const(0x06)
PAGE7                      = const(0x07)
SET_PAGE_START_ADDRESS     = const(0xB0)    # = const( with a page number to get start address (Page mode only)

SET_COMMON_REMAP_0         = const(0xC0)    # row address  0 is mapped to COM0 (Reset)
SET_COMMON_REMAP_63        = const(0xC8)    # row address 63 is mapped to COM0

SET_DISPLAY_OFFSET         = const(0xD3)    # takes one byte from 0-63 for vertical shift, Reset = 0

SET_DISPLAY_CLOCK          = const(0xD5)    # takes one byte
                                            #  bit7-4 = Osc Freq DCLK (Reset = 1000b) 
                                            #  bit3-0 = Divide ration (Reset = oooob, Ratio = 1)   

SET_PRECHARGE_TIME         = const(0xD9)    # takes one byte
                                            #  bit7-4 = Phase2, upto 15 DCLKs (Reset = 0010b) 
                                            #  bit3-0 = Phase1, upto 15 DCLKs (Reset = 0010b)   

                                       
COMMON_BASE                = const(0x02)    # 
COMMON_SEQUENTIAL          = const(0x00)    # Sequential common pins config
COMMON_ALTERNATIVE         = const(0x10)    # Odd/Even common pins config (Reset)
COMMON_LEFTRIGHT_NORMAL    = const(0x00)    # LeftRight Normal (Reset)
COMMON_LEFTRIGHT_FLIP      = const(0x20)    # LeftRight Flip 
SET_COMMON_CONF            = const(0xDA)    # takes one byte as given above


VCOMH_DESELECT_0_65_CODE   = const(0x00)
VCOMH_DESELECT_0_77_CODE   = const(0x20)
VCOMH_DESELECT_0_83_CODE   = const(0x30)
SET_VCOMH_DESELECT_LEVEL   = const(0xDB)    # takes one byte as given above

NOP                        = const(0xE3)

SCROLL_INTERVAL_5_FRAMES   = const(0x00)
SCROLL_INTERVAL_64_FRAMES  = const(0x01)
SCROLL_INTERVAL_128_FRAMES = const(0x02)
SCROLL_INTERVAL_256_FRAMES = const(0x03)
SCROLL_INTERVAL_3_FRAMES   = const(0x04)
SCROLL_INTERVAL_4_FRAMES   = const(0x05)
SCROLL_INTERVAL_25_FRAMES  = const(0x06)
SCROLL_INTERVAL_2_FRAMES   = const(0x07)

SET_RIGHT_HOR_SCROLL       = const(0x26)    # takes 6 bytes: = const(0x00, PageStart, Scroll_Interval, PageEnd, = const(0x00, = const(0xFF
SET_LEFT_HOR_SCROLL        = const(0x27)    # takes 6 bytes: = const(0x00, PageStart, Scroll_Interval, PageEnd, = const(0x00, = const(0xFF

SET_VERT_RIGHT_HOR_SCROLL  = const(0x29)    # takes 5 bytes: = const(0x00, PageStart, Scroll_Interval, PageEnd, VertOffset
SET_VERT_LEFT_HOR_SCROLL   = const(0x2A)    # takes 5 bytes: = const(0x00, PageStart, Scroll_Interval, PageEnd, VertOffset

SET_DEACTIVATE_SCROLL      = const(0x2E)
SET_ACTIVATE_SCROLL        = const(0x2F)

SET_VERTICAL_SCROLL_AREA   = const(0xA3)    # takes 2 bytes: Rows in Top Area (Reset=0), Rows in Scroll Area (Reset=64)

class SSD1308:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MVLSB)
        self.poweron()
        self.init_display()

    # original initialization
    def init_display(self):
        for cmd in (
            SET_DISPLAY_POWER_OFF,                  # off
            # address setting
            SET_MEMORY_ADDRESSING_MODE, 0x00,       # horizontal
            # resolution and layout
            SET_DISPLAY_START_LINE | 0x00,
            SET_SEGMENT_REMAP_0 | 0x01,             # column addr 127 mapped to SEG0
            SET_MULTIPLEX_RATIO, self.height - 1,
            SET_COMMON_REMAP_0 | 0x08,              # scan from COM[N] to COM0
            SET_DISPLAY_OFFSET, 0x00,
            SET_COMMON_CONF, 0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            SET_DISPLAY_CLOCK, 0x80,
            SET_PRECHARGE_TIME, 0x22 if self.external_vcc else 0xf1,
            SET_VCOMH_DESELECT_LEVEL, 0x30,         # 0.83*Vcc
            # display
            SET_CONTRAST, 0xff,                     # maximum
            SET_DISPLAY_GDDRAM,                     # output follows RAM contents
            SET_NORMAL_DISPLAY,                     # not inverted
            # charge pump
            # SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISPLAY_POWER_ON): # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    # Set Display StartLine, takes one byte, 0x00-0x3F
    # line startline (valid range 0..MAX_ROWS)
    def setDisplayStartLine(self, line):
        line = line & MAX_ROW
        self.write_cmd(SET_DISPLAY_START_LINE | line)     

    # Sets External Iref (default)
    def setExternalIref(self):
        self.write_cmd(SET_IREF_SELECTION) 
        self.write_cmd(EXTERNAL_IREF) 

    # Shows Pixels as RAM content
    def setEntireDisplayRAM(self):
        self.write_cmd(SET_DISPLAY_GDDRAM) 

    # Activate or Deactivate Horizontal and Vertical scroll
    # Note: after deactivating scrolling, the RAM data needs to be rewritten
    # bool on activate scroll 
    def setDisplayScroll(self, on):
        if (on):
            self.write_cmd(SET_ACTIVATE_SCROLL)     # Scroll on
        else:  
            self.write_cmd(SET_DEACTIVATE_SCROLL)   # Scroll off  

    # start startpage (valid range 0..MAX_PAGE)
    # end   endpage   (valid range start..MAX_PAGE)
    def setPageAddress(self, start, end):
        self.write_cmd(SET_PAGE_ADDRESS)   
        self.write_cmd(start)   
        self.write_cmd(end)   
            
    # clear the display
    # Standard version
    def clearDisplay(self):
        self.setPageAddress(0, MAX_PAGE)            # all pages
        self.setColumnAddress(0, MAX_COL)           # all columns
        for page in range(0, PAGES):
            for col in range(0, COLUMNS):
                self.write_data(0x00)
        #setDisplayOn()

    # Set Addressing Mode
    def setMemoryAddressingMode(self, mode):
        self.write_cmd(SET_MEMORY_ADDRESSING_MODE)   
        self.write_cmd(mode)   

    # Set Horizontal Addressing Mode (cursor incr left-to-right, top-to-bottom)
    def setHorizontalAddressingMode(self):
        self.setMemoryAddressingMode(HORIZONTAL_ADDRESSING_MODE) 

    # start startcolumn (valid range 0..MAX_COL)
    # end   endcolumn   (valid range start..MAX_COL)
    def setColumnAddress(self, start, end):
        self.write_cmd(SET_COLUMN_ADDRESS)     
        self.write_cmd(start)     
        self.write_cmd(end)     
        
    # Low level Init
    # Init the configuration registers in accordance with the datasheet
    def new_init_display(self):
        self.write_cmd(SET_DISPLAY_POWER_OFF)      # 0xAE

        # column address   0 is mapped to SEG0 (Reset)    
        # row address   0 is mapped to COM0 (Reset)      
        self.write_cmd(SET_SEGMENT_REMAP_0)        # 0xA0 (Reset)
        self.write_cmd(SET_COMMON_REMAP_0)         # 0xC0 (Reset) 

        self.setDisplayStartLine(0)                # 0x40 (Reset) 

        # self.write_cmd(SET_COMMON_CONF, COMMON_BASE | COMMON_ALTERNATIVE | COMMON_LEFTRIGHT_NORMAL)    # 0xDA, 0x12 (Reset)
        self.write_cmd(SET_COMMON_CONF)    # 0xDA, 0x12 (Reset)
        self.write_cmd(COMMON_BASE | COMMON_ALTERNATIVE | COMMON_LEFTRIGHT_NORMAL)    # 0xDA, 0x12 (Reset)

        # Pagemode or Horizontal mode
        self.setHorizontalAddressingMode()          # 0x20, 0x00 (Non-Reset)
        self.setColumnAddress(0, MAX_COL)           # 0x21, 0x00, 0x37 (Reset)
        self.setPageAddress(0, MAX_PAGE)            # 0x22, 0x00, 0x07 (Reset)

        self.setExternalIref()                      # 0xAD, 0x10 (Reset)

        self.write_cmd2(SET_DISPLAY_CLOCK, 0x70)    # 0xD5, 0x70 (Reset = 0x80)
        self.write_cmd2(SET_PRECHARGE_TIME, 0x21)   # 0xD9, 0x21 (Reset = 0x22)
        self.write_cmd2(SET_VCOMH_DESELECT_LEVEL, 0x30)    # 0xDB, 0x30 (Reset = 0x20)  
        self.write_cmd2(SET_MULTIPLEX_RATIO, 0x3F)  # 0xA8, 0x3F (Reset)  
        self.write_cmd2(SET_DISPLAY_OFFSET, 0x00)   # 0xD3, 0x00 (Reset)  

        self.write_cmd2(SET_CONTRAST, 0x7F)         # 0x81, 0x7F (Reset)

        self.write_cmd(SET_NORMAL_DISPLAY)          # 0xA6 (Reset)

        self.setEntireDisplayRAM()                  # 0xA4 (Reset)
        self.setDisplayScroll(False)

        self.clearDisplay()   

        self.write_cmd(SET_DISPLAY_POWER_ON)        # 0xAF

        self.fill(0)
        self.show()
        
    def poweroff(self):
        self.write_cmd(SET_DISPLAY_POWER_OFF)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORMAL_DISPLAY | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COLUMN_ADDRESS)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDRESS)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)

    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)


class SSD1308_I2C(SSD1308):
    def __init__(self, objI2C=None, addr=0x3c, width=128, height=64, external_vcc=False):
        if objI2C is None:
            raise ValueError('An I2C object is required.')
        else:
            self.i2c = objI2C

        self.addr = addr
        self.temp = bytearray(2)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        tmp = bytearray(1)
        tmp[0] = cmd
        self.i2c.writeto_mem(self.addr, 0x80, tmp)

    def write_cmd2(self, cmd, data):
        self.write_cmd(cmd)
        self.write_cmd(data)

    def write_data(self, buf):
        self.i2c.writeto_mem(self.addr, 0x40, buf)

    def poweron(self):
        pass

