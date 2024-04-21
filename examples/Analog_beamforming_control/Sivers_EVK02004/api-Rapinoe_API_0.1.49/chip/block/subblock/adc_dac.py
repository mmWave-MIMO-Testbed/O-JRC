import amux
import evk_logger
from common import *


class Adc_dac():


    __instance    = None

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Adc_dac, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        self.spi  = spi
        self.evk_logger = evk_logger.EvkLogger()

                



    @evk_logger.log_call
    def reset(self, devs):
        self.spi.clr(devs, 'adc_dac_cfg', 0x03)

    @evk_logger.log_call
    def enable(self, devs):
        self.spi.set(devs, 'adc_dac_cfg', 0x03)
        
    @evk_logger.log_call
    def disable(self, devs):
        self.spi.clr(devs, 'adc_dac_cfg', 0x01)


    @evk_logger.log_call
    def set(self, devs, val, repr='binoffs', auto=True):
        if repr.lower() == 'dec':
            val = dec2binoffs(val,10)
        elif repr.lower() == 'volt':
            val = volt2binoffs(val,10,1.2)
        if auto:
            self.spi.wr(devs, 'adc_dac_code', 1|(val<<4))
        else:
            self.spi.wr(devs, 'adc_dac_code', 0|(val<<4))
            self.spi.wr(devs, 'adc_dac_code', 1|(val<<4))
            self.spi.wr(devs, 'adc_dac_code', 0|(val<<4))

    @evk_logger.log_call
    def get(self, devs, repr='binoffs'):
        val = self.spi.rd(devs, 'adc_dac_code') >> 4
        if repr.lower() == 'dec':
            val = binoffs2dec(val,10)
        elif repr.lower() == 'volt':
            val = binoffs2volt(val,10,1.2)
        return val


    @evk_logger.log_call
    def adj_set(self, devs, val, auto=True):
        if auto:
            self.spi.wr(devs, 'adc_dac_adj_fs', (1<<4)|(val&0xF))
        else:
            self.spi.wr(devs, 'adc_dac_adj_fs', (0<<4)|(val&0xF))
            self.spi.wr(devs, 'adc_dac_adj_fs', (1<<4)|(val&0xF))
            self.spi.wr(devs, 'adc_dac_adj_fs', (0<<4)|(val&0xF))

    @evk_logger.log_call
    def adj_get(self, devs):
        return self.spi.rd(devs, 'adc_dac_adj_fs') & 0xF

