import adc
import temp_meas
import chip_info
from common import *
import evk_logger

class Temp():

    __instance = None

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Temp, cls).__new__(cls)
            cls.__instance.__initialized = False
            cls.__instance.is_checked = False
            cls.__instance.is_calibrated = False
        return cls.__instance


    def __init__(self, spi):
        if self.__initialized != True:
            self._spi       = spi
            self.adc        = adc.Adc(spi)
            self._chip_info = chip_info.Chip_info(spi)
            self.meas       = temp_meas.Temp_meas()
            self.src        = {'SYNTH': {'enable': {},                             'activate': {'sm_en' : 0x08}},
                               'COM':   {'enable': {'com_misc' : 0x02},            'activate': {'com_misc': 0x01}},
                               'RX H':  {'enable': {'ssw_cfg_on_en_rx_h' : 0x100}, 'activate': {'bb_rx_config_h' : 0x100}},
                               'RX V':  {'enable': {'ssw_cfg_on_en_rx_v' : 0x100}, 'activate': {'bb_rx_config_v' : 0x100}},
                               'BF W':  {'enable': {'bf_biasref_en' : 0x20},       'activate': {'bf_biasref_en': 0x40}},
                               'BF E':  {'enable': {'bf_biasref_en' : 0x02},       'activate': {'bf_biasref_en': 0x04}},
                               'TX H':  {'enable': {'bb_tx_config_h' : 0x400},     'activate': {'bb_tx_config_h': 0x100}},
                               'TX V':  {'enable': {'bb_tx_config_v' : 0x400},     'activate': {'bb_tx_config_v': 0x100}}
                              } 
            self.src_names  = [key for key in self.src]
            self.conv_dec   = {}
            for dev_num in range(0,self._chip_info.get_num_devs()):
                dev         = self._chip_info.get_dev(dev_num)
                self.conv_dec.update({dev: {'SYNTH': {'slope':0.26, 'offs':15.644},
                                            'COM':   {'slope':0.26, 'offs':15.644},
                                            'RX H':  {'slope':0.26, 'offs':15.644},
                                            'RX V':  {'slope':0.26, 'offs':15.644},
                                            'BF W':  {'slope':0.26, 'offs':15.644},
                                            'BF E':  {'slope':0.26, 'offs':15.644},
                                            'TX H':  {'slope':0.26, 'offs':15.644},
                                            'TX V':  {'slope':0.26, 'offs':15.644}
                                           }
                                      })
            self.__initialized = True

    def volt2temp(self,dev,src,volt):
        return round(self.conv_dec[dev][src]['slope'] * volt * 1024/1.2 + self.conv_dec[dev][src]['offs'],2)

    def dec2temp(self,dev,src,dec):
        return round(self.conv_dec[dev][src]['slope'] * dec + self.conv_dec[dev][src]['offs'],2)

    @evk_logger.log_call
    def reset(self, devs):
        self.deactivate(devs,'all')
        self.disable(devs,'all')


    @evk_logger.log_call
    def isenable(self, devs):
        enabled_units = []
        for unit in self.src:
            enabled = True
            for reg,val in self.src[unit]['enable'].items():
                data = self._spi.rd(devs,reg)
                if not (data & val):
                    enabled = False
            if enabled:
                enabled_units.append(unit)
        return enabled_units


    @evk_logger.log_call
    def isactive(self, devs):
        active_units = []
        for unit in self.src:
            active = True
            for reg,val in self.src[unit]['activate'].items():
                data = self._spi.rd(devs,reg)
                if not (data & val):
                    active = False
            if active:
                active_units.append(unit)
        return active_units


    @evk_logger.log_call
    def isrunning(self, devs):
        running_units = []
        for unit in self.src:
            if unit in self.isenable(devs) and unit in self.isactive(devs):
                running_units.append(unit)
        return running_units


    @evk_logger.log_call
    def enable(self, devs, units=None):
        if units is not None:
            if isinstance(units,str):
                if units.lower() == 'all':
                    units = self.src.keys()
                else:
                    units = [units]
            for unit in units:
                if unit in self.src:
                    # Enable selected and existing unit
                    for reg,val in self.src[unit]['enable'].items():
                        new_val = self._spi.rd(devs,reg) | val
                        self._spi.wr(devs,reg,new_val)
                else:
                    evk_logger.evk_logger.log_info("Temp unit '{:}' does not exist. \nPlease select from {:}.".format(unit,self.src_names))
        return self.isenable(devs)


    @evk_logger.log_call
    def disable(self, devs, units=None):
        if units is not None:
            if isinstance(units,str):
                if units.lower() == 'all':
                    units = self.src.keys()
                else:
                    units = [units]
            for unit in units:
                if unit in self.src:
                    # Disable selected and existing unit
                    for reg,val in self.src[unit]['enable'].items():
                        new_val = self._spi.rd(devs,reg) & ~val
                        self._spi.wr(devs,reg,new_val)
                else:
                        evk_logger.evk_logger.log_info("Temp unit '{:}' does not exist. \nPlease select from {:}.".format(unit,self.src_names))
        return self.isenable(devs)


    @evk_logger.log_call
    def activate(self, devs, unit=None, printit=True):
        if unit is not None:
            if unit in self.src:
                # Deactivate running unit if it is not the same as the one requested
                if unit not in self.isrunning(devs):
                    for dunit in self.isactive(devs):
                        if printit:
                            evk_logger.evk_logger.log_info("Deactivate {:}".format(dunit))
                        for reg,val in self.src[dunit]['activate'].items():
                            new_val = self._spi.rd(devs,reg) & ~val
                            self._spi.wr(devs,reg,new_val)
                    # Activate requested unit
                    if printit:
                        evk_logger.evk_logger.log_info("Activate {:}".format(unit))
                    for reg,val in self.src[unit]['activate'].items():
                        new_val = self._spi.rd(devs,reg) | val
                        self._spi.wr(devs,reg,new_val)
            else:
                evk_logger.evk_logger.log_info("Temp unit '{:}' does not exist. \nPlease select from {:}.".format(unit,self.src_names))
        return self.isactive(devs)


    @evk_logger.log_call
    def deactivate(self, devs, units='all'):
        if units == 'all':
            units = self.src.keys()
        if isinstance(units,str):
            units = [units]
        for unit in units:
            if unit in self.src:
                # Deactivate selected and existing unit
                for reg,val in self.src[unit]['activate'].items():
                    new_val = self._spi.rd(devs,reg) & ~val
                    self._spi.wr(devs,reg,new_val)
            else:
                evk_logger.evk_logger.log_info("Temp unit '{:}' does not exist. \nPlease select from {:}.".format(unit,self.src_names))                
        return self.isactive(devs)


    @evk_logger.log_call
    def get(self, devs, src, formatit='adc', printit=True, enable_activate='both'):
        if src in self.src_names:
            if enable_activate is not None:
                if (enable_activate.lower() == 'enable') or (enable_activate.lower() == 'both'):
                    self.enable(devs,src)
                if (enable_activate.lower() == 'activate') or (enable_activate.lower() == 'both'):
                    self.activate(devs,src,printit)
            if formatit.lower() == 'temp' or formatit.lower() == 'volt':
                formatit_ = 'volt'
            elif formatit.lower() == 'adc' or formatit.lower() == 'dec':
                formatit_ = 'dec'
            else:
                formatit_ = formatit
            adc_data = self.adc.get_data(devs,'PTAT Sense',formatit_)
        else:
            adc_data = 0
        if formatit.lower() == 'temp' or formatit.lower() == 'volt':
            adc_data = self.volt2temp(devs,src,adc_data)
        elif formatit.lower() == 'adc' or formatit.lower() == 'dec':
            adc_data = self.dec2temp(devs,src,adc_data)
        return adc_data


    @evk_logger.log_call
    def dump(self, devs, srcs='all', formatit='temp', printit=False, enable_activate='both'):
        resp = {}
        if srcs == 'all':
            srcs = self.src_names
        for src in srcs:
            resp[src] = self.get(devs,src,formatit,printit,enable_activate)
        return resp

    @evk_logger.log_call
    def cal(self, devs, srcs='all', method='orthogonal'):
        if not isinstance(devs, list):
            devs = [devs]
        for dev in devs:
            cal = self.meas.cal(dev,srcs,method)
            for src in cal:
                self.conv_dec[dev][src]=cal[src]

    @evk_logger.log_call
    def cal_get(self, devs, srcs='all'):
        return_one = False
        resp = []
        if not isinstance(devs, list):
            devs = [devs]
            return_one = True
        if srcs == 'all':
            srcs = self.src_names
        elif isinstance(srcs, str):
            srcs = [srcs]
        for dev in devs:
            src_dict = {}
            for src in srcs:
                if src in self.src_names:
                    src_dict.update({src:self.conv_dec[dev][src]})
            resp.append(src_dict)
        if return_one:
            return resp[0]
        else:
            return resp

