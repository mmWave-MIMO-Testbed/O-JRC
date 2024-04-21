import evk_logger
from common import *

class Trx():

    __instance = None
    _pol  = {'SLEEP': 0b0001, 'SX': 0b1001,
             'RH': 0b0000, 'RV': 0b0010, 'RVRH': 0b0100, 'RHRV': 0b0100,
             'RVTH': 0b0110, 'THRV': 0b0110,
             'TH': 0b1000, 'TV': 0b1010, 'TVTH': 0b1110, 'THTV': 0b1110,
             'TVRH': 0b1100, 'RHTV': 0b1100
            }
    _cmd  = {'BEAM': [0], 'GAIN': [1], 'MODE': [3], 'ALL':[0,1,3]}
    _sync = {True:1, 1:1, 'True':1, '1':1, False:0, 0:0, 'False':0, '0':0}

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Trx, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        self._spi = spi


    @evk_logger.log_call
    def mode(self, devs, pol, sync=1):
        """
        """
        self._order(devs, cmd='MODE', pol=pol, data=0, sync=sync)


    @evk_logger.log_call
    def _order(self, devs, cmd, pol, data, sync=1):
        cmds = self._cmd[cmd.upper()]
        pol  = self._pol[pol.upper()]
        sync = self._sync[sync]    

        for cmd in cmds:
            self._spi.wr(devs, 'trx_control_reg',(data&0xFF) | (pol<<8) | (sync<<12) | (cmd<<13))
