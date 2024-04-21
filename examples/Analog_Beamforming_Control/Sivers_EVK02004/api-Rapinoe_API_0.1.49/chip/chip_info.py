import register
import evk_logger
from common import *

class Chip_info():
    __instance = None

    _chip_info = {0x02512106: {'type': 'Rapinoe 28 GHz TO1',         'R-rev': '3', 'band': 28, 'fref_def':245.76e6, 'workaround': ['SW','Issue#12','Issue#66','Issue#87','Issue#94']},
                  0x12512106: {'type': 'Rapinoe 28 GHz TO1 Alt',     'R-rev': '3', 'band': 28, 'fref_def':245.76e6, 'workaround': ['SW','Issue#12','Issue#66','Issue#87','Issue#94']},
                  0x02612106: {'type': 'Rapinoe 39 GHz TO1',         'R-rev': '3', 'band': 39, 'fref_def':245.76e6, 'workaround': ['SW','Issue#12','Issue#66','Issue#87','Issue#94']},
                  0x12612106: {'type': 'Rapinoe 39 GHz TO1 Alt',     'R-rev': '3', 'band': 39, 'fref_def':245.76e6, 'workaround': ['SW','Issue#12','Issue#66','Issue#87','Issue#94']},
                  0x02522112: {'type': 'Rapinoe 28 GHz TO1 MMF',     'R-rev': '3', 'band': 28, 'fref_def':245.76e6, 'workaround': ['Issue#12','Issue#66','Issue#87','Issue#94']},
                  0x12522112: {'type': 'Rapinoe 28 GHz TO1 Alt MMF', 'R-rev': '3', 'band': 28, 'fref_def':245.76e6, 'workaround': ['Issue#12','Issue#66','Issue#87','Issue#94']},
                  0x02622112: {'type': 'Rapinoe 39 GHz TO1 MMF',     'R-rev': '3', 'band': 39, 'fref_def':245.76e6, 'workaround': ['Issue#12','Issue#66','Issue#87','Issue#94']},
                  0x12622112: {'type': 'Rapinoe 39 GHz TO1 Alt MMF', 'R-rev': '3', 'band': 39, 'fref_def':245.76e6, 'workaround': ['Issue#12','Issue#66','Issue#87','Issue#94']},
                  0x12532212: {'type': 'Rapinoe 28 GHz TO2',         'R-rev': '5', 'band': 28, 'fref_def':245.76e6, 'workaround': ['SW']}}
    _chip_no_resp = {'type': None, 'R-rev': None, 'band': None, 'fref_def': None, 'workaround': []}

    def __new__(cls, spi, indent=None):
        if cls.__instance is None:
            cls.__instance = super(Chip_info, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi, indent=None):
        if self.__initialized != True:
            self._spi   = spi
            if indent is None:
                self.indent = evk_logger.evk_logger._indent
            else:
                self.indent = indent
            self.__initialized = True


    @evk_logger.log_call
    def detect(self, devs='all', printit=None):
        dev_list = []

        if devs == 'all':
            devs = []
            for dev in range(0,self.get_num_devs()):
                devs.append(self.get_dev(dev))

        if not isinstance(devs, list):
            devs = [devs]

        for dev in devs:
            chip_id  = self._spi.rd(dev, 'chip_id')
            if chip_id in self._chip_info.keys():
                dev.id = chip_id
                dev_list.append(dev)
                if printit:
                    evk_logger.evk_logger.log_info("Device with id {:} detected.".format(fhex(chip_id,8)),self.indent)
            else:
                if printit is not None:
                    evk_logger.evk_logger.log_error("Device with id {:} not supported.".format(fhex(chip_id,8)),self.indent)

        return dev_list


    @evk_logger.log_call
    def get(self, devs, printit=False):
        resp = []
        return_one = False

        if not isinstance(devs, list):
            devs = [devs]
            return_one = True

        for dev in devs:
            chip_id  = self._spi.rd(dev, 'chip_id')
            dev_info = {'chip_id': chip_id}
            if chip_id in self._chip_info.keys():
                dev_info.update(self._chip_info[chip_id])
            else:
                if printit is not None:
                    evk_logger.evk_logger.log_error("  Device with id {:} not supported.".format(fhex(chip_id,8)),self.indent)
                dev_info.update(self._chip_no_resp)
            resp.append(dev_info)

        if return_one:
            return resp[0]
        else:
            return resp


    @evk_logger.log_call
    def get_num_devs(self, printit=False):
        max_num_devs = 10
        for dev in range(0,max_num_devs):
            try:
                exec("self._spi._connection.rap"+str(dev))
            except:
                return dev
        return max_num_devs

    @evk_logger.log_call
    def get_dev(self, num, printit=False):
        return eval("self._spi._connection.rap"+str(num))