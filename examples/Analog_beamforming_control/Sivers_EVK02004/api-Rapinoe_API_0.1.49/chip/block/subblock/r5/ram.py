import os

import rapspi
import evk_logger
import ram_file
import env_config
from common import *

class Ram():

    __instance = None
    __rows     = {'ram':256, 'tx_ram_v':64, 'tx_ram_h':64, 'rx_ram_v':64, 'rx_ram_h':64}
    __fields   = {'ram':      [32, [[15,15],[14,10],[9,5],[4,0]]],
                  'tx_ram_v': [1,  [[23,19],[18,14],[13,6],[5,0]]],
                  'tx_ram_h': [1,  [[23,19],[18,14],[13,6],[5,0]]],
                  'rx_ram_v': [1,  [[79,75],[74,71],[70,65],[64,59],[58,56],[55,52],[51,49],[48,47],[46,44],[43,42],[41,35],[34,28],[27,21],[20,14],[13,7],[6,0]]],
                  'rx_ram_h': [1,  [[79,75],[74,71],[70,65],[64,59],[58,56],[55,52],[51,49],[48,47],[46,44],[43,42],[41,35],[34,28],[27,21],[20,14],[13,7],[6,0]]]
                 }

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Ram, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        if self.__initialized:
            return
        self.__initialized = True
        self._spi = spi
        self.rf = self.get_ram_file()

    def _get_ram(self, ram):
        if (ram.lower() == 'bf')   | (ram.lower() == 'bf_ram') | (ram.lower() == 'ram'):
            return 'ram'
        if (ram.lower() == 'tx_v') | (ram.lower() == 'tx_ram_v'):
            return 'tx_ram_v'
        if (ram.lower() == 'tx_h') | (ram.lower() == 'tx_ram_h'):
            return 'tx_ram_h'
        if (ram.lower() == 'rx_v') | (ram.lower() == 'rx_ram_v'):
            return 'rx_ram_v'
        if (ram.lower() == 'rx_h') | (ram.lower() == 'rx_ram_h'):
            return 'rx_ram_h'

    def _int2format(self, ram, data, size, formatit=None):
        if (formatit == 'compact') or (formatit is None):
            return [data],2*size
        if formatit == 'byte':
            return int2intlist(data,256,size),2
        if formatit == 'field':
            resp = []
            repeat, fields = self.__fields[ram][0], self.__fields[ram][1]
            fields_bits = fields[0][0]+1
            for rep in range(repeat-1,-1,-1):
                for field in fields:
                    field_pos = field[1]
                    field_len = field[0]-field[1]+1
                    resp.append((data >> (field_pos + fields_bits * rep)) & (2**field_len-1))
            return resp,int((field_len-1)/4+1)

    def _name(self, addr):
        reg_name  = None
        for key,reg in self._spi.register_map.regs.items():
            if (reg['addr'] <= addr) and (reg['addr']+reg['length'] > addr):
                reg_name  = key
        return reg_name

    def _size(self, reg_name):
        """Return size of symbolic address"""
        return self._spi.register_map.regs[reg_name]['length']


    def _fielddict2data(self,address,fields_dict):
        if isinstance(address,int):
            address = self._name(address)
        data=0
        mask=2**(self._size(address)*8)-1
        for field,val in fields_dict.items():
            if not field in self._spi.register_map.reg_map[address]:
                print('Warning: field not valid. {} {}'.format(address,data))
            else:
                data+=val<<self._spi.register_map.reg_map[address][field]['Lsb']
                mask-=(2**(self._spi.register_map.reg_map[address][field]['Msb']+1)-2**self._spi.register_map.reg_map[address][field]['Lsb'])
        return int(data),int(mask)


    @evk_logger.log_call
    def rd(self, devs, ram, row):
        """ Read contents of 'ram' at <row>.
        """
        ram = self._get_ram(ram)
        addr, size = self._spi._addr_and_size(ram)
        return self._spi.rd(devs,addr + row,size)


    @evk_logger.log_call
    def wr(self, devs, ram, row, data, elem_pos=None, length=1):
        """ Write contents of 'ram' at <row> with <data>.
        """
        ram = self._get_ram(ram)
        addr, size = self._spi._addr_and_size(self._get_ram(ram))
        if elem_pos is not None:
            rd_data = self._spi.rd(devs,addr + row,size)
            rd_mask = (2**(size*8)-1)^(0xFFFF<<(elem_pos*16))
            data = (data << (elem_pos*16)) | (rd_data & rd_mask)
        return self._spi.wr(devs,addr + row, data, size*length)



    @evk_logger.log_call
    def wrrd(self, devs, ram, row, data, printit=True):
        """ Write contents of 'ram' at <row> with <data>.
        """
        ram = self._get_ram(ram)
        addr, size = self._spi._addr_and_size(self._get_ram(ram))
        return self._spi.wrrd(devs,addr + row, data, size, printit)

    @evk_logger.log_call
    def set(self, devs, ram, row, data, length=1):
        """ Write contents of 'ram' at <row> with <data>.
        """
        ram = self._get_ram(ram)
        addr, size = self._spi._addr_and_size(self._get_ram(ram))
        rd_data = self._spi.rd(devs,addr + row,size)
        wr_data = data | rd_data
        return self._spi.wr(devs,addr + row, wr_data, size*length)

    @evk_logger.log_call
    def clr(self, devs, ram, row, data, length=1):
        """ Write contents of 'ram' at <row> with <data>.
        """
        ram = self._get_ram(ram)
        addr, size = self._spi._addr_and_size(self._get_ram(ram))
        rd_data = self._spi.rd(devs,addr + row,size)
        wr_data = ~data & rd_data
        return self._spi.wr(devs,addr + row, wr_data, size*length)

    @evk_logger.log_call
    def tgl(self, devs, ram, row, data, length=1):
        """ Write contents of 'ram' at <row> with <data>.
        """
        ram = self._get_ram(ram)
        addr, size = self._spi._addr_and_size(self._get_ram(ram))
        rd_data = self._spi.rd(devs,addr + row,size)
        wr_data = data ^ rd_data
        return self._spi.wr(devs,addr + row, wr_data, size*length)

    @evk_logger.log_call
    def dump(self, devs, ram, rangeit=None, formatit='compact', printit=True):
        """ Read contents of 'ram'.
        """
        ram = self._get_ram(ram)
        addr, size = self._spi._addr_and_size(ram)
        if not rangeit:
            rangeit = [0,self.__rows[ram]]
        if not formatit:
            formatit = 'compact'
            
        resp = {'ram': ram, 'format':formatit}
        for row in range(rangeit[0],rangeit[1]):
            rd_resp = self.rd(devs,ram,row)
            data,fhex_size = self._int2format(ram,rd_resp,size,formatit)
            if printit:
                print ("{:3} | ".format(row),end='')
                for dat in data:
                    print ("{} ".format(fhex(dat,fhex_size)),end='')
                print('|')
            resp[row] = data
        if not printit:
            return resp


    @evk_logger.log_call
    def dump_wr(self, devs, ram, data, rangeit=None, formatit='compact', printit=True):
        """ Fill 'ram' with data.
        """
        resp = []
        ram = self._get_ram(ram)
        addr, size = self._spi._addr_and_size(ram)
        if not rangeit:
            rangeit = [0,self.__rows[ram]]
        if not formatit:
            formatit = 'compact'
        for row in range(rangeit[0],rangeit[1]):
            rd_resp = self.wrrd(devs,ram,row,data, printit)
            if printit:
                print ("{:3}: {:}".format(row, rd_resp))
            resp.append(rd_resp)
        if not printit:
            return resp

    @evk_logger.log_call
    def fill(self, devs, table_id=None, filename='ram_r5.xml'):
        """Reads a RAM XML file and writes the content to chip RAM.

        Args:
            devs (Rap object(s)): A single or a list of Rap objects.
            table_id (str, optional): The ID of table to read from XML file. 
                                      If no table ID is specified all tables are read and written to RAM.
                                      Defaults to None.
            filename (str, optional): XML file name including path to be loaded. Defaults to 'ram_r5.xml'.
        """
        if not os.path.isabs(filename):
            filename = env_config.env_config.ram_path()+'/'+filename
        evk_logger.evk_logger.log_bold('Reading RAM file {} ...'.format(filename))
        rf = ram_file.RamFile(filename)
        if table_id == None:
            table_id_list = rf.table_id_list()
        else:
            if not isinstance(table_id, list):
                table_id_list = [table_id]
        last_indices = {}
        for table_id in table_id_list:
            ram_table = rf.table_data(table_id)
            table_type = rf.table_tag_info(table_id, 'TYPE').lower()
            for row in ram_table.items():
                data, mask = self._fielddict2data(table_type, row[1])
                self.wr(devs, table_type, row[0], data)
            last_indices[table_id] = {'last_index':row[0]}
            evk_logger.evk_logger.log_bold('RAM table id {} written to RAM.'.format(table_id), indentation=4)
        return last_indices

    def file_info(self, filename='ram_r5.xml'):
        """Prints out information about the specified RAM XML file.
        The information included file header and table information.

        Args:
            filename (str, optional): The selected XML file name including path. Defaults to 'ram_r5.xml'.
        """
        if not os.path.isabs(filename):
            filename = env_config.env_config.ram_path()+'/'+filename
        rf = ram_file.RamFile(filename)
        rf.file_header()

    def get_ram_file(self, filename='ram_r5.xml'):
        if not os.path.isabs(filename):
            filename = env_config.env_config.ram_path()+'/'+filename
        return ram_file.RamFile(filename)

    def get_index(self, table_id, attribs_attrib_values, filename='ram_r5.xml'):
        """_summary_

        Args:
            table_id (str): ID of the table in the ram file to search. e.g. '25GHz'
            attribs_attrib_values (dict): A dictionary containing one or more pairs of attributes to search for. e.g. {'AZIMUTH':-15, 'ELEVATION':20}
            filename (str, optional): ram file to search in. Defaults to 'ram_r5.xml'.

        Returns:
            list: A list of beam indexes with matching attributes specified in attribs_attrib_values.
        """
        if not os.path.isabs(filename):
            filename = env_config.env_config.ram_path()+'/'+filename
        evk_logger.evk_logger.log_bold('Reading RAM file {} ...'.format(filename))
        rf = ram_file.RamFile(filename)
        return rf.find_index_by_tags(table_id, attribs_attrib_values)

