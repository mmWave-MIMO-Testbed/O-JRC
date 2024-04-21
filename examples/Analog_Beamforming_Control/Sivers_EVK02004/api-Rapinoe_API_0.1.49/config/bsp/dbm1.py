# Signal override
#RST_N            = 12

# Objects
HW_OBJECTS = {'rap0'      : {'type':'Rap', 'params': {'name':'rap0', 'chip_num':0, 'chip_select':3}},
              'rap1'      : {'type':'Rap', 'params': {'name':'rap1', 'chip_num':1, 'chip_select':3}},
              'cfg_eeprom': {'type':'CfgEeprom', 'params': {'addr':0x50, 'addr_size':2, 'page_size':32}}
             }

class Rap():

    RAPINOE_SPI_RD      = 0
    RAPINOE_SPI_WR_RAW  = 1
    RAPINOE_SPI_WR_SET  = 2
    RAPINOE_SPI_WR_CLR  = 3
    RAPINOE_SPI_WR_TGL  = 4

    def __init__(self, name, chip_num, chip_select):
        self.chip_num = chip_num
        self.chip_select = chip_select
        self.name = name

    def get_name(self):
        return self.name

    def format_rci_read(self, addr):
        send_data = [0, 0]
        command = (self.chip_num << 14) + (addr << 3) + Rap.RAPINOE_SPI_RD
        send_data[0] = (command >> 8) & 0xff
        send_data[1] = (command) & 0xff
        return send_data

    def format_rci_write(self, addr, data):
        send_data = [0, 0] + data
        command = (self.chip_num << 14) + (addr << 3) + Rap.RAPINOE_SPI_WR_RAW
        send_data[0] = (command >> 8) & 0xff
        send_data[1] = (command) & 0xff
        return send_data

    def format_rci_tgl(self, addr, data):
        send_data = [0, 0] + data
        command = (self.chip_num << 14) + (addr << 3) + Rap.RAPINOE_SPI_WR_TGL
        send_data[0] = (command >> 8) & 0xff
        send_data[1] = (command) & 0xff
        return send_data

    def format_rci_set(self, addr, data):
        send_data = [0, 0] + data
        command = (self.chip_num << 14) + (addr << 3) + Rap.RAPINOE_SPI_WR_SET
        send_data[0] = (command >> 8) & 0xff
        send_data[1] = (command) & 0xff
        return send_data

    def format_rci_clr(self, addr, data):
        send_data = [0, 0] + data
        command = (self.chip_num << 14) + (addr << 3) + Rap.RAPINOE_SPI_WR_CLR
        send_data[0] = (command >> 8) & 0xff
        send_data[1] = (command) & 0xff
        return send_data

class CfgEeprom():
    def __init__(self, addr, addr_size, page_size):
        self.addr = addr
        self.addr_size = addr_size
        self.page_size = page_size
