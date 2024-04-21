import evk_logger
from common import *

class Tx():

    __instance = None
    _bb_cfg_if = 0b11011001111
    _bb_cfg_bb = 0b10011100111
    antenna_en_v_default = 0x0100
    antenna_en_h_default = 0x0000
    _pol  = {'SLEEP': 0b0001, 'SX': 0b1001,
             'RH': 0b0000, 'RV': 0b0010, 'RVRH': 0b0100, 'RHRV': 0b0100,
             'RVTH': 0b0110, 'THRV': 0b0110,
             'TH': 0b1000, 'TV': 0b1010, 'TVTH': 0b1110, 'THTV': 0b1110,
             'TVRH': 0b1100, 'RHTV': 0b1100
            }
    _cmd  = {'BEAM': [0], 'GAIN': [1], 'MODE': [3], 'ALL':[0,1,3]}
    _sync = {True:1, 1:1, 'True':1, '1':1, False:0, 0:0, 'False':0, '0':0}

    def __new__(cls, spi, ram):
        if cls.__instance is None:
            cls.__instance = super(Tx, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi, ram):
        if self.__initialized:
            return
        self.__initialized = True
        self._spi = spi
        self.ram = ram
        self.tx_ram_table_id = {'V':'TXRAMV01', 'H':'TXRAMH01'}

    @evk_logger.log_call
    def setup_bb(self, devs, mode, pol):
        """
        """
        # Set Tx IF or Tx BB mode
        if isinstance(mode,str) and isinstance(pol,str):
            if mode.upper() == 'IF':
                if (pol.upper() == 'TVTH') or (pol.upper() == 'THTV'):
                    self._spi.wr(devs,'bb_tx_config_v', self._bb_cfg_if)
                    self._spi.wr(devs,'bb_tx_config_h', self._bb_cfg_if)
                elif (pol.upper() == 'TV') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'bb_tx_config_v', self._bb_cfg_if)
                    self._spi.wr(devs,'bb_tx_config_h', 0)
                elif (pol.upper() == 'TH') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'bb_tx_config_v', 0)
                    self._spi.wr(devs,'bb_tx_config_h', self._bb_cfg_if)
                else:
                    self._spi.wr(devs,'bb_tx_config_v', 0)
                    self._spi.wr(devs,'bb_tx_config_h', 0)
                self._spi.wr(devs,'bb_tx_ctune', 0x44)
            if mode.upper() == 'BB':
                if (pol.upper() == 'TVTH') or (pol.upper() == 'THTV'):
                    self._spi.wr(devs,'bb_tx_config_v', self._bb_cfg_bb)
                    self._spi.wr(devs,'bb_tx_config_h', self._bb_cfg_bb)
                elif (pol.upper() == 'TV') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'bb_tx_config_v', self._bb_cfg_bb)
                    self._spi.wr(devs,'bb_tx_config_h', 0)
                elif (pol.upper() == 'TH') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'bb_tx_config_v', 0)
                    self._spi.wr(devs,'bb_tx_config_h', self._bb_cfg_bb)
                else:
                    self._spi.wr(devs,'bb_tx_config_v', 0)
                    self._spi.wr(devs,'bb_tx_config_h', 0)
                self._spi.wr(devs,'bb_tx_ctune', 0xcc)


    @evk_logger.log_call
    def setup_rf(self, devs, pol, latitude):
        """
        """
        if isinstance(latitude,str) and isinstance(pol,str):
            if (latitude.upper() == 'WE') or (latitude.upper() == 'EW'):
                if (pol.upper() == 'TVTH') or (pol.upper() == 'THTV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x77) # W, E, V, H
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x33) #       V, H
                elif (pol.upper() == 'TV') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x70) # W, E, V
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x30) #       V
                elif (pol.upper() == 'TH') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x07) # W, E, H
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x03) #       H
                else:
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x00) # None
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x00) # None
            elif latitude.upper() == 'W':
                if (pol.upper() == 'TVTH') or (pol.upper() == 'THTV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x66) # W, V, H
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x33) #    V, H
                elif (pol.upper() == 'TV') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x60) # W, V
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x30) #    V
                elif (pol.upper() == 'TH') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x06) # W, H
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x03) #    H
                else:
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x00) # None
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x00) # None
            elif latitude.upper() == 'E':
                if (pol.upper() == 'TVTH') or (pol.upper() == 'THTV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x55) # E, V, H
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x33) #    V, H
                elif (pol.upper() == 'TV') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x50) # E, V
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x30) #    V
                elif (pol.upper() == 'TH') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x05) # E, H
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x03) #    H
                else:
                    self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x00) # None
                    self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x00) # None
            else:
                self._spi.wr(devs,'ssw_cfg_on_sel_tx', 0x00) # None
                self._spi.wr(devs,'ssw_cfg_on_en_tx',  0x00) # None


    @evk_logger.log_call
    def setup(self, devs, mode, pol, latitude='WE', ant_en_v='DEFAULT', ant_en_h='DEFAULT'):
        """
        """
        self.ram.fill(devs, table_id=self.tx_ram_table_id['V'])
        self.ram.fill(devs, table_id=self.tx_ram_table_id['H'])
        self.setup_bb(devs, mode, pol)
        self.setup_rf(devs, pol, latitude)
        if ant_en_v is not None:
            if isinstance(ant_en_v,str) and (ant_en_v.upper() == 'DEFAULT'):
                ant_en_v = self.antenna_en_v_default
            self._spi.wr(devs,'ssw_cfg_on_bf_en_tx_v', ant_en_v)
        if ant_en_h is not None:
            if isinstance(ant_en_h,str) and (ant_en_h.upper() == 'DEFAULT'):
                ant_en_h = self.antenna_en_h_default
            self._spi.wr(devs,'ssw_cfg_on_bf_en_tx_h', ant_en_h)


    @evk_logger.log_call
    def gain_bb(self, devs, bb_v, bb_h):
        """
        """
        bb_gain = ((bb_v & 0x1F) << 8) | (bb_h & 0x1F)
        self._spi.wr(devs,'bb_tx_gain', bb_gain)
        return self._spi.rd(devs,'bb_tx_gain')

    def save_gain_index_to_ram(self, devs, index, pol):
        V_OFFSET = 60
        H_OFFSET = 61
        RAM_ADDR = 0x600
        if not isinstance(devs,list):
            devs = [devs]
        for dev in devs:
            if 'V' in pol:
                r = self._spi.rd(dev, RAM_ADDR+V_OFFSET, 10) & 0x3fffffffffffffffff
                r = r + (index << 70)
                self._spi.wr(dev, RAM_ADDR+V_OFFSET, r, 10)
            if 'H' in pol:
                r = self._spi.rd(dev, RAM_ADDR+H_OFFSET, 10) & 0x3fffffffffffffffff
                r = r + (index << 70)
                self._spi.wr(dev, RAM_ADDR+H_OFFSET, r, 10)

    def load_gain_index_from_ram(self, devs, pol):
        V_OFFSET = 60
        H_OFFSET = 61
        RAM_ADDR = 0x600
        if pol.lower() == 'v' or pol.lower() == 'tv':
            index = (self._spi.rd(devs, RAM_ADDR+V_OFFSET, 10) & 0xffc00000000000000000) >> 70
        else:
            index = (self._spi.rd(devs, RAM_ADDR+H_OFFSET, 10) & 0xffc00000000000000000) >> 70
        return index

    @evk_logger.log_call
    def gain_rf(self, devs, index, pol='TVTH', sync=1):
        """
        """
        self._order(devs, cmd='GAIN', pol=pol, data=index, sync=sync)
        self.save_gain_index_to_ram(devs, index, pol)

    @evk_logger.log_call
    def beam(self, devs, index, pol='TVTH', sync=1):
        """Sets TX beam to the specified index.

        Args:
            devs (RapX): Device ID (e.g. rap0)
            index (int): Specifies the beam index
            pol (str, optional): TX polarization. 'TV', 'TH' or 'TVTH'. Defaults to 'TVTH'.
            sync (int, optional): If set to 1 the new beam will be activated immediately. Defaults to 1.
        """
        self._order(devs, cmd='BEAM', pol=pol, data=index, sync=sync)

    @evk_logger.log_call
    def _order(self, devs, cmd, pol, data, sync=1):
        cmds = self._cmd[cmd.upper()]
        pol  = self._pol[pol.upper()]
        sync = self._sync[sync]

        for cmd in cmds:
            self._spi.wr(devs, 'trx_control_reg',(data&0xFF) | (pol<<8) | (sync<<12) | (cmd<<13))

    def get_selected_gain_table(self, pol):
        return self.tx_ram_table_id[pol.upper()]

    def set_selected_gain_table(self, pol, id):
        self.tx_ram_table_id[pol.upper()] = id

    @evk_logger.log_call
    def override_mode(self, devs, enable):
        if not enable:
            self._spi.wr(devs, 'sel_tx_override', 0)
            self._spi.wr(devs, 'en_tx_override', 0)
            self._spi.wr(devs, 'bf_en_tx_v_override', 0)
            self._spi.wr(devs, 'bf_en_tx_h_override', 0)
        else:
            self._spi.wr(devs, 'sel_tx_override', 0x77)
            self._spi.wr(devs, 'en_tx_override', 0x33)
            self._spi.wr(devs, 'bf_en_tx_v_override', 0xffff)
            self._spi.wr(devs, 'bf_en_tx_h_override', 0xffff)

    @evk_logger.log_call
    def curr_gain_index(self, devs, pol):
        if (pol.lower() == 'tv') or (pol.lower() == 'v'):
            pol_suffix = 'v'
        else:
            pol_suffix = 'h'

        return self.load_gain_index_from_ram(devs, pol)
