import copy
import evk_logger
import amux
import ref_clk
from common import *


class Synth_adc():

    __instance  = None
    clk_targets = {'sm_adc_clk'     : 10e6,
                   'sm_dac_cal_clk' : 2e6,
                   'sm_digtune_clk' : 50e3,
                   'sm_ibias_clk'   : 10e6
                  }

    def __new__(cls, spi, fref):
        if cls.__instance is None:
            cls.__instance = super(Synth_adc, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi, fref=None):
        self.spi        = spi
        self.amux       = amux.Amux(spi)
        self.ref_clk    = ref_clk.Ref_clk(spi, fref)
        self._conv_raw  = {'conv':'raw', 'print':True, 'nobits':8, 'volt':1, 'precision':None}
        self._conv_volt = {'conv':'volt',  'print':True, 'nobits':8, 'volt':1.2, 'precision':5}
        self.conv_cur   = {}
        self._set_conv(self.conv_cur, 'volt')



    def _set_conv(self, old_conv, new_conv):
        if isinstance(new_conv,str):
            if new_conv.lower() == 'volt':
                new_conv = self._conv_volt
            else:
                new_conv = self._conv_raw
        for key,val in new_conv.items():
            old_conv[key] = val

    @evk_logger.log_call
    def set_conv_cur(self, devs, conv):
        self._set_conv(self.conv_cur, conv)

    def _get_conv(self, conv_to_copy):
        if isinstance(conv_to_copy,str):
            if conv_to_copy.lower() == 'volt':
                conv_to_copy = self._conv_volt
            else:
                conv_to_copy = self._conv_raw
        return copy.deepcopy(conv_to_copy)
        
    @evk_logger.log_call
    def get_conv_cur(self, devs):
        return self._get_conv(self.conv_cur)


    @evk_logger.log_call
    def init_clks(self, devs, pll_divn_divby2_en=None):
        fref = self.ref_clk.get(devs)
        if pll_divn_divby2_en == None:
            pll_divn_divby2_en = (self.spi.rd(devs,'pll_en')>>2)&1
        else:
            self.spi.wr(devs,'pll_en',{'pll_divn_divby2_en':pll_divn_divby2_en})
        sm_adc_clk     = round(fref/(self.clk_targets['sm_adc_clk']*(1+pll_divn_divby2_en)))
        sm_dac_cal_clk = round(fref/(self.clk_targets['sm_dac_cal_clk']*(1+pll_divn_divby2_en)))
        sm_digtune_clk = round(fref/(self.clk_targets['sm_digtune_clk']*(1+pll_divn_divby2_en)))
        sm_ibias_clk   = round(fref/(self.clk_targets['sm_ibias_clk']*(1+pll_divn_divby2_en)))
        
        if (sm_adc_clk < 1):
            sm_adc_clk = 1
        if (sm_adc_clk > 31):
            sm_adc_clk = 31

        if (sm_dac_cal_clk < 8):
            sm_dac_cal_clk = 8
        if (sm_dac_cal_clk > 127):
            sm_dac_cal_clk = 127

        if (sm_digtune_clk < 2):
            sm_digtune_clk = 2
        if (sm_digtune_clk > 511):
            sm_digtune_clk = 511

        if (sm_ibias_clk < 1):
            sm_ibias_clk = 1
        if (sm_ibias_clk > 255):
            sm_ibias_clk = 255

        sm_clk_config  = (sm_adc_clk << 32) + (sm_dac_cal_clk << 24) + (sm_digtune_clk << 8) + sm_ibias_clk
        values = self.spi.wrrd(devs, 'sm_clk_config', sm_clk_config)
        return values


    @evk_logger.log_call
    def enable(self, devs):
        self.spi.wr(devs, 'pll_en', 0x13)
        self.spi.wr(devs, 'sm_en', 0x01)
        self.spi.wr(devs, 'sm_adc_control', 0x03)


    @evk_logger.log_call
    def disable(self, devs):
        self.spi.wr(devs, 'pll_en', 0x00)
        self.spi.wr(devs, 'sm_en', 0x00)
        self.spi.wr(devs, 'sm_adc_control', 0x00)


    @evk_logger.log_call
    def get_data(self, devs, synth, biastop=None, conv={}):
        set_conv = self.get_conv_cur(devs)
        if isinstance(synth,str) and (biastop is not None):
            self._set_conv(set_conv, biastop)
        else:
            self._set_conv(set_conv, conv)

        adc_data   = []
        return_int = False
        if not isinstance(devs, list):
            devs = [devs]
            return_int = True
        if isinstance(synth,int):
            synth = synth | 0x10
        if isinstance(biastop,int):
            biastop = biastop | 0x10
        
        if isinstance(synth, str):
            resp = self.amux.set(devs, synth)
        else:
            resp = self.amux.set(devs, 5, 0, synth, biastop)

        for i,dev in enumerate(devs):
            if resp[i] != 'No source':
                data = self.spi.rd(dev, 'sm_adc_neg')
                if set_conv['conv'] == 'volt':
                    data2append = twoscomp2volt(data,set_conv['nobits']+1,set_conv['volt'])*resp[i]['mult']
                else:
                    data2append = data
                adc_data.append(data2append)

        if return_int:
            return round(adc_data[0],set_conv['precision'])
        else:
            return [round(item,set_conv['precision']) for item in adc_data]

    def get(self, devs, synth, biastop=None, conv={}):
        return self.get_data(devs, synth, biastop, conv)


    @evk_logger.log_call
    def dump(self, devs, synth=[0,8], biastop=[0,16]):
        amux_ctrl_src    = self.spi.rd(devs, 'amux_ctrl_src')
        synth_misc       = self.spi.rd(devs, 'synth_misc')
        biastop_config   = self.spi.rd(devs, 'biastop_config')
        synt_src_mult    = [3, 3, 3, 1,
                            1, 1, 1, 1]
        synth_src_text   = ["VTUNE_SET", "VCO_AMP", "VTUNE_REF", "BIASTOP",
                            "DAC_P", "DAC_N", "GND", "DAC_N"]
        biastop_src_mult = [3, 4.5, 4.5, 4.5,
                            3, 3, 3, 3,
                            3, 3, 3, 4.5,
                            4.5, 4.5, 3, 3]
        biastop_src_text = ["VDD_1V2", "VCC_RF", "VCC_BB_V", "VCC_BB_H",
                            "LDO_2V7_BB_V", "LDO_2V7_BB_H", "LDO_2V7_VCO", "LDO_2V7_CHP",
                            "LDO_2V7_PLL", "EXT_LO_DET", "BG_1V1", "VCC_SYNTH",
                            "VCC_PA_W", "VCC_PA_E", "BG_1V1_W", "BG_1V1_E"]
        print('')
        print ('{:^21}'.format('Device'),end='')
        if not isinstance(devs, list):
            devs = [devs]
        for dev in devs:
            print ('|{:^9}'.format(str(dev.chip_num)+' (V)'),end='')
        print('')
        print ('{:^21}'.format(21*'-'),end='')
        for dev in devs:
            print ('|{:^9}'.format(9*'-'),end='')
        print('')
        for synth_src in range(synth[0], synth[1]):
            if (synth_src != 3):
                print("  {:2} {:16}".format(synth_src, synth_src_text[synth_src]),end='')
                self.amux.set(devs, 5, 0, synth_src+0x10)
                sm_adcs = self.spi.rd(devs, 'sm_adc_neg')
                for sm_adc in sm_adcs:
                    print("| {:>6.3f}  ".format(
                        round((sm_adc & 0xFF)*synt_src_mult[synth_src]*1.2/256, 3)),end='')
                print('')
            else:
                print("  {:2} {:16}".format(synth_src, synth_src_text[synth_src]),end='')
                for dev in devs:
                    print ('|{:^9}'.format(9*' '),end='')
                print('')
                for biastop_src in range(biastop[0], biastop[1]):
                    print("     {:2} {:13}".format(biastop_src, biastop_src_text[biastop_src]),end='')
                    self.amux.set(devs, 5, 0, synth_src+0x10, biastop_src+0x10)
                    sm_adcs = self.spi.rd(devs, 'sm_adc_neg', 2)
                    for sm_adc in sm_adcs:
                        print("| {: >6.3f}  ".format(
                            round((sm_adc & 0xFF)*synt_src_mult[synth_src]*biastop_src_mult[biastop_src]*1.2/256, 3)),end='')
                    print('')
        self.spi.wr(devs, 'amux_ctrl_src', amux_ctrl_src)
        self.spi.wr(devs, 'biastop_config', biastop_config)
        self.spi.wr(devs, 'synth_misc', synth_misc)
