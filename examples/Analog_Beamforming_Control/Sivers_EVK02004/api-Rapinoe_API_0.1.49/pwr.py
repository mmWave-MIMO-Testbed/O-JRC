import evk_logger
import pca6107
from common import *


class Pwr(pca6107.Pca6107):

    def __init__(self, conn, runinit=False, indent=None):
        super().__init__(conn, i2c_addr=24,init={'regs':[1,2,3],'data':[0x00,0x00,0x80],'printit':False},runinit=runinit)
        self.input_ports  = {}
        self.output_ports = {'VDD1V8': 6,
                             'VCC3V3_SYNTH_B':5, 'VCC3V3_B2':4, 'VCC3V3_B1':3,
                             'VCC3V3_SYNTH_A':2, 'VCC3V3_A2':1, 'VCC3V3_A1':0}
        self.input_names  = list(self.input_ports.keys())
        self.output_names = list(self.output_ports.keys())
        if indent is None:
            self.indent = evk_logger.evk_logger._indent
        else:
            self.indent = indent


    @evk_logger.log_call
    def on(self, ports, printit=False):
        data_d = self.rd(1, printit)
        if data_d['status'] == 0:
            if isinstance(ports,str) and ports.upper() == 'ALL':
                ports = self.output_names
            data2wr = data_d['data']
            if isinstance(ports,dict) or isinstance(ports,list):
                for port in ports:
                    if isinstance(port,str):
                        if port.upper() in self.output_names:
                            data2wr |= (1 << self.output_ports[port.upper()])
                    if isinstance(port,int):
                        data2wr |= (1 << port)
            if isinstance(ports,str):
                if ports.upper() in self.output_names:
                    data2wr |= (1 << self.output_ports[ports.upper()])
            if isinstance(ports,int):
                data2wr |= (1 << ports)
            self.wr(1, data2wr, printit)


    @evk_logger.log_call
    def off(self, ports, printit=False):
        data_d = self.rd(1, printit)
        if data_d['status'] == 0:
            if isinstance(ports,str) and ports.upper() == 'ALL':
                ports = self.output_names
            data2wr = data_d['data']
            if isinstance(ports,dict) or isinstance(ports,list):
                for port in ports:
                    if isinstance(port,str):
                        if port.upper() in self.output_names:
                            data2wr &= ~(1 << self.output_ports[port.upper()])
                    if isinstance(port,int):
                        data2wr &= ~(1 << port)
            if isinstance(ports,str):
                if ports.upper() in self.output_names:
                    data2wr &= ~(1 << self.output_ports[ports.upper()])
            if isinstance(ports,int):
                data2wr &= ~(1 << ports)
            self.wr(1, data2wr, printit)


    @evk_logger.log_call
    def status(self, ports=None, printit=False):
        data_d = self.rd(0)
        if data_d['status'] == 0:
            data      = data_d['data']
            all_ports = {}
            all_ports.update(self.input_ports)
            all_ports.update(self.output_ports)
            all_names = self.input_names + self.output_names
            if ports is None:
                ports = all_ports
            if isinstance(ports,dict):
                resp = {}
                for port in ports:
                    if isinstance(port,str):
                        port = port.upper()
                        if port in all_names:
                            port_num = all_ports[port]
                    elif isinstance(port,int):
                        port_num = port
                    resp[port] = (data >> port_num) & 1
                    if printit:
                        evk_logger.evk_logger.log_info("{:}: {:}".format(port,resp[port]),self.indent)
            if isinstance(ports,list):
                resp = []
                for port in ports:
                    if isinstance(port,str):
                        port = port.upper()
                        if port in all_names:
                            port_num = all_ports[port]
                    elif isinstance(port,int):
                        port_num = port
                    resp.append((data >> port_num) & 1)
                    if printit:
                        evk_logger.evk_logger.log_info("{:}: {:}".format(port,resp[-1]),self.indent)
            if isinstance(ports,str):
                port = ports.upper()
                if port in all_names:
                    resp = (data >> all_ports[port]) & 1
                if printit:
                    evk_logger.evk_logger.log_info("{:}: {:}".format(port,resp),self.indent)
            if isinstance(ports,int):
                resp = (data >> ports) & 1
                if printit:
                    evk_logger.evk_logger.log_info("{:}: {:}".format(ports,resp),self.indent)
        else:
            resp = None
        return resp
