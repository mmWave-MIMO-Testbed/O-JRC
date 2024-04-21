from common import *
import evk_logger
import math

class Fir():

    __instance = None
    __initialized = False


    def __new__(cls, spi, indent=None):
        if cls.__instance is None:
            cls.__instance = super(Fir, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi, indent=None):
        if Fir.__initialized is not True:
            self._spi       = spi
            if indent is None:
                self.indent = evk_logger.evk_logger._indent
            else:
                self.indent = indent
            self.order = 0xf
            Fir.__initialized = True

    @evk_logger.log_call
    def setup(self, devs,
              order=0xf,
              coeff=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
              ):
        """Sets up FIR filter (affects fir_cfg_0)

        Args:
            devs : Device or device list (ex. rap0)
            order (hexadecimal, optional): Order of FIR filter (0 to 16). Defaults to 15.

            coeff (dict, optional): FIR filter coefficients as either -0.5 to 0.5 or 0x0000 to 0xffff . Defaults to [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5].
        """
        if order > 0x10: order = 0x10
        if order < 0: order = 0
        self._spi.wr(devs, 'fir_cfg_0', {'order':order})
        self.order = order
        start_addr = self._spi.register_map.regs['fir_cfg_16']['addr']

        for addr_offset in range(0, 2*len(coeff), 2):
            if (coeff[addr_offset//2] >= -0.5) and (coeff[addr_offset//2] <= 0.5):
                if coeff[addr_offset//2] >= 0:
                    coeff_cfg_value = int(0x7fff * coeff[addr_offset//2] / 0.5)
                else:
                    coeff_cfg_value = int(0x7fff * coeff[addr_offset//2] / 0.5 * -1)
                    coeff_cfg_value = int(bin(~coeff_cfg_value)[3:],2) + 1
                self._spi.wr(devs, start_addr+addr_offset, coeff_cfg_value, 2)
            elif coeff[addr_offset//2] >= 0:
                self._spi.wr(devs, start_addr+addr_offset, coeff[addr_offset//2], 2)

    @evk_logger.log_call
    def enable(self, devs):
        """Enables the FIR filter.

        Args:
            devs : Device or device list (ex. rap0)
        """
        self._spi.wr(devs, 'fir_cfg_0', {'en':1})

    @evk_logger.log_call
    def disable(self, devs):
        """Disables the FIR filter.

        Args:
            devs : Device or device list (ex. rap0)
        """ 
        self._spi.wr(devs, 'fir_cfg_0', {'en':0})

    @evk_logger.log_call
    def get_data(self, devs):
        """Returns a dictionary containing fir_out_data and trunc_error flag.

        Args:
            devs : Device or device list (ex. rap0)

        Returns:
            dict: fir_out_data and trunc_error flag.
        """
        fir_data_out = (self._spi.rd(devs, 'fir_read_info_12')&0x7ff)
        trunc_error = (self._spi.rd(devs, 'fir_read_info_12')&0x1000)>>12

        return {'fir_data_out':fir_data_out, 'trunc_error':trunc_error}

    @evk_logger.log_call
    def clear_error(self, devs):
        """Clears the truncation error flag.

        Args:
            devs : Device or device list (ex. rap0)
        """
        self._spi.set(devs, 'fir_cfg_0', {'clear_err':1})



