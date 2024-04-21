import evk_logger

from common import *


class Pca6107():

    def __init__(self, conn, i2c_addr, init=None, runinit=False):
        self._conn      = conn
        self._i2c_read  = conn.mb.i2c_read
        self._i2c_write = conn.mb.i2c_write
        self.board_id = conn.board_id
        self.i2c_addr   = i2c_addr
        self._init  = {'regs':[],'data':[],'printit':False}
        if init is not None:
            for key,val in init.items():
                self._init[key] = val
        if runinit:
            self.init()

    def wr(self, regs, data, printit=False):
        resp = []
        reg_resp = {}
        reg_list = []
        return_one = False
        if isinstance(self.i2c_addr,int):
            i2c_addr = [self.i2c_addr]
            return_one = True
        else:
            i2c_addr = self.i2c_addr
        if isinstance(regs,int):
            regs = [regs]
            if isinstance(data,int):
                data = [[data]]
        elif isinstance(regs,list):
            for i,dat in enumerate(data):
                if isinstance(dat,int):
                    data[i] = [dat]
        for one_addr in i2c_addr:
            for i,reg in enumerate(regs):
                data[i].insert(0,reg)
                self._i2c_write(self.board_id,one_addr,data[i],len(data[i]),
                    start_condition=True,stop_condition=True)

        
    def rd(self, regs, printit=False):
        resp = []
        reg_resp = {}
        reg_list = []
        return_dev_list = False
        return_reg_list = False
        if isinstance(self.i2c_addr,int):
            i2c_addr = [self.i2c_addr]
            return_dev_list = True
        else:
            i2c_addr = self.i2c_addr
        if isinstance(regs,int):
            regs = [regs]
            return_reg_list = True
        for one_addr in i2c_addr:
            for reg in regs:
                self._i2c_write(self.board_id,one_addr,[reg],1,
                    start_condition=True,stop_condition=False)
                reg_resp = self._i2c_read(self.board_id,one_addr,1,
                    start_condition=True,stop_condition=True,nack_last_byte=True)
                reg_list.append({'status':reg_resp['status'],'data':reg_resp['data'][0]})
                if printit:
                    evk_logger.evk_logger.log_info("{}".format(resp))
            resp.append(reg_list)
            reg_list       = []
        if return_dev_list:
            if return_reg_list:
                return resp[0][0]
            else:
                return resp[0]
        elif return_reg_list:
            return resp[0][0]
        else:
            return resp

    def dump(self, printit=False):
        return self.rd([0,1,2,3], printit)

    def init(self, regs=None, data=None, printit=None):
        if regs is None:
            regs = self._init['regs']
        if data is None:
            data = self._init['data']
        if printit is None:
            printit = self._init['printit']
        if len(regs) == 0 or len(data) == 0:
            if printit:
                evk_logger.evk_logger.log_info("No init performed")
            return
        self.wr(regs,data,printit)

