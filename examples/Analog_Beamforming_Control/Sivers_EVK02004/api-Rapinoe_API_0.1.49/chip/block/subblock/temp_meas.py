import adc
from common import *
import evk_logger

class Temp_meas():

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Temp_meas, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance


    def __init__(self):
        self.evk_logger  = evk_logger.EvkLogger()
        self._meas_data = {}


    @evk_logger.log_call
    def add(self, devs, temp, adc=None, src=None):
        return_one = False
        resp = []
        if not isinstance(devs, list):
            devs = [devs]
            return_one = True
        if isinstance(temp,int) or isinstance(temp,float):
            if isinstance(adc,int) or isinstance(adc,float):
                if src is None:
                    self.evk_logger.log_error("When first argument is integer/float and second argument is integer/float, then third argument must indicate source")
                    return None
                else:
                    for dev in devs:
                        if dev not in self._meas_data.keys():
                            self._meas_data[dev] = {}
                        if src not in self._meas_data[dev].keys():
                            self._meas_data[dev][src] = {}
                            self._meas_data[dev][src]['temp'] = [temp]
                            self._meas_data[dev][src]['adc'] = [adc]
                        else:
                            self._meas_data[dev][src]['temp'].append(temp)
                            self._meas_data[dev][src]['adc'].append(adc)
                        resp.append(self._meas_data[dev])
                    if return_one:
                        return resp[0]
                    else:
                        return resp
            elif not isinstance(adc,dict):
                self.evk_logger.log_error("When first argument is integer/float and second argument is not integer/gloat, it must be a dictionary, in which key is the source used and value is the ADC-value")
                return None
            elif src is not None:
                self.evk_logger.log_error("When first argument is integer or float and second argument is a dictionary, then third argument should not be supplied")
                return None
            else:
                for dev in devs:
                    if dev not in self._meas_data.keys():
                        self._meas_data[dev] = {}
                    for src in adc:
                        if src not in self._meas_data[dev].keys():
                            self._meas_data[dev][src] = {}
                            self._meas_data[dev][src]['temp'] = [temp]
                            self._meas_data[dev][src]['adc'] = [adc[src]]
                        else:
                            self._meas_data[dev][src]['temp'].append(temp)
                            self._meas_data[dev][src]['adc'].append(adc[src])
                    resp.append(self._meas_data[dev])
                if return_one:
                    return resp[0]
                else:
                    return resp
        elif isinstance(temp,dict):
            for dev in devs:
                if dev not in self._meas_data.keys():
                    self._meas_data[dev] = {}
                for temp_ in temp:
                    for src in temp[temp_]:
                        if src not in self._meas_data[dev].keys():
                            self._meas_data[dev][src] = {}
                            self._meas_data[dev][src]['temp'] = [temp_]
                            self._meas_data[dev][src]['adc']  = [temp[temp_][src]]
                        else:
                            self._meas_data[dev][src]['temp'].append(temp_)
                            self._meas_data[dev][src]['adc'].append(temp[temp_][src])
                resp.append(self._meas_data[dev])
            if return_one:
                return resp[0]
            else:
                return resp
        else:
            self.evk_logger.log_error("temp not int nor float")


    @evk_logger.log_call
    def get(self, devs, srcs='all'):
        return_one = False
        resp = []
        if not isinstance(devs, list):
            devs = [devs]
            return_one = True
        for dev in devs:
            if dev in self._meas_data.keys():
                if srcs == 'all':
                    resp.append(self._meas_data[dev])
                elif isinstance(srcs,str):
                    if srcs in self._meas_data[dev].keys():
                        resp.append({srcs:self._meas_data[dev][srcs]})
                elif isinstance(srcs,list):
                    resp_dict = {}
                    for src in srcs:
                        if src in self._meas_data[dev].keys():
                            resp_dict.update({src:self._meas_data[dev][src]})
                    resp.append(resp_dict)
            else:
                resp.append({})
        if return_one:
            return resp[0]
        else:
            return resp


    @evk_logger.log_call
    def clear(self, devs, srcs='all'):
        return_one = False
        resp = []
        if not isinstance(devs, list):
            devs = [devs]
            return_one = True
        for dev in devs:
            if dev in self._meas_data.keys():
                if srcs == 'all':
                    self._meas_data[dev].clear()
                elif isinstance(srcs,str):
                    if srcs in self._meas_data[dev].keys():
                        self._meas_data[dev][srcs].clear()
                elif isinstance(srcs,list):
                    for src in srcs:
                        if src in self._meas_data[dev].keys():
                            self._meas_data[dev][src].clear()


    @evk_logger.log_call
    def cal(self, devs, srcs='all', method='orthogonal'):
        return_one = False
        resp = []
        if not isinstance(devs, list):
            devs = [devs]
            return_one = True
        for dev in devs:
            if dev in self._meas_data.keys():
                src_res = {}
                if srcs == 'all':
                    for src in self._meas_data[dev].keys():
                        p = linregr(self._meas_data[dev][src]['adc'],self._meas_data[dev][src]['temp'],method)
                        src_res.update({src:p})
                elif isinstance(srcs,str):
                    if srcs in self._meas_data[dev].keys():
                        p = linregr(self._meas_data[dev][src]['adc'],self._meas_data[dev][src]['temp'],method)
                        src_res.update({src:p})
                elif isinstance(srcs,list):
                    for src in srcs:
                        if src in self._meas_data[dev].keys():
                            p = linregr(self._meas_data[dev][src]['adc'],self._meas_data[dev][src]['temp'],method)
                            src_res.update({src:p})
            else:
                src_res = {}

            resp.append(src_res)
        if return_one:
            return resp[0]
        else:
            return resp




