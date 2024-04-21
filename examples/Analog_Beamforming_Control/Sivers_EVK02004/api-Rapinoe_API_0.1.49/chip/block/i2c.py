from common import *
import eeprom as cfg_eeprom
import evk_logger
import math

class I2c():

    __instance = None

    i2c_states   = {0: 'ST_IDLE',1: 'ST_BUSBUSY',2: 'ST_INIT',3: 'ST_START',4: 'ST_ADDRPH',5: 'ST_ADDROK',6: 'ST_ADDR10PH',7: 'ST_ADDR10OK',8: 'ST_RDATAPH',9: 'ST_RDATAOK',10: 'ST_WDATAPH',11: 'ST_WDATAOK',12: 'ST_STOP',13: 'ST_STOPPED',14: 'ST_ARBLOST',15: 'ST_MISSACK'}

    def __new__(cls, spi, chip_info):
        if cls.__instance is None:
            cls.__instance = super(I2c, cls).__new__(cls)
            cls.__instance.__initialized = False
            cls.__instance.is_checked = False
            cls.__instance.is_calibrated = False
        return cls.__instance

    def __init__(self, spi, chip_info):
        self._spi       = spi
        self._chip_info = chip_info

    @evk_logger.log_call
    def reset(self, devs):
        """
        * Stop the I2C IP and send STOP command on the I2C bus
        * Toggle I2C RGU Module and SAB resets
        """
        self._stop(devs)
        self._spi.set(devs, 'rgu_slave_rst',  0b00000100)
        self._spi.set(devs, 'rgu_module_rst', 0b00000100)
        self._spi.clr(devs, 'rgu_slave_rst',  0b00000100)
        self._spi.clr(devs, 'rgu_module_rst', 0b00000100)

    @evk_logger.log_call
    def enable(self, devs):
        """ 
        * Deactivate I2C RGU Module and SAB resets
        * Activate   I2C RGU Module and SAB clocks
        """ 
        self._spi.clr(devs, 'rgu_slave_rst',  0b00000100)
        self._spi.clr(devs, 'rgu_module_rst', 0b00000100)
        self._spi.set(devs, 'cgu_slave_clk',  0b00000100)
        self._spi.set(devs, 'cgu_module_clk', 0b00000100)

    @evk_logger.log_call
    def disable(self, devs):
        """
        * Deactivate I2C RGU Module and SAB clocks
        * Activate   I2C RGU Module and SAB resets
        """ 
        self._stop(devs)
        self._spi.clr(devs, 'cgu_slave_clk',  0b00000100)
        self._spi.clr(devs, 'cgu_module_clk', 0b00000100)
        self._spi.set(devs, 'rgu_slave_rst',  0b00000100)
        self._spi.set(devs, 'rgu_module_rst', 0b00000100)

    @evk_logger.log_call
    def _fetch_i2c_data(self, devs, i2c_addr):
        """ Fetch I2C Slave data
        ------------------------------------------------------------------------------------
        Pre-requisites:
        * uses current i2c slave internal address
        * uses i2c slave address defined by i2c_cfg_1.slave0_id if the i2c_addr is not defined
        ------------------------------------------------------------------------------------
        Configure I2C Bus Control memory to read 14 bytes
        ------------------------------------------------------------------------------------
        1  i2c_bus_ctrl[ 0]      b000_1_1110     < 3 bits  =  Slave ID  =  0>_ < Read>_ < 14 bytes>
        2  i2c_bus_ctrl[15]      h0              STOP
        3  i2c_cfg_1             h50             I2C address  i2c_cfg_1 i2c_slave0_id
        4  i2c_cfg_4             b01010100       Set i2c_cfg_4 start_sw  other bits keep the reset values
        """ 
        # Wait for the I2C FSM to enter state IDLE!!
        self._wait_i2c_fsm(devs)
        
        self._spi.wr(devs, 'i2c_cfg_32', 0b000_1_1110 ) # Slave 0, READ, 14 bytes
        self._spi.wr(devs, 'i2c_cfg_47', 0x00         ) # STOP command

        # Setup I2C slave address
        self._spi.wr(devs, 'i2c_cfg_1', i2c_addr)

        self._spi.wr(devs, 'i2c_cfg_4', 0b01010100 ) # Set start_sw 
        self._wait_i2c_fsm(devs)
        self._spi.wr(devs, 'i2c_cfg_4', 0b01000100 ) # Clear start_sw 

    @evk_logger.log_call
    def _set_i2c_internal_addr(self, devs, i2c_addr, int_addr):
        """ Set I2C Slave internal address
        ------------------------------------------------------------------------------------
        1  i2c_bus_ctrl[ 0]      b000_0_0010    <3 bits Slave ID always 0>_<Write_n>_<2 bytes>
        2  i2c_bus_ctrl[ 1]      int_addr[15:8] Write I2C Slave internal MSB Address
        3  i2c_bus_ctrl[ 2]      int_addr[ 7:0] Write I2C Slave internal LSB Address
        4  i2c_bus_ctrl[ 3]      h0             STOP
        5  i2c_cfg_1             i2c_addr       I2C address i2c_cfg_1 i2c_slave0_id
        6  i2c_cfg_4             b01010100      Set   i2c_cfg_4 start_sw other bits keep the reset values
        7  i2c_cfg_4             b01000100      Clear i2c_cfg_4 start_sw other bits keep the reset values
        """
        # 1-3
        self._spi.wr(devs, 'i2c_cfg_32', 0b000_0_0010 ) 
        self._spi.wr(devs, 'i2c_cfg_33', 0xff & (int_addr >> 8) ) 
        self._spi.wr(devs, 'i2c_cfg_34', 0xff & int_addr) 
        self._spi.wr(devs, 'i2c_cfg_35', 0x0 ) 
        
        self._spi.wr(devs, 'i2c_cfg_1', i2c_addr ) 
        # Ensure that the I2C FSM is in state IDLE!!
        self._wait_i2c_fsm(devs)
        self._spi.wr(devs, 'i2c_cfg_4', 0b01010100 ) # Set start_sw 

        # Wait for the I2C FSM to enter state IDLE!!
        self._wait_i2c_fsm(devs)
        
        self._spi.wr(devs, 'i2c_cfg_4', 0b01000100 ) # Clear start_sw 

    @evk_logger.log_call
    def rd(self, devs, slave_addr, start_addr, no_bytes, formatit=None, printit=False):
        """ 
        * Read data from an external I2C Slave. Need to define:
          - I2C Slave address
          - I2C Slave internal address
          - Data
          - (Page size, default 32 bytes)
        """ 

        # Wait for the I2C FSM to enter state IDLE!!
        self._wait_i2c_fsm(devs)
        read_data = 0
        
        # The very small 16 byte I2C Bus Control Memory can only read 14 bytes at a time, one byte for READ COMMAND and one byte for STOP
        # Start by updating the I2C Slave internal address pointer
        self._set_i2c_internal_addr(devs,slave_addr,start_addr)
        # Read chunks of 14 bytes until no_bytes is read
        number_fetch = math.ceil(no_bytes/14)
        #evk_logger.evk_logger.log_info("Number of fetches = ",number_fetch)
        for loop in range(0,number_fetch):
            self._fetch_i2c_data(devs, slave_addr)
            if (loop*14 + 1 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_33')
            if (loop*14 + 2 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_34')
            if (loop*14 + 3 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_35')
            if (loop*14 + 4 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_36')
            if (loop*14 + 5 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_37')
            if (loop*14 + 6 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_38')
            if (loop*14 + 7 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_39')
            if (loop*14 + 8 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_40')
            if (loop*14 + 9 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_41')
            if (loop*14 +10 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_42')
            if (loop*14 +11 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_43')
            if (loop*14 +12 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_44')
            if (loop*14 +13 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_45')
            if (loop*14 +14 <= no_bytes):
                read_data = (read_data << 8) + self._spi.rd(devs, 'i2c_cfg_46')
        return read_data

    @evk_logger.log_call
    def _wait_i2c_fsm(self, devs, to_ms=1000, printit=False):
        # to_time is in ms, timediff is in ns
        start = timediff()
        while ((0b00001111 & self._spi.rd(devs, 'i2c_read_info_20')) !=  0x0):
            cur = timediff(start)
            if (cur/1e6 > to_ms):
                if printit:
                    evk_logger.evk_logger.log_error("Timeout!")
                return 1
        return 0

    @evk_logger.log_call
    def _write_i2c_data(self, devs, i2c_addr,start_addr,no_bytes,write_data,page_size=32,formatit=None, printit=False):
        mask = 0
        for x in range(no_bytes):
            mask = (mask << 8) + 0xFF
        rest_bytes = no_bytes
        next_addr  = start_addr
        while (rest_bytes >= 12):
            next_addr = next_addr + 12
            rest_bytes = rest_bytes - 12
        self._wait_i2c_fsm(devs)
        if (rest_bytes > 0):
            self._spi.wr(devs, 'i2c_cfg_32', 0b000_0_0010 + rest_bytes)
            self._spi.wr(devs, 'i2c_cfg_33', 0xff & (next_addr >> 8))
            self._spi.wr(devs, 'i2c_cfg_34', 0xff & next_addr)
            if (rest_bytes >  0):
                self._spi.wr(devs, 'i2c_cfg_35', 0xff & (write_data >> 8*(rest_bytes- 1)))
            else:
                self._spi.wr(devs, 'i2c_cfg_35', 0)
            if (rest_bytes >  1):
                self._spi.wr(devs, 'i2c_cfg_36', 0xff & (write_data >> 8*(rest_bytes- 2)))
            else:
                self._spi.wr(devs, 'i2c_cfg_36', 0)
            if (rest_bytes >  2):
                self._spi.wr(devs, 'i2c_cfg_37', 0xff & (write_data >> 8*(rest_bytes- 3)))
            else:
                self._spi.wr(devs, 'i2c_cfg_37', 0)
            if (rest_bytes >  3):
                self._spi.wr(devs, 'i2c_cfg_38', 0xff & (write_data >> 8*(rest_bytes- 4)))
            else:
                self._spi.wr(devs, 'i2c_cfg_38', 0)
            if (rest_bytes >  4):
                self._spi.wr(devs, 'i2c_cfg_39', 0xff & (write_data >> 8*(rest_bytes- 5)))
            else:
                self._spi.wr(devs, 'i2c_cfg_39', 0)
            if (rest_bytes >  5):
                self._spi.wr(devs, 'i2c_cfg_40', 0xff & (write_data >> 8*(rest_bytes- 6)))
            else:
                self._spi.wr(devs, 'i2c_cfg_40', 0)
            if (rest_bytes >  6):
                self._spi.wr(devs, 'i2c_cfg_41', 0xff & (write_data >> 8*(rest_bytes- 7)))
            else:
                self._spi.wr(devs, 'i2c_cfg_41', 0)
            if (rest_bytes >  7):
                self._spi.wr(devs, 'i2c_cfg_42', 0xff & (write_data >> 8*(rest_bytes- 8)))
            else:
                self._spi.wr(devs, 'i2c_cfg_42', 0)
            if (rest_bytes >  8):
                self._spi.wr(devs, 'i2c_cfg_43', 0xff & (write_data >> 8*(rest_bytes- 9)))
            else:
                self._spi.wr(devs, 'i2c_cfg_43', 0)
            if (rest_bytes >  9):
                self._spi.wr(devs, 'i2c_cfg_44', 0xff & (write_data >> 8*(rest_bytes-10)))
            else:
                self._spi.wr(devs, 'i2c_cfg_44', 0)
            if (rest_bytes > 10):
                self._spi.wr(devs, 'i2c_cfg_45', 0xff & (write_data >> 8*(rest_bytes-11)))
            else:
                self._spi.wr(devs, 'i2c_cfg_45', 0)
            if (rest_bytes > 11):
                self._spi.wr(devs, 'i2c_cfg_46', 0xff & (write_data >> 8*(rest_bytes-12)))
            else:
                self._spi.wr(devs, 'i2c_cfg_46', 0)
            self._spi.wr(devs, 'i2c_cfg_47', 0)
            self._spi.wr(devs, 'i2c_cfg_1', i2c_addr)
            self._spi.wr(devs, 'i2c_cfg_4', 0b01010100 ) # Set start_sw 
            self._wait_i2c_fsm(devs)
            self._spi.wr(devs, 'i2c_cfg_4', 0b01000100 ) # Clear start_sw 
            self._wait_i2c_fsm(devs)
            rd_data=self._spi.rd(devs, 'i2c_read_info_21')
            #if (rd_data != (4+rest_bytes)):
            #    evk_logger.evk_logger.log_info("Error: bus_ptr_[start,stop] are not as expected! 4+",rest_bytes," != ",rd_data)
        
        no_bytes_left = no_bytes - rest_bytes
        next_addr     = next_addr - 12
        next_data     = write_data >> 8*rest_bytes
        while (no_bytes_left > 0):
            self._wait_i2c_fsm(devs)
            self._spi.wr(devs, 'i2c_cfg_32', 0b000_0_1110)
            self._spi.wr(devs, 'i2c_cfg_33', 0xff & (next_addr >> 8))
            self._spi.wr(devs, 'i2c_cfg_34', 0xff & next_addr)
            self._spi.wr(devs, 'i2c_cfg_35', 0xff & (next_data >> 8*11))
            self._spi.wr(devs, 'i2c_cfg_36', 0xff & (next_data >> 8*10))
            self._spi.wr(devs, 'i2c_cfg_37', 0xff & (next_data >> 8* 9))
            self._spi.wr(devs, 'i2c_cfg_38', 0xff & (next_data >> 8* 8))
            self._spi.wr(devs, 'i2c_cfg_39', 0xff & (next_data >> 8* 7))
            self._spi.wr(devs, 'i2c_cfg_40', 0xff & (next_data >> 8* 6))
            self._spi.wr(devs, 'i2c_cfg_41', 0xff & (next_data >> 8* 5))
            self._spi.wr(devs, 'i2c_cfg_42', 0xff & (next_data >> 8* 4))
            self._spi.wr(devs, 'i2c_cfg_43', 0xff & (next_data >> 8* 3))
            self._spi.wr(devs, 'i2c_cfg_44', 0xff & (next_data >> 8* 2))
            self._spi.wr(devs, 'i2c_cfg_45', 0xff & (next_data >> 8* 1))
            self._spi.wr(devs, 'i2c_cfg_46', 0xff & (next_data >> 8* 0))
            self._spi.wr(devs, 'i2c_cfg_47', 0)
            self._spi.wr(devs, 'i2c_cfg_1', i2c_addr)
            self._spi.wr(devs, 'i2c_cfg_4', 0b01010100 ) # Set start_sw 
            self._wait_i2c_fsm(devs)
            self._spi.wr(devs, 'i2c_cfg_4', 0b01000100 ) # Clear start_sw 
            no_bytes_left = no_bytes_left -12
            next_addr     = next_addr - 12
            next_data     = next_data >> 8*12
            self._wait_i2c_fsm(devs)
            rd_data=self._spi.rd(devs, 'i2c_read_info_21')

    @evk_logger.log_call
    def _write_i2c_page(self, devs, i2c_addr,start_addr,no_bytes,write_data,page_size=32, formatit=None, printit=False):
        left_data = write_data
        wr1_bytes  = min(12,no_bytes)
        wr1_addr   = start_addr
        wr2_bytes  = min(12,max(0,no_bytes-12))
        wr2_addr   = wr1_addr + wr1_bytes
        wr3_bytes  = min( 8,max(0,no_bytes-12-12))
        wr3_addr   = wr2_addr + wr2_bytes
        wr1_data   = 0
        wr2_data   = 0
        wr3_data   = 0
        for i in range(0,wr3_bytes):
            wr3_data  = wr3_data + ((0xff & left_data) << i*8)
            left_data = left_data >> 8
        for i in range(0,wr2_bytes):
            wr2_data  = wr2_data + ((0xff & left_data) << i*8)
            left_data = left_data >> 8
        for i in range(0,wr1_bytes):
            wr1_data  = wr1_data + ((0xff & left_data) << i*8)
            left_data = left_data >> 8
        num_writes = int(wr1_bytes > 0) + int(wr2_bytes > 0) + int(wr3_bytes > 0)
        if (wr1_bytes > 0):
            self._write_i2c_data(devs,i2c_addr,wr1_addr,wr1_bytes,wr1_data,page_size,formatit,printit)
        if (wr2_bytes > 0):
            self._write_i2c_data(devs,i2c_addr,wr2_addr,wr2_bytes,wr2_data,page_size,formatit,printit)
        if (wr3_bytes > 0):
            self._write_i2c_data(devs,i2c_addr,wr3_addr,wr3_bytes,wr3_data,page_size,formatit,printit)

    @evk_logger.log_call
    def wr(self, devs, i2c_addr, start_addr, no_bytes, write_data, page_size=32, formatit=None, printit=False):
        start_page            = int(start_addr/page_size)
        stop_page             = int((start_addr+no_bytes-1)/page_size)
        start_page_free_bytes = (start_page+1)*page_size-start_addr
        if (start_page_free_bytes <= no_bytes):
            start_page_bytes = start_page_free_bytes
        else:
            start_page_bytes = no_bytes
        if (stop_page - start_page == 0):
            stop_page_bytes   = 0
        else:
            stop_page_bytes   = start_addr+no_bytes-stop_page*page_size
        if (stop_page - start_page == 0):
            additional_full_pages = 0
        else:
            additional_full_pages = stop_page - start_page -1
        left_data = write_data
        page_data = 0
        if (stop_page_bytes > 0):
            for i in range(0,stop_page_bytes):
                page_data = page_data + ((0xff & left_data) << i*8)
                left_data = left_data >> 8
            self._write_i2c_page(devs,i2c_addr,page_size*stop_page,stop_page_bytes,page_data,page_size,formatit,printit)
        for page in range(additional_full_pages,0,-1):
            page_data = 0
            for i in range(0,32):
                page_data = page_data + ((0xff & left_data) << i*8)
                left_data = left_data >> 8
            self._write_i2c_page(devs,i2c_addr,(start_page+page)*32,32,page_data,page_size)
        if (start_page_bytes > 0):
            page_data = 0
            for i in range(0,start_page_bytes):
                page_data = page_data + ((0xff & left_data) << i*8)
                left_data = left_data >> 8
            self._write_i2c_page(devs,i2c_addr,start_addr,start_page_bytes,page_data,page_size)

    def _find_tlv_seq(self, devs, i2c_addr, break_at_stop=True):
        value = 0xff
        addr = 0x00
        eeprom = []
        while (addr < 0x2000):
            value = self.rd(devs, i2c_addr, addr, 1)
            if value == cfg_eeprom.tlv_codes['JMP']:
                tlv_data = {'addr':addr, 'tlv': cfg_eeprom.tlv_codes['JMP']}
                addr += 1
                i2c_slave_id = self.rd(devs, i2c_addr, addr, 1)
                tlv_data['i2c_slave_id'] = i2c_slave_id
                addr += 1
                i2c_int_addr = self.rd(devs, i2c_addr, addr, 1)
                tlv_data['i2c_int_addr'] = i2c_int_addr
                addr = i2c_int_addr
                eeprom.append(tlv_data)
            elif value == cfg_eeprom.tlv_codes['STOP']:
                tlv_data = {'addr':addr, 'tlv': cfg_eeprom.tlv_codes['STOP']}
                addr += 1
                eeprom.append(tlv_data)
                if break_at_stop:
                    break
            elif value == cfg_eeprom.tlv_codes['CFG']:
                tlv_data = {'addr':addr, 'tlv': cfg_eeprom.tlv_codes['CFG']}
                addr += 1
                len0 = self.rd(devs, i2c_addr, addr, 1)
                addr += 1
                len1 = self.rd(devs, i2c_addr, addr, 1)
                length = (len0<<8) + len1
                tlv_data['length'] = length
                addr += 1
                chip_num = self.rd(devs, i2c_addr, addr, 1)
                tlv_data['chip_num'] = chip_num
                addr += 1
                tlv_data['data_block'] = []
                db_complete = False
                while not db_complete:
                    db = {}
                    sab_sel = self.rd(devs, i2c_addr, addr, 1)
                    db['sab_sel'] = sab_sel
                    addr += 1
                    sab_int_addr = self.rd(devs, i2c_addr, addr, 1)
                    db['sab_int_addr'] = sab_int_addr
                    addr += 1
                    db_size = self.rd(devs, i2c_addr, addr, 1)
                    db['db_size'] = db_size
                    addr += 1
                    db['d'] = []
                    for n in range(db_size+1):
                        db['d'].append(self.rd(devs, i2c_addr, addr, 1))
                        addr += 1
                    tlv_data['data_block'].append(db)
                    sab_sel_or_next_tlv_addr = self.rd(devs, i2c_addr, addr, 1)
                    if sab_sel_or_next_tlv_addr & 0x80:
                        # Next TLV addr reached
                        addr += 1
                        tlv_data['next_tlv_addr'] = (sab_sel_or_next_tlv_addr<<8) + self.rd(devs, i2c_addr, addr, 1)
                        addr = tlv_data['next_tlv_addr'] & 0x7f
                        db_complete = True
                eeprom.append(tlv_data)
            else:
                addr += 1
        return eeprom

    def _print_tlv_data(self, tlv_data):
        evk_logger.evk_logger.log_bold('')
        evk_logger.evk_logger.log_bold('TLV DATA (addr {})'.format(fhex(tlv_data['addr'],4)))
        evk_logger.evk_logger.log_bold('----------------------')
        for key in tlv_data.keys():
            if key == 'data_block':
                for db in tlv_data[key]:
                    evk_logger.evk_logger.log_bold('Data block - start', indentation=4)
                    for db_key in db.keys():
                        evk_logger.evk_logger.log_info('{}: {}'.format(db_key, fhex(db[db_key])), indentation=8)
                    evk_logger.evk_logger.log_bold('Data block - end', indentation=4)
            else:
                if key != 'addr':
                    evk_logger.evk_logger.log_info('{}: {}'.format(key, hex(tlv_data[key])), indentation=4)
        evk_logger.evk_logger.log_info('')

    @evk_logger.log_call
    def get_config(self, devs, i2c_addr, filename=None, printit=False):
        """
        Reads TVL blocks from EEPROM
        """
        evk_logger.evk_logger.log_info('Searching for valid TLV in EEPROM. Please wait ...')
        eeprom_config = self._find_tlv_seq(devs, i2c_addr)
        if filename != None:
            eeprom = cfg_eeprom.EEPROM(None)
            eeprom._to_xml(eeprom_config, filename)
        if printit:
            for tlv_data in eeprom_config:
                self._print_tlv_data(tlv_data)
        else:
            return eeprom_config

    @evk_logger.log_call
    def set_config(self, devs, i2c_addr, filename):
        """
        Writes TLV blocks from specified XML file to the EEPROM
        """
        eeprom = cfg_eeprom.EEPROM(None)
        eeprom._load_file(filename)
        for eprm in eeprom.eeprom:
            data_a = eeprom._get_byte_list(eprm)
            sp_data = eeprom._split_data(data_a) # First 2 elements in each array is the 16 bit starting EEPROM byte address.
            for a in sp_data:
                self.wr(devs, i2c_addr, intlist2int(a[:2]), len(a)-2, intlist2int(a[2:]))
        evk_logger.evk_logger.log_info('Done.')

    @evk_logger.log_call
    def _is_set(self, devs, data, bit_no, formatit=None, printit=False):
        """
        Return True if bit is 1, otherwise False
        """
        mask = 1 << bit_no
        return (mask & data) == mask

    @evk_logger.log_call
    def _is_clr(self, devs, data, bit_no, formatit=None, printit=False):
        """
        Return True if bit is 0, otherwise False
        """
        mask = 1 << bit_no
        return (mask & data) == 0

    @evk_logger.log_call
    def status(self, devs, formatit=None, printit=False):
        """
        * Boot-Loader running/done
        * FSM State
        * ACK/NACK abort
        * Arbitration lost
        """
        rd_data_16 = self._spi.rd (devs, 'i2c_read_info_16')
        rd_data_17 = self._spi.rd (devs, 'i2c_read_info_17')
        rd_data_19 = self._spi.rd (devs, 'i2c_read_info_19')
        rd_data_20 = self._spi.rd (devs, 'i2c_read_info_20')
        rd_data_22 = self._spi.rd (devs, 'i2c_read_info_22')
        rd_data_23 = self._spi.rd (devs, 'i2c_read_info_23')
        rd_data_27 = self._spi.rd (devs, 'i2c_read_info_27')
        rd_data_28 = self._spi.rd (devs, 'i2c_read_info_28')
        rd_data_29 = self._spi.rd (devs, 'i2c_read_info_29')
        rd_data_31 = self._spi.rd (devs, 'i2c_read_info_31')
        evk_logger.evk_logger.log_info("")
        evk_logger.evk_logger.log_info("-------------------------------------------------")
        evk_logger.evk_logger.log_info("-  I2C general status                           -")
        evk_logger.evk_logger.log_info("-------------------------------------------------")
        evk_logger.evk_logger.log_info("The I2C FSM is in state_____________ : {}".format(I2c.i2c_states[rd_data_20 & 0b00001111]))
        #evk_logger.evk_logger.log_info("I2C Master bit rate is______________ : {:0.0f} kbps with clk divider {}".format(self.get_data_rate(devs), self._spi.rd (devs, 'i2c_cfg_10')))
        evk_logger.evk_logger.log_info("I2C Master bit rate is______________ : {:0.0f} kbps".format(self.get_data_rate(devs)))
        if (self._is_set(devs,rd_data_17, 6)): evk_logger.evk_logger.log_info("i2c_read_info_17[  6]_______________ : {} - Abort due to bus_ctrl memory pointer overflow!".format((rd_data_17 & 0b01000000) >> 6))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_17[  6]_______________ : {}".format((rd_data_17 & 0b01000000) >> 6))
        if (self._is_set(devs,rd_data_17, 5)): evk_logger.evk_logger.log_info("i2c_read_info_17[  5]_______________ : {} - The I2C IP is running!".format((rd_data_17 & 0b00100000) >> 5))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_17[  5]_______________ : {}".format((rd_data_17 & 0b00100000) >> 5))
        if (self._is_clr(devs,rd_data_17, 0)): evk_logger.evk_logger.log_info("i2c_read_info_17[  0]_______________ : {} - The I2C Done indicator is not set!".format(rd_data_17 & 0b00000001))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_17[  0]_______________ : {}".format(rd_data_17 & 0b00000001))
        if (self._is_set(devs,rd_data_19, 7)): evk_logger.evk_logger.log_info("i2c_read_info_19[  7]_______________ : {} - Abort due to bus_ctrl memory pointer overflow!".format((rd_data_19 & 0b10000000) >> 7))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_19[  7]_______________ : {}".format((rd_data_19 & 0b10000000) >> 7))
        if (rd_data_19 & 0b01110000 != 0): evk_logger.evk_logger.log_info("i2c_read_info_19[6:4]_______________ : {} - The number of aborts due to missing ACK is not 0!".format((rd_data_19 & 0b01110000) >> 4))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_19[6:4]_______________ : {}".format((rd_data_19 & 0b01110000) >> 4))
        if (self._is_set(devs,rd_data_19, 3)): evk_logger.evk_logger.log_info("i2c_read_info_19[  3]_______________ : {} - The I2C missing ACK retrials have reached its maximum!".format((rd_data_19 & 0b00001000) >> 3))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_19[  3]_______________ : {}".format((rd_data_19 & 0b00001000) >> 3))
        if (self._is_set(devs,rd_data_19, 2)): evk_logger.evk_logger.log_info("i2c_read_info_19[  2]_______________ : {} - The I2C Arbitration lost retrials have reached its maximum!".format((rd_data_19 & 0b00000100) >> 2))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_19[  2]_______________ : {}".format((rd_data_19 & 0b00000100) >> 2))
        if (self._is_set(devs,rd_data_19, 1)): evk_logger.evk_logger.log_info("i2c_read_info_19[  1]_______________ : {} - The I2C Arbitration lost indicator is set!".format((rd_data_19 & 0b00000010) >> 1))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_19[  1]_______________ : {}".format((rd_data_19 & 0b00000010) >> 1))
        if (rd_data_20 & 0b11110000 != 0): evk_logger.evk_logger.log_info("i2c_read_info_20[7:4]_______________ : {} - The number of aborts due to Arbitration lost is not 0!({})".format((rd_data_20 & 0b11110000) >> 4))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_20[7:4]_______________ : {}".format((rd_data_20 & 0b11110000) >> 4))
        evk_logger.evk_logger.log_info("")
        evk_logger.evk_logger.log_info("-------------------------------------------------")
        evk_logger.evk_logger.log_info("-   I2C Boot-Loader status                      -")
        evk_logger.evk_logger.log_info("-------------------------------------------------")
        evk_logger.evk_logger.log_info("Last decoded TLV code_______________ : {} - {}".format(I2c.tlv_names.get(rd_data_28 & 0b11111111,'Undefined key'),fhex(rd_data_28 & 0b11111111)))
        evk_logger.evk_logger.log_info("Last accessed I2C Slave address_____ : {}".format(fhex(rd_data_27 & 0b01111111)))
        evk_logger.evk_logger.log_info("Last I2C Slave internal address_____ : {}".format(rd_data_29 & 0b1111111111111111))
        if (rd_data_31 & 0b1111111 > 0): evk_logger.evk_logger.log_info("Last I2C SAB Master access__________ : Write {} to {} address {} (d{})".format(fhex(rd_data_16),I2c.sab_slv_names[((rd_data_22 & 0b111) << 1) + ((rd_data_23 & 0x80) >> 7)],fhex(rd_data_23 & 0x7F),rd_data_23 & 0x7F))
        evk_logger.evk_logger.log_info("No. I2C SAB Master Write accesses___ : {}".format(rd_data_31 & 0b1111111))
        if (self._is_set(devs,rd_data_27, 7)): evk_logger.evk_logger.log_info("i2c_read_info_27[  7]_______________ : {} - Boot-Loader TLV decoding is still ongoing!".format((rd_data_27 & 0b10000000) >> 7))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_27[  7]_______________ : {}".format((rd_data_27 & 0b10000000) >> 7))
        if (self._is_set(devs,rd_data_17, 4)): evk_logger.evk_logger.log_info("i2c_read_info_17[  4]_______________ : {} - The I2C Boot-Loader is still running!".format((rd_data_17 & 0b00010000) >> 4))
        elif (printit): evk_logger.evk_logger.log_info("i2c_read_info_17[  4]_______________ : {}".format((rd_data_17 & 0b00010000) >> 4))
        evk_logger.evk_logger.log_info("")

    @evk_logger.log_call
    def _stop(self, devs):
        """
        Stop the I2C IP module and send STOP command on the I2C bus
        -------------------------------------------------------------
        1. Stop the I2C IP module         : Set i2c_cfg_5.clear       = 1
        2. Prepare for an I2C STOP command: Set i2c_cfg_7.bypass_cr   = Stop
        3. Enable control of I2C IP by SW : Set i2c_cfg_4.bypass_mode = 1
        4. Enable the I2C module          : Set i2c_cfg_5.clear       = 0
        5. Disable Stop command           : Set i2c_cfg_4.bypass_mode = 0
        """
        self._spi.set(devs, 'i2c_cfg_5', 0b10000000)
        self._spi.wr (devs, 'i2c_cfg_7', 0b00010000)
        self._spi.set(devs, 'i2c_cfg_4', 0b00001000)
        self._spi.clr(devs, 'i2c_cfg_5', 0b10000000)
        self._spi.wr (devs, 'i2c_cfg_7', 0b00000000)
        self._spi.clr(devs, 'i2c_cfg_4', 0b00001000)

    @evk_logger.log_call
    def scan_slaves(self, devs, start_addr=0,stop_addr=0x7F,to_ms=1000,printit=False):
        if (start_addr > stop_addr):
            evk_logger.evk_logger.log_error("Error: Start address ({}) must be smaller than Stop address ({}).".format(fhex(start_addr),fhex(stop_addr)),2)
            evk_logger.evk_logger.log_error("No scan was performed.",2)
            return None;
        if (stop_addr >= 0b10000000):
            evk_logger.evk_logger.log_error("Note! Only 7 LSBs of I2C Slave address are used!",2)
            evk_logger.evk_logger.log_error("No scan was performed.",2)
            return None;

        # Wait for I2C FSM
        self._wait_i2c_fsm(devs,to_ms,printit)
        self._spi.wr (devs, 'i2c_cfg_32', 0b000_0_0001 ) 
        self._spi.wr (devs, 'i2c_cfg_33', 0x0 ) 
        self._spi.wr (devs, 'i2c_cfg_34', 0x0 ) 
        for i2c_addr in range(start_addr, stop_addr+1):
            self._spi.wr (devs, 'i2c_cfg_1', i2c_addr ) 
            self._spi.wr (devs, 'i2c_cfg_4', 0b01010100 ) # Set start_sw 
            self._wait_i2c_fsm(devs,to_ms,printit)
            self._spi.wr (devs, 'i2c_cfg_4', 0b01000100 ) # Clear start_sw 
            rd_data16 = self._spi.rd (devs, 'i2c_read_info_16')
            rd_data17 = self._spi.rd (devs, 'i2c_read_info_17')
            rd_data19 = self._spi.rd (devs, 'i2c_read_info_19')
            rd_data20 = self._spi.rd (devs, 'i2c_read_info_20')
            rd_data21 = self._spi.rd (devs, 'i2c_read_info_21')
            rd_data22 = self._spi.rd (devs, 'i2c_read_info_22')
            rd_data23 = self._spi.rd (devs, 'i2c_read_info_23')
            rd_data24 = self._spi.rd (devs, 'i2c_read_info_24')
            rd_data25 = self._spi.rd (devs, 'i2c_read_info_25')
            rd_data26 = self._spi.rd (devs, 'i2c_read_info_26')
            rd_data27 = self._spi.rd (devs, 'i2c_read_info_27')
            rd_data28 = self._spi.rd (devs, 'i2c_read_info_28')
            rd_data29 = self._spi.rd (devs, 'i2c_read_info_29')
            rd_data31 = self._spi.rd (devs, 'i2c_read_info_31')
            found_i2c_slave = (rd_data21 == 0x03) and (rd_data26 == 0x00) and (rd_data19 == 0b0_000_0_000)
            chk_val = 0xFF & (i2c_addr << 1)
            if (found_i2c_slave) :
                evk_logger.evk_logger.log_info("I2C slave found @ {}".format(fhex(i2c_addr)),2)

    @evk_logger.log_call
    def get_data_rate(self, devs):
        # Return value in kbps
        ref_clk_f = self._chip_info.get(devs)['fref_def'] #225000000 # Use function when available
        return ref_clk_f / (self._spi.rd (devs, 'i2c_cfg_10') + 2) / 5.3 / 1000

    @evk_logger.log_call
    def set_data_rate(self, devs, kbps):
        # New data rate in kbps
        ref_clk_f = self._chip_info.get(devs)['fref_def'] #225000000 # Use function when available
        clk_div = int(ref_clk_f / kbps / 5.3 / 1000 -2)
        evk_logger.evk_logger.log_info("New I2C data rate         = {}".format(kbps))
        evk_logger.evk_logger.log_info("New I2C data rate divider = {}".format(clk_div))
        self._spi.wr (devs, 'i2c_cfg_10',clk_div)



