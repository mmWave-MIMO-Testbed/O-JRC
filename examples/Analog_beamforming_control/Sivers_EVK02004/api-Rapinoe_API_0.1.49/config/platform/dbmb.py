from common import *

## GPIO definitions
SPI_CLK          = 0
SPI_MOSI         = 1
SPI_MISO         = 2
SPI_CS_N_A       = 3
SPI_CS_N_B       = 4
SPI_CS_N_REF     = 5
VDD1V8_MEAS      = 6
RST_N            = 7

I2C_SCL          = 8
I2C_SDA_IN       = 9
I2C_SDA_OUT      = 10
DBG1             = 11
DBG2             = 12
CTRL_0_B         = 13
CTRL_1_B         = 14
CTRL_2_B         = 15

GPIO             = 16
CTRL_0_A         = 17
CTRL_1_A         = 18
CTRL_2_A         = 19
CTRL_3_A         = 20
CTRL_4_A         = 21
CTRL_5_A         = 22
CTRL_6_A         = 23

CTRL_7_A         = 24
CTRL_7_B         = 25
DIG_GPIO_0_A     = 26
DIG_GPIO_1_A     = 27
DIG_GPIO_2_A     = 28
DIG_GPIO_0_B     = 29
DIG_GPIO_1_B     = 30
DIG_GPIO_2_B     = 31

# Pin used for device reset
DEVICE_NRESET_PIN = RST_N

# CTRL interface definitions
CTRL_MODES  = [0,1]
CTRL_DATA   = {'grp':None, 'shift':None, 'pins':None}
CTRL_STROBE = {'grp':'D', 'shift':0, 'pins':{0:0x01, 1:0x01, 2:None, 3:None}}

# Moderboard type
MB_TYPE = 'DBMB'

# FTDI initial and final pin state
#ADBUS
GPIO_STATE_INITIAL_A = 0x000082bb
GPIO_STATE_FINAL_A = 0x82bb0000
GPIO_STATE_A = GPIO_STATE_INITIAL_A + GPIO_STATE_FINAL_A

#BDBUS
GPIO_STATE_INITIAL_B = 0x0000030B
GPIO_STATE_FINAL_B = 0x030B0000
GPIO_STATE_B = GPIO_STATE_INITIAL_B + GPIO_STATE_FINAL_B

#CDBUS
GPIO_STATE_INITIAL_C = 0x000000ff
GPIO_STATE_C = GPIO_STATE_INITIAL_C

#DDBUS
GPIO_STATE_INITIAL_D = 0x000000ff
GPIO_STATE_D = GPIO_STATE_INITIAL_D



# Objects
HW_OBJECTS = {
              'pwr' : {'type':'Pwr', 'params':{'name':'pwr', 'chip_select':5}}
             }


class Pwr():
    def __init__(self, name, chip_select):
        self.chip_select = chip_select
        self.name = name

    def get_name(self):
        return self.name

    def format_spi_write(self, data):
        send_data = int2intlist(data & 0xFFFFFFFF,256,4)
        return send_data