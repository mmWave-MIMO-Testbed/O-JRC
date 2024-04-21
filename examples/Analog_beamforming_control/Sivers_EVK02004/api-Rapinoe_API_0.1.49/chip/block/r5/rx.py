import evk_logger
from common import *

class Rx():

    __instance = None
    _bb_rx_cfg = 0b1000000000
    _bb_cfg_if = 0b1100000000
    _bb_cfg_bb = 0b1011111111
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
            cls.__instance = super(Rx, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi, ram):
        if self.__initialized:
            return
        self.__initialized = True
        self._spi = spi
        self.ram = ram
        self.rx_ram_table_id = {'V':'RXRAMV01', 'H':'RXRAMH01'}

    @evk_logger.log_call
    def setup_bb(self, devs, mode, pol):
        """
        """
        # Set rx IF or Rx BB mode
        if isinstance(mode,str) and isinstance(pol,str):
            if mode.upper() == 'IF':
                if (pol.upper() == 'RVRH') or (pol.upper() == 'RHRV'):
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_v', self._bb_cfg_if)
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_h', self._bb_cfg_if)
                    self._spi.wr(devs,'bb_rx_config_v', self._bb_rx_cfg)
                    self._spi.wr(devs,'bb_rx_config_h', self._bb_rx_cfg)
                elif (pol.upper() == 'RV') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_v', self._bb_cfg_if)
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_h', 0)
                    self._spi.wr(devs,'bb_rx_config_v', self._bb_rx_cfg)
                    self._spi.wr(devs,'bb_rx_config_h', 0)
                elif (pol.upper() == 'RH') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_v', 0)
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_h', self._bb_cfg_if)
                    self._spi.wr(devs,'bb_rx_config_v', 0)
                    self._spi.wr(devs,'bb_rx_config_h', self._bb_rx_cfg)
                else:
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_v', 0)
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_h', 0)
                    self._spi.wr(devs,'bb_rx_config_v', 0)
                    self._spi.wr(devs,'bb_rx_config_h', 0)
            if mode.upper() == 'BB':
                if (pol.upper() == 'RVRH') or (pol.upper() == 'RHRV'):
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_v', self._bb_cfg_bb)
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_h', self._bb_cfg_bb)
                    self._spi.wr(devs,'bb_rx_config_v', self._bb_rx_cfg)
                    self._spi.wr(devs,'bb_rx_config_h', self._bb_rx_cfg)
                elif (pol.upper() == 'RV') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_v', self._bb_cfg_bb)
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_h', 0)
                    self._spi.wr(devs,'bb_rx_config_v', self._bb_rx_cfg)
                    self._spi.wr(devs,'bb_rx_config_h', 0)
                elif (pol.upper() == 'RH') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_v', 0)
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_h', self._bb_cfg_bb)
                    self._spi.wr(devs,'bb_rx_config_v', 0)
                    self._spi.wr(devs,'bb_rx_config_h', self._bb_rx_cfg)
                else:
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_v', 0)
                    self._spi.wr(devs,'ssw_cfg_on_en_rx_h', 0)
                    self._spi.wr(devs,'bb_rx_config_v', 0)
                    self._spi.wr(devs,'bb_rx_config_h', 0)


    @evk_logger.log_call
    def setup_rf(self, devs, pol, latitude):
        """
        """
        if isinstance(latitude,str) and isinstance(pol,str):
            if (latitude.upper() == 'WE') or (latitude.upper() == 'EW'):
                if (pol.upper() == 'RVRH') or (pol.upper() == 'RHRV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x77) # W, E, V, H
                elif (pol.upper() == 'RV') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x70) # W, E, V
                elif (pol.upper() == 'RH') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x07) # W, E, H
                else:
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x00) # None
            elif latitude.upper() == 'W':
                if (pol.upper() == 'RVRH') or (pol.upper() == 'RHRV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x66) # W, V, H
                elif (pol.upper() == 'RV') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x60) # W, V
                elif (pol.upper() == 'RH') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x06) # W, H
                else:
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x00) # None
            elif latitude.upper() == 'E':
                if (pol.upper() == 'RVRH') or (pol.upper() == 'RHRV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x55) # E, V, H
                elif (pol.upper() == 'RV') or (pol.upper() == 'THRV') or (pol.upper() == 'RVTH'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x50) # E, V
                elif (pol.upper() == 'RH') or (pol.upper() == 'TVRH') or (pol.upper() == 'RHTV'):
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x05) # E, H
                else:
                    self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x00) # None
            else:
                self._spi.wr(devs,'ssw_cfg_on_sel_rx', 0x00) # None


    @evk_logger.log_call
    def setup(self, devs, mode, pol, latitude='WE', ant_en_v='DEFAULT', ant_en_h='DEFAULT'):
        """
        """
        self.ram.fill(devs, table_id=self.rx_ram_table_id['V'])
        self.ram.fill(devs, table_id=self.rx_ram_table_id['H'])
        self.setup_bb(devs, mode, pol)
        self.setup_rf(devs, pol, latitude)
        if ant_en_v is not None:
            if isinstance(ant_en_v,str) and (ant_en_v.upper() == 'DEFAULT'):
                ant_en_v = self.antenna_en_v_default
            self._spi.wr(devs,'ssw_cfg_on_bf_en_rx_v', ant_en_v)
        if ant_en_h is not None:
            if isinstance(ant_en_h,str) and (ant_en_h.upper() == 'DEFAULT'):
                ant_en_h = self.antenna_en_h_default
            self._spi.wr(devs,'ssw_cfg_on_bf_en_rx_h', ant_en_h)

    @evk_logger.log_call
    def gain(self, devs, index, pol='RVRH', sync=1):
        """
        """
        self._order(devs, cmd='GAIN', pol=pol, data=index, sync=sync)
        
        
    @evk_logger.log_call
    def beam(self, devs, index, pol='RVRH', sync=1):
        """
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
        return self.rx_ram_table_id[pol.upper()]

    def set_selected_gain_table(self, pol, id):
        self.rx_ram_table_id[pol.upper()] = id

    @evk_logger.log_call
    def override_mode(self, devs, enable):
        if not enable:
            self._spi.wr(devs, 'sel_rx_override', 0)
            self._spi.wr(devs, 'en_rx_v_override', 0)
            self._spi.wr(devs, 'en_rx_h_override', 0)
            self._spi.wr(devs, 'bf_en_rx_v_override', 0)
            self._spi.wr(devs, 'bf_en_rx_h_override', 0)
        else:
            self._spi.wr(devs, 'sel_rx_override', 0x77)
            self._spi.wr(devs, 'en_rx_v_override', 0x3ff)
            self._spi.wr(devs, 'en_rx_h_override', 0x3ff)
            self._spi.wr(devs, 'bf_en_rx_v_override', 0xffff)
            self._spi.wr(devs, 'bf_en_rx_h_override', 0xffff)

    @evk_logger.log_call
    def curr_gain_index(self, devs, pol):
        if (pol.lower() == 'rv') or (pol.lower() == 'v'):
            pol_suffix = 'v'
        else:
            pol_suffix = 'h'

        return self._spi.rd(devs, 'rx_gain_current_index_' + pol_suffix)
