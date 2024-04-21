import numpy as np
import evk_logger
import amux
import chip_info
import ref_clk
import sd
import synth_adc
from common import *
import time

class Synth():

    __instance = None
    sm_dac_ref = 1.13
    vco_amp_28 = 0.725
    vco_amp_39 = 1.1
    chp_28    = [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,
                 7,7,7,7,7,6,6,6,6,6,6,5,5,5,5,5,
                 5,5,5,4,4,4,4,4,4,4,4,3,3,3,3,3,
                 3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,
                 7,7,7,7,7,7,7,7,6,6,6,6,6,6,6,6,
                 5,5,5,5,5,5,5,5,4,4,4,4,4,4,4,3,
                 3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,
                 2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1]
    chp_39    = [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,
                 7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,
                 7,7,7,7,6,6,6,6,6,6,6,6,6,6,6,6,
                 6,6,6,6,6,6,6,6,6,6,5,5,5,5,5,5,
                 5,5,5,5,5,5,5,5,5,5,5,5,5,5,4,4,
                 4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,
                 4,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,
                 3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]

    def __new__(cls, spi, ram, fref):
        if cls.__instance is None:
            cls.__instance = super(Synth, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi, ram, fref=None, indent=2):
        if self.__initialized:
            return
        self.__initialized = True
        self._indent   = indent
        self.spi       = spi
        self.ram       = ram
        self.amux      = amux.Amux(spi)
        self.chip_info = chip_info.Chip_info(spi)
        self.ref_clk   = ref_clk.Ref_clk(spi, fref)
        self.adc       = synth_adc.Synth_adc(spi, fref)
        self.sd        = sd.Sd(spi)
        self.loaded_beambook_id = None

    @evk_logger.log_call
    def setup(self, devs, pll_divn_divby2_en=None, sd_cfg={'sd_order':2}):
        self.adc.init_clks(devs, pll_divn_divby2_en)
        if self.chip_info.get(devs)['band'] == 28:
            self.spi.wr(devs,'sm_dac',round(self.vco_amp_28/self.sm_dac_ref*255))
        elif self.chip_info.get(devs)['band'] == 39:
            self.spi.wr(devs,'sm_dac',round(self.vco_amp_39/self.sm_dac_ref*255))
        self.sd.cfg_wr(devs, sd_cfg)
        

    @evk_logger.log_call
    def status(self, devs):
        prior_status   = self.spi.rd(devs, 'sm_config_status')
        current_status = self.spi.rd(devs, 'sm_config_status')
        vco_digtune    = self.spi.rd(devs, 'vco_digtune_read')
        vco_ibias      = self.spi.rd(devs, 'vco_ibias_read')
        frac_mode      = self.spi.rd(devs, 'sd_config') & 1
        N              = self.spi.rd(devs, 'sd_n')
        chp_setting    = self.spi.rd(devs, 'pll_config')
        if frac_mode:
            k          = self.spi.rd(devs, 'sd_k')
        else:
            k          = 0
        fref           = self.ref_clk.get(devs)
        freq           = self.sd.calc_rf_freq(devs,N,k,fref)
        status         = {'current_status':current_status,
                          'prior_status':prior_status,
                          'vco_digtune':vco_digtune,
                          'vco_ibias':vco_ibias,
                          'frac_mode':frac_mode,
                          'freq':freq,
                          'chp_setting':chp_setting}
        return status

    def status_print(self, status, indent=None):
        if indent is None:
            indent = self._indent
        evk_logger.evk_logger.log_info("prior lock status:   {}".format(fhex(status['prior_status'], 2)),indent)
        evk_logger.evk_logger.log_info("current lock status: {}".format(fhex(status['current_status'], 2)),indent)
        evk_logger.evk_logger.log_info("vco_digtune:         {}".format(fhex(status['vco_digtune'], 2)),indent)
        evk_logger.evk_logger.log_info("vco_ibias:           {}".format(fhex(status['vco_ibias'], 2)),indent)
        evk_logger.evk_logger.log_info("frac_mode:           {}".format(status['frac_mode']),indent)
        evk_logger.evk_logger.log_info("frequency:           {} Hz".format(status['freq']),indent)
        evk_logger.evk_logger.log_info("chp_setting:         {}".format(status['chp_setting']),indent)
        if 'retry_count' in status:
            evk_logger.evk_logger.log_info("retry count:         {}".format(status['retry_count']),indent)


    def load_best_beambook(self, dev, freq):
        beambook_list = self.ram.rf.find_tables_by_type('RAM')
        min_freq_diff = 0xffffffffffff
        best_beambook = None
        for beambook in beambook_list:
            beambook_freq = int(self.ram.rf.table_tag_info(beambook, 'FREQ'))
            if abs(beambook_freq - freq) < min_freq_diff:
                min_freq_diff = abs(beambook_freq - freq)
                best_beambook = beambook
        if self.loaded_beambook_id != best_beambook:
            self.ram.fill(dev, best_beambook)
            self.loaded_beambook_id = best_beambook
            evk_logger.evk_logger.log_info("beambook {} loaded.".format(best_beambook))

    @evk_logger.log_call
    def set(self, dev, freq, frac_mode=None, sd_order=None, retry_count=10, chp=None, printit=False):
        self.load_best_beambook(dev, freq)
        fref = self.ref_clk.get(dev)
        (N, k) = self.sd.calc_N_k(dev, freq, fref)
        return self._sm_run(dev, fref=fref, N=N, k=k, frac_mode=frac_mode, sd_order=sd_order, retry_count=retry_count, chp=chp, printit=printit)


    @evk_logger.log_call
    def _sm_run(self, devs, fref, N, k=0, frac_mode=None, sd_order=None, retry_count=10, chp=None, printit=False):
        if frac_mode == None:
            frac_mode = (self.spi.rd(devs, 'sd_config') & 1)
        if printit:
            evk_logger.evk_logger.log_info("Earlier status:",self._indent)
            status = self.status(devs)
            self.status_print(status,self._indent+2)
            evk_logger.evk_logger.log_info("Trigger PLL SM",self._indent)
        if (frac_mode == 0) | (frac_mode == False):
            self.sd.cfg_wr(devs, cfg = {'sd_rst_n':0})
            set_freq = self.sd.calc_rf_freq(devs,N,0,fref)
            if printit:
                evk_logger.evk_logger.log_info("Integer mode: N={:} (used), k={:} (ignored)".format(N, k),self._indent)
                evk_logger.evk_logger.log_info("RF frequency: {:<7.9} GHz".format(set_freq/1.0e9),self._indent)
        else:
            if sd_order == None:
                sd_order = ((self.spi.rd(devs, 'sd_config') >> 2) & 3)
            self.sd.cfg_wr(devs, cfg = {'sd_rst_n':1, 'sd_order':sd_order})
            set_freq = self.sd.calc_rf_freq(devs,N,k,fref)
            if printit:
                evk_logger.evk_logger.log_info("Fractional mode: N={:} (used), k={:} (used)".format(N, k),self._indent)
                evk_logger.evk_logger.log_info("RF frequency: {:<7.9} GHz".format(set_freq/1.0e9),self._indent)

        self.spi.wrrd(devs, 'sd_n', N)
        self.spi.wrrd(devs, 'sd_k', k)
        self.spi.wrrd(devs, 'sm_sd_fsm_ctrl', 0x0A)
        time.sleep(0.1)
        self.spi.wrrd(devs, 'sm_sd_fsm_ctrl', 0x05)
        time.sleep(0.05)
        status = self.status(devs)
        
        retry_count_orig = retry_count
        # Lock failed and retry_count > 0
        while (((status['current_status'] & 0xA3) != 0x23) & (retry_count > 0)):
            self.spi.wrrd(devs, 'sm_sd_fsm_ctrl', 0x0A)
            time.sleep(0.1)
            self.spi.wrrd(devs, 'sm_sd_fsm_ctrl', 0x05)
            time.sleep(0.05)
            status = self.status(devs)
            retry_count -= 1
            if chp is not None:
                self.spi.wr(devs, 'pll_config', chp)
        status['retry_count'] = retry_count_orig - retry_count
        
        if printit:
            evk_logger.evk_logger.log_info("Current status:",self._indent)
            self.status_print(status,self._indent+2)

        digtune = self.spi.rd(devs, 'vco_digtune_read')
        if self.chip_info.get(devs)['band'] == 28:
            chp_setting = self.chp_28[digtune]
        elif self.chip_info.get(devs)['band'] == 39:
            chp_setting = self.chp_39[digtune]
        else:
            chp_setting = 7
        status['chp_setting'] = chp_setting
        self.spi.wr(devs, 'pll_config', chp_setting)
        return status


    @evk_logger.log_call
    def calc_ref_offs(self, devs, rf_offs, freq):
        if self.chip_info.get(devs,False)['band'] == 28:
            div   = 3.0
        elif self.chip_info.get(devs,False)['band'] == 39:
            div   = 6.0
        else:
            div   = 3.0
        fref = self.ref_clk.get(devs)
        (N, k) = self.sd.calc_N_k(devs, freq, fref)
        return rf_offs/div/(N+k/self.sd.sd_length)

