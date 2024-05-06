import time
import sys
import evk_logger

import connect
import version
from chip import chip
from evk.gui import gui_handler
import pwr
import misc
import adf4150
from common import *
import modstore
import gpio
import eeprom
#import cmd_server

class Host():
    def __init__(self, serial_num, bsp='rapvalbsp', fref=None, fdig=None, flo=None, fspi=None, indent=None):
        if fspi is not None:
            pass
        elif bsp == 'rapvalt':
            fspi = 1000000
        elif fspi is None:
            fspi = 10000000
        self._conn      = connect.Connect(serial_num=serial_num, bsp=bsp, clock_rate=fspi)
        self.version    = version.Version().get_version()
        if evk_logger.evk_logger == None:
            info_logger = self.info_file()
        if indent is None:
            self.indent = evk_logger.evk_logger._indent
        else:
            self.indent = indent
        self.versions(printit=True)
        self.chip       = chip.Chip(conn=self._conn, fref=fref, indent=self.indent)
        self.spi        = self.chip.spi
        self.ctrl       = self.chip.ctrl
        self.gpio       = gpio.Gpio(conn=self._conn)
        if bsp != 'none':
            self.eeprom     = eeprom.EEPROM(self._conn)
        self.bspload    = modstore.load
        self.bspsave    = modstore.save
        self.rapAll     = []
        num_devs        = self.chip._chip_info.get_num_devs()
        print("[HOST]The number of devices:{:}".format(num_devs))
        for dev_num in range(0,num_devs):
            exec("self.rap{:} = self.spi._connection.rap{:}".format(str(dev_num),str(dev_num)))
            exec("self.rapAll.append(self.rap{:})".format(str(dev_num)))
            self.set_vcm(self.chip._chip_info.get_dev(dev_num), 600)

        self.detected_chips = self.chip._chip_info.detect(printit=True)
        if self._conn.config.MB_TYPE == 'MB1':
            if len(self.detected_chips) != num_devs:
                evk_logger.evk_logger.log_info("Initial connection failed. Resetting devices ...",self.indent)
                self.reset(self.rapAll, printit=False)
                self.detected_chips  = self.chip._chip_info.detect(printit=True)

        if self._conn.config.MB_TYPE == 'MB2':
            self.pwr        = pwr.Pwr(self._conn)
            self.misc       = misc.Misc(self._conn)
            self.pll        = adf4150.Adf4150(self._conn,self.misc)
            if len(self.detected_chips) != num_devs:
                evk_logger.evk_logger.log_info("Initial connection failed. Initialising power and re-trying ...",self.indent)
                self.misc.init()
                self.pwr.init()
                self.ctrl.set_notreset(self.rapAll, 0)
                time.sleep(0.1)
                self.pwr.on('VDD1V8')
                time.sleep(0.1)
                self.ctrl.set_notreset(self.rapAll, 1)
                self.detected_chips  = self.chip._chip_info.detect(printit=True)

        if self._conn.config.MB_TYPE == 'DBMB':
            if len(self.detected_chips) != num_devs:
                evk_logger.evk_logger.log_info("Initial connection failed. Initialising power and re-trying ...",self.indent)
                self.detected_chips  = self.chip._chip_info.detect(printit=True)

        try:
            self.chip.update_revision_data(self.detected_chips[0].id)
        except IndexError:
            self.chip.update_revision_data(0)

        if self._conn.config.MB_TYPE == 'MB2':
            self.chip.ref_clk.set(self.rapAll,self.pll.setup()['vcxo_freq'])

        # from threading import Thread
        # self.cmd_server_thread = Thread(target=self.start_cmd_server)
        # self.cmd_server_thread.setDaemon(True)
        # self.cmd_server_thread.start()

    def start_cmd_server(self):
        cmdserver = cmd_server.MyService(self)
        from rpyc.utils.server import  ThreadedServer
        t = ThreadedServer(cmdserver, port=18861, protocol_config={"allow_public_attrs": True, "allow_all_attrs": True})
        t.start()

    def info_file(self, fname="evk.info"):
        evk_logger.evk_logger = evk_logger.EvkLogger(fname)
        return evk_logger.evk_logger

    def speed_test(self, dev, count=10000):
        evk_logger.CALL_ENTRY_PROCESS = False
        start_time = time.perf_counter()
        for n in range(count):
            x = self.spi.rd(dev, 'chip_id')
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print("Elapsed time: ", elapsed_time)
        evk_logger.CALL_ENTRY_PROCESS = True

    def open_gui(self,dev, extended=False):
        try:
            self.gui_handler.start_gui(dev, extended)
        except AttributeError:
            self.gui_handler = gui_handler.GuiHandler(self)
            self.gui_handler.start_gui(dev, extended)

    def _reset(self, dev, rst_time_ms=100):
        self.ctrl.set_notreset(dev, 0)
        time.sleep(rst_time_ms/1000)
        self.ctrl.set_notreset(dev, 1)
        
    @evk_logger.log_call
    def reset(self, devs, rst_time_ms=1, run_workaround=True, printit=True):
        """Reset devices.
           Examples: reset(rap0)
                     reset([rap0, rap1])
                     reset([rap0, rap1], 10)
        """
        if not isinstance(devs, list):
            devs = [devs]
        for dev in devs:
            self._reset(dev, rst_time_ms)
        if run_workaround:
            for dev in devs:
                if 'SW' in self.chip.info(dev)['workaround']:
                    self.chip.init(dev, 'AFTER RESET', printit)
                if 'Issue#94' in self.chip.info(dev)['workaround']:
                    self.chip.init(dev, 'EN VCC HIGH w OVR', printit)

    @evk_logger.log_call
    def set_vcm(self, devs, mV):
        self._conn.mb.set_vcm_dac(self._conn.board_id, mV)

    @evk_logger.log_call
    def versions(self,printit=False):
        mbdll_version   = self._conn.mb.mbdrv_version()
        api_version     = self.version
        ret = {"MB_DLL":mbdll_version, "API":api_version}
        if printit:
            print_dict(ret,self.indent+2)
        return ret

    @evk_logger.log_call
    def adjust_ref(self, devs, rf_offs, rf_freq):
        ref_offs=self.chip.synth.calc_ref_offs(devs,rf_offs, rf_freq)
        self.pll.adjust_ref(ref_offs)
        return self.chip.ref_clk.set(devs,self.pll.get_ref())

