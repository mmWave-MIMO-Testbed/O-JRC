import os
from time import sleep
import xml.etree.ElementTree as ET

import common
import evk_logger

STOP = 0b10000000

tlv_codes    = {'JMP':0x10,'STOP':0x11,'CFG':0x20,"DEFAULT":'HELP'}
tlv_names    = {0x10:'JMP',0x11:'STOP',0x20:'CFG',"DEFAULT":'HELP'}
sab_slv_codes= {'SYSTEM':0b0000,'RCU':0b0001,'I2C':0b0010,'EFC':0b0011,'ADC':0b0100,'SCHED':0b0101,'FIR':0b0110,'SYNTH':0b0111,'TRX':0b1000,'BIST':0b1010,'RX':0b1011,'RX_RAM':0b1100,'TX_RAM':0b1101,'BF_RAM':0b1110,"DEFAULT":'HELP'}
sab_slv_names= {0b0000:'SYSTEM',0b0001:'RCU',0b0010:'I2C',0b0011:'EFC',0b0100:'ADC',0b0101:'SCHED',0b0110:'FIR',0b0111:'SYNTH',0b1000:'TRX',0b1010:'BIST',0b1011:'RX',0b1100:'RX_RAM',0b1101:'TX_RAM',0b1110:'BF_RAM',"DEFAULT":'HELP'}


class EEPROM():

    __instance = None

    def __new__(cls, conn):
        if cls.__instance is None:
            cls.__instance = super(EEPROM, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance


    def __init__(self, conn):
        if self.__initialized:
            return
        self._conn = conn
        self.addr = self._conn.cfg_eeprom.addr
        self.addr_size = self._conn.cfg_eeprom.addr_size
        self.page_size = self._conn.cfg_eeprom.page_size
        self.eeprom = []
        self.__initialized = True
        
    def _parse_length(self, l):
        length = l.split(',')[0].split(' ')
        length = list(filter(lambda a: a != '', length))
        try:
            length = list(map(int,length))
        except:
            length = list(map(lambda x:int(x,16),length))
        return length

    def _parse_data_block(self, d):
        db = {'sab_sel': [], 'sab_int_addr': [], 'nbytes': [], 'd': []}
        db_size = 0
        for elem in d:
            if elem.tag == 'd':
                et = elem.text.split(',')[0].split(' ')
                et = list(filter(lambda a: a != '', et))
                try:
                    data = list(map(int,et))
                except:
                    data = list(map(lambda x:int(x,16),et))
                db['d'] = db['d'] + data
                db_size = db_size + len(data)
            else:
                try:
                    db[elem.tag] = [int(elem.text)]
                except:
                    db[elem.tag] = [int(elem.text, 16)]
                db_size = db_size + 1
        db['nbytes'] = [db_size - 3]
        return db, db_size

    def _load_file(self, filename):
        if not os.path.isabs(filename):
            filename = 'config/eeprom'+'/'+filename
        print('Reading EEPROM file {} ...'.format(filename))
        self.filename = filename
        eeprom_tree = ET.parse(filename)
        self.eeprom_root = eeprom_tree.getroot()
        if self.eeprom_root.tag != 'eeprom':
            raise Exception("File not an EEPROM file.")
        
        self.eeprom = []

        self.tlv_blocks = self.eeprom_root.findall('tlv_block')

        for tlv_block in self.tlv_blocks:
            eeprom_data = {}
            tlv_value_length = 0
            for element in tlv_block:
                if element.tag == 'length':
                    length = self._parse_length(tlv_block.find(element.tag).text)
                    eeprom_data[element.tag] = length
                elif element.tag == 'next_tlv_addr':
                    next_tlv_addr = self._parse_length(tlv_block.find(element.tag).text)
                    eeprom_data[element.tag] = next_tlv_addr
                    tlv_value_length = tlv_value_length + 2
                elif element.tag == 'data_block':
                    try:
                        eeprom_data[element.tag]
                    except:
                        eeprom_data[element.tag] = []
                    db, db_size = self._parse_data_block(element)
                    tlv_value_length = tlv_value_length + db_size
                    eeprom_data[element.tag] = eeprom_data[element.tag] + [db]
                else:
                    try:
                        eeprom_data[element.tag] = [int(tlv_block.find(element.tag).text)]
                    except:
                        eeprom_data[element.tag] = [int(tlv_block.find(element.tag).text, 16)]
                    if element.tag == 'tlv' and eeprom_data[element.tag] == [0x20]:
                        # For CFG TLV add a length key
                        eeprom_data['length'] = []
                    if element.tag != 'addr' and element.tag != 'tlv':
                        tlv_value_length = tlv_value_length + 1
            try:
                if eeprom_data['length'] == []:
                    eeprom_data['length'] = [(tlv_value_length&0xff00) >> 8, tlv_value_length&0x00ff]
            except:
                pass
            self.eeprom.append(eeprom_data)

    def _get_byte_list(self, eprm):
        data = []
        for key in eprm.keys():
            if key == 'data_block':
                for db in eprm[key]:
                    for db_key in db.keys():
                        data = data + db[db_key]
            else:
                data = data + eprm[key]
        return data

    def _split_data(self, data_a):
        start_addr = data_a[0]
        data = data_a[1:]
        ret_data = []
        num_of_fragments = (len(data) // self.page_size) + 2
        start_i = 0
        end_i = self.page_size - start_addr%self.page_size
        for n in range(num_of_fragments):
            ret_data.append([])
            ret_data[n] = data[start_i: end_i]
            if ret_data[n] != []:
                address16 = [(start_addr&0xff00)>>8, (start_addr&0x00ff)]
                ret_data[n] = address16 + ret_data[n]
                start_addr = start_addr + end_i - start_i
                start_i = end_i
                end_i = end_i + self.page_size
            else:
                ret_data.pop(n)
                break

        return ret_data

    def _write_config(self, printit=False):
        for eprm in self.eeprom:
            data_a = self._get_byte_list(eprm)
            sp_data = self._split_data(data_a) # First 2 elements in each array is the 16 bit starting EEPROM byte address.
            for data in sp_data:
                if printit:
                    print ('WRITING: {} size: {}'.format(data, len(data)))
                self._conn.mb.i2c_write(self._conn.board_id, self.addr, data, len(data))
                sleep(0.01)

    def _read_addr(self, byte_addr, num_of_bytes):
        self._conn.mb.i2c_write(self._conn.board_id, self.addr, common.int2intlist(byte_addr, num_ints=2), 2, stop_condition=False)
        return self._conn.mb.i2c_read(self._conn.board_id, self.addr, num_of_bytes)

    def _find_tlv_seq(self, break_at_stop=True):
        value = 0xff
        addr = 0x0000
        eeprom = []
        while (addr < 0x2000):
            value = self._read_addr(addr, 1)['data'][0]
            if value == tlv_codes['JMP']:
                tlv_data = {'addr':addr, 'tlv': tlv_codes['JMP']}
                addr += 1
                i2c_slave_id = self._read_addr(addr, 1)['data'][0]
                tlv_data['i2c_slave_id'] = i2c_slave_id
                addr += 1
                i2c_int_addr = self._read_addr(addr, 1)['data'][0]
                tlv_data['i2c_int_addr'] = i2c_int_addr
                addr = i2c_int_addr
                eeprom.append(tlv_data)
            elif value == tlv_codes['STOP']:
                tlv_data = {'addr':addr, 'tlv': tlv_codes['STOP']}
                addr += 1
                eeprom.append(tlv_data)
                if break_at_stop:
                    break
            elif value == tlv_codes['CFG']:
                tlv_data = {'addr':addr, 'tlv': tlv_codes['CFG']}
                addr += 1
                len0 = self._read_addr(addr, 1)['data'][0]
                addr += 1
                len1 = self._read_addr(addr, 1)['data'][0]
                length = (len0<<8) + len1
                tlv_data['length'] = length
                addr += 1
                chip_num = self._read_addr(addr, 1)['data'][0]
                tlv_data['chip_num'] = chip_num
                addr += 1
                tlv_data['data_block'] = []
                db_complete = False
                while not db_complete:
                    db = {}
                    sab_sel = self._read_addr(addr, 1)['data'][0]
                    db['sab_sel'] = sab_sel
                    addr += 1
                    sab_int_addr = self._read_addr(addr, 1)['data'][0]
                    db['sab_int_addr'] = sab_int_addr
                    addr += 1
                    db_size = self._read_addr(addr, 1)['data'][0]
                    db['db_size'] = db_size
                    addr += 1
                    db['d'] = []
                    for n in range(db_size+1):
                        db['d'].append(self._read_addr(addr, 1)['data'][0])
                        addr += 1
                    tlv_data['data_block'].append(db)
                    sab_sel_or_next_tlv_addr = self._read_addr(addr, 1)['data'][0]
                    if sab_sel_or_next_tlv_addr & 0x80:
                        # Next TLV addr reached
                        addr += 1
                        tlv_data['next_tlv_addr'] = (sab_sel_or_next_tlv_addr<<8) + self._read_addr(addr, 1)['data'][0]
                        addr = tlv_data['next_tlv_addr'] & 0x7f
                        db_complete = True
                eeprom.append(tlv_data)
            else:
                addr += 1
        return eeprom

    def _print_tlv_data(self, tlv_data):
        evk_logger.evk_logger.log_bold('')
        evk_logger.evk_logger.log_bold('TLV DATA (addr {})'.format(common.fhex(tlv_data['addr'],4)))
        evk_logger.evk_logger.log_bold('----------------------')
        for key in tlv_data.keys():
            if key == 'data_block':
                for db in tlv_data[key]:
                    evk_logger.evk_logger.log_bold('Data block - start', indentation=4)
                    for db_key in db.keys():
                        evk_logger.evk_logger.log_info('{}: {}'.format(db_key, common.fhex(db[db_key])), indentation=8)
                    evk_logger.evk_logger.log_bold('Data block - end', indentation=4)
            else:
                if key != 'addr':
                    evk_logger.evk_logger.log_info('{}: {}'.format(key, hex(tlv_data[key])), indentation=4)
        evk_logger.evk_logger.log_info('')

    def _to_xml(self, d, filename):
        DB_ELEMENTS_PER_LINE = 10
        if not os.path.isabs(filename):
            filename = 'config/eeprom'+'/'+filename
        print('Writing EEPROM file {} ...'.format(filename))
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write('<eeprom>\n')
            for tlv_block in d:
                f.write('    <tlv_block>\n')
                for key in tlv_block.keys():
                    if key != 'data_block' and key != 'length' and key != 'next_tlv_addr' and key != 'db_size':
                        f.write('        <{}>{}</{}>\n'.format(key, hex(tlv_block[key]), key))
                    elif key == 'next_tlv_addr':
                        f.write('        <{}>{} {}</{}>\n'.format(key, hex((tlv_block[key]&0xff00)>>8), hex(tlv_block[key]&0x00ff), key))
                    elif key == 'length':
                        pass
                    else:
                        for data_block in tlv_block[key]:
                            f.write('        <data_block>\n')
                            for dbkey in data_block.keys():
                                if dbkey != 'd' and dbkey != 'db_size':
                                    f.write('            <{}>{}</{}>\n'.format(dbkey, hex(data_block[dbkey]), dbkey))
                                elif dbkey == 'db_size':
                                    pass
                                else:
                                    f.write('            <d>')
                                    counter = 0
                                    for d in data_block[dbkey]:
                                        if counter % DB_ELEMENTS_PER_LINE > 0:
                                            f.write(' ')
                                        f.write(hex(d))
                                        counter += 1
                                        if counter % DB_ELEMENTS_PER_LINE == 0:
                                            f.write('</d>\n')
                                            f.write('            <d>')
                                    f.write('</d>\n')
                            f.write('        </data_block>\n')
                f.write('    </tlv_block>\n')
            f.write('</eeprom>\n')



    def set_config(self, filename):
        """set_config(filename)
        Writes TLV blocks from specified XML file to the EEPROM

        Args:
            filename (string): Name of an XML file containing TLV information to
            be written to the EEPROM.
        """
        self._load_file(filename)
        self._write_config()
        evk_logger.evk_logger.log_info('Done.')


    def get_config(self, filename=None, printit=False):
        """get_config(printit=False)
        Reads TVL blocks from EEPROM

        Args:
            filename (string): If not None the EEPROM content will be
            written to an XML file.

            printit (bool): True: Prints the results on the screen.
            False: Returns the results as a dictionary.
        """
        evk_logger.evk_logger.log_info('Searching for valid TLV in EEPROM. Please wait ...')
        eeprom_config = self._find_tlv_seq()
        if filename != None:
            self._to_xml(eeprom_config, filename)
        if printit:
            for tlv_data in eeprom_config:
                self._print_tlv_data(tlv_data)
        else:
            return eeprom_config
