import numpy as np
import evk_logger
import subblock.r5.amux as amux
import chip_info
import subblock.ref_clk as ref_clk
import subblock.r5.sd as sd
import synth_adc
import subblock.r5.temp as temp
from common import *
import time

class Synth():

    __instance = None
    sm_dac_ref = 1.25
    vco_amp_28 = 0.65
    vco_amp_39 = 1.1
    chp_28    = [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,
                 7,7,7,7,7,6,6,6,6,6,6,6,5,5,5,5,
                 5,5,5,4,4,4,4,4,4,4,4,3,3,3,3,3,
                 3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,
                 6,6,6,6,6,6,6,6,6,6,6,6,6,5,5,5,
                 5,5,5,5,5,5,5,4,4,4,4,4,4,4,4,4,
                 3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,
                 2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1]                 
                 
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
        self.temp      = temp.Temp(spi)
        self.loaded_beambook_id = None

    @evk_logger.log_call
    def _fill_pll_i_chp_tbl(self, devs, chp_tbl):
        result = []
        count = 1
        for i in range(1, len(chp_tbl)):
            if chp_tbl[i] == chp_tbl[i-1]:
                count += 1
            else:
                result.append((chp_tbl[i-1], count))
                count = 1

        result.append((chp_tbl[-1], count))
        start_addr = self.spi._addr('pll_i_chp_tbl_0')
        reg_size = self.spi._size('pll_i_chp_tbl_0')
        pll_i_chp_tbl_stop = []
        for i in range(len(result)):
            if i == 0:
                pll_i_chp_tbl_stop.append(result[i][1]-1)
                pll_i_chp_tbl = (pll_i_chp_tbl_stop[len(pll_i_chp_tbl_stop)-1]<<8) + result[i][0]
            else:
                pll_i_chp_tbl_stop.append(result[i][1]+pll_i_chp_tbl_stop[len(pll_i_chp_tbl_stop)-1])
                pll_i_chp_tbl = (pll_i_chp_tbl_stop[len(pll_i_chp_tbl_stop)-1]<<8) + result[i][0]
            self.spi.wr(devs, start_addr + i*2, pll_i_chp_tbl, reg_size)

    @evk_logger.log_call
    def setup(self, devs, pll_divn_divby2_en=None, sd_cfg={'sd_order':3}):
        self.adc.init_clks(devs, pll_divn_divby2_en)
        if isinstance(sd_cfg, dict):
            try:
                sd_order = sd_cfg['sd_order']
            except:
                sd_order = 3
        else:
            sd_order = (sd_cfg&0x0c)>>2

        if self.chip_info.get(devs)['band'] == 28:
            self._fill_pll_i_chp_tbl(devs, self.chp_28)
            self.spi.wr(devs,'sm_dac',round(self.vco_amp_28/self.sm_dac_ref*255))
        elif self.chip_info.get(devs)['band'] == 39:
            self._fill_pll_i_chp_tbl(devs, self.chp_39)
            self.spi.wr(devs,'sm_dac',round(self.vco_amp_39/self.sm_dac_ref*255))
        self.sd.cfg_wr(devs, sd_cfg)
        if sd_order == 3:
            self.spi.wr(devs, 'pll_phase_adj', 0xff)
            self.spi.wr(devs, 'pll_en', {'pll_spi_leak_en':1})
        else:
            self.spi.wr(devs, 'pll_phase_adj', 0x00)
            self.spi.wr(devs, 'pll_en', {'pll_spi_leak_en':0})

        # Prepare for temperature reading
        self.spi.set(devs, 'bist_config', 0x80)
        self.spi.set(devs, 'biastop_en', 0x20)
        self.spi.set(devs, 'adc_enable', 3)
        self.spi.set(devs, 'adc_ctrl', 1)

    @evk_logger.log_call
    def status(self, devs, printit=False):
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
        if printit:
            self.status_print(status,self._indent+2)
        else:
            return status

    def ld_status(self, devs, reps=1, sleep=0, printit=False):
        if (reps>1):
            printit = True
        for rep in range(reps):
            status = self.spi.rd(devs, 'sm_config_status')
            if printit:
                evk_logger.evk_logger.log_info(fhex(status,2))
                if (sleep>0):
                    time.sleep(sleep)
        if not printit:
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
    def set(self, dev, freq, frac_mode=None, sd_order=None, retry_count=10, chp=None, printit=True, load_beambook=True):
        temperatute = self.temp.get(dev)
        if temperatute < 0:
            self.spi.wr(dev, 'sm_vtune_cal', 0x3f)
        else:
            self.spi.wr(dev, 'sm_vtune_cal', 0x17)
        if load_beambook:
            self.load_best_beambook(dev, freq)
        fref = self.ref_clk.get(dev)
        (N, k) = self.sd.calc_N_k(dev, freq, fref)
        res = self._sm_run(dev, fref=fref, N=N, k=k, frac_mode=frac_mode, sd_order=sd_order, retry_count=retry_count, chp=chp, printit=printit)
        if sd_order == 3:
            pll_i_leak = self.spi.rd(dev, 'pll_i_chp_read') + 2
            self.spi.wr(dev, 'pll_config', {'pll_i_leak':pll_i_leak})
        else:
            self.spi.wr(dev, 'pll_config', {'pll_i_leak':0})
        return res


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
            if (k>(self.sd.sd_length/2)):
                N=N+1
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
        while (((status['current_status'] & 0x87) != 0x07) & (retry_count > 0)):
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

        #if ((self.spi.rd(devs, 'sm_en') & 0x80) == 0x00):
        digtune = self.spi.rd(devs, 'vco_digtune_read')
        if self.chip_info.get(devs)['band'] == 28:
            chp_setting = self.chp_28[digtune]
        elif self.chip_info.get(devs)['band'] == 39:
            chp_setting = self.chp_39[digtune]
        else:
            chp_setting = 7
        self.spi.wr(devs, 'pll_config', chp_setting)
        status['chp_setting'] = self.spi.rd(devs, 'pll_i_chp_read')
        return status
