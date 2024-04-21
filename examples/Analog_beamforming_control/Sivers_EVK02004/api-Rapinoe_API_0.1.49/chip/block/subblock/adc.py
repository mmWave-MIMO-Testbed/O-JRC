import copy
import adc_dac
import amux
import evk_logger
import matplotlib.pyplot as plt
from common import *


class Adc():


    __instance    = None

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Adc, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        self.spi          = spi
        self.dac          = adc_dac.Adc_dac(spi)
        self.amux         = amux.Amux(spi)
        self.evk_logger   = evk_logger.EvkLogger()
        self._conv_raw    = {'conv':'raw', 'print':True, 'nobits':11, 'volt':1, 'precision':0}
        self._conv_2comp  = {'conv':'twoscomp', 'print':True, 'nobits':11, 'volt':1, 'precision':0}
        self._conv_dec    = {'conv':'dec',   'print':True, 'nobits':11, 'volt':1, 'precision':0}
        self._conv_volt   = {'conv':'volt',  'print':True, 'nobits':11, 'volt':1.2, 'precision':5}
        self.conv_cur     = {}
        self._set_conv(self.conv_cur, 'volt')


    def _read_adc_data(self, devs, reps=10):
        ret = []
        return_int = False
        if not isinstance(devs,list):
            devs = [devs]
            return_int = True
        for dev in devs:
            adc_data = []
            adc_sum  = 0
            for rd in range(0,reps):
                adc_data.append(self.spi.rd(dev,'adc_data_0'))
            adc_sum = sum(twoscomp2dec(adc_data,11))
            adc_diff = [abs(twoscomp2dec(x,11) - adc_sum/reps) for x in adc_data]
            ret.append(adc_data[adc_diff.index(min(adc_diff))])
        if return_int:
            return ret[0]
        else:
            return ret


    def _set_conv(self, old_conv, new_conv):
        if isinstance(new_conv,str):
            if new_conv.lower() == 'volt':
                new_conv = self._conv_volt
            elif new_conv.lower() == 'dec':
                new_conv = self._conv_dec
            elif new_conv.lower() == 'twoscomp':
                new_conv = self._conv_2comp
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
            elif conv_to_copy.lower() == 'dec':
                conv_to_copy = self._conv_dec
            elif conv_to_copy.lower() == 'twoscomp':
                conv_to_copy = self._conv_2comp
            else:
                conv_to_copy = self._conv_raw
        return copy.deepcopy(conv_to_copy)
        
    @evk_logger.log_call
    def get_conv_cur(self, devs):
        return self._get_conv(self.conv_cur)




    @evk_logger.log_call
    def reset(self, devs):
        self.spi.clr(devs, 'adc_enable', 3)
        self.spi.clr(devs, 'adc_ctrl', 1)

    @evk_logger.log_call
    def enable(self, devs):
        self.spi.set(devs, 'adc_enable', 3)
        self.spi.set(devs, 'adc_ctrl', 1)
        
    @evk_logger.log_call
    def disable(self, devs):
        self.spi.clr(devs, 'adc_enable', 1)
        self.spi.clr(devs, 'adc_ctrl', 1)



    @evk_logger.log_call
    def get_data(self, devs, amux, amux8=None, synth=None, biastop=None, conv={}, reps=10):
        set_conv = self.get_conv_cur(devs)
        if isinstance(amux,str) and (amux8 is not None):
            self._set_conv(set_conv, amux8)
        else:
            self._set_conv(set_conv, conv)

        offs       = []
        adc_data   = []
        return_int = False
        if not isinstance(devs, list):
            devs = [devs]
            return_int = True
        if isinstance(synth,int):
            synth = synth | 0x10
        if isinstance(biastop,int):
            biastop = biastop | 0x10
        for i,dev in enumerate(devs):
            offs.append(0)
        
        if isinstance(amux,str):
            get_offs = self.amux.src_get_cfg(amux)['offs']
        else:
            get_offs = self.amux.src_get_cfg(self.amux.src_get_name(amux,amux8,synth,biastop))['offs']
        if get_offs:
            self.amux.set(devs, 'GND')
            offs = self._read_adc_data(devs, reps)

        resp = self.amux.set(devs, amux, amux8, synth, biastop)
        for i,dev in enumerate(devs):
            if resp[i] != 'No source':
                data = self._read_adc_data(dev, reps)
                if set_conv['conv'] == 'volt':
                    data2append = (twoscomp2volt(data,set_conv['nobits'],set_conv['volt'])-twoscomp2volt(offs[i],set_conv['nobits'],set_conv['volt']))*resp[i]['mult']
                elif set_conv['conv'] == 'dec':
                    data2append = twoscomp2dec(data-offs[i],set_conv['nobits'])*resp[i]['mult']
                elif set_conv['conv'] == 'twoscomp':
                    data2append = dec2twoscomp(data-offs[i],set_conv['nobits'])*resp[i]['mult']
                else:
                    data2append = data
                adc_data.append(data2append)

        if return_int:
            return round(adc_data[0],set_conv['precision'])
        else:
            return [round(item,set_conv['precision']) for item in adc_data]

    def get(self, devs, amux, amux8=None, synth=None, biastop=None, conv={}):
        return self.get_data(devs, amux, amux8, synth, biastop, conv)


    @evk_logger.log_call
    def dump(self, devs, amux=[0,6], amux8=[0,8], synth=[0,8], biastop=[0,16], conv={}):
        set_conv = self.get_conv_cur(devs)
        self._set_conv(set_conv, conv)
        prec = set_conv['precision']
        deci = 9+prec-3
        amux_ctrl_src    = self.spi.rd(devs, 'amux_ctrl_src')
        synth_misc       = self.spi.rd(devs, 'synth_misc')
        biastop_config   = self.spi.rd(devs, 'biastop_config')
        amux_src_text    = ["BIST SENSE", "BIST BF DET", "BB V", "BB H",
                            "COM", "SYNTH/BIASTOP"]
        amux8_src_text   = [["ADC DAC", "Test Amux", "VCM Sense", "VCC2V5 Sense",
                             "PTAT Sense", "VDD1V2 Sense", "BG Sense", "VTUNE Sense"],
                            ["BF DET V W", "BF DET H W", "BF DET V E", "BF DET H E",
                             "COM RX DET V", "COM RX DET H", "COM RX DAC V", "COM RX DAC H"],
                            ["RX I PGA1 DET", "RX I FILT DET", "RX Q PGA1 DET", "RX Q FILT DET",
                             "RX I PGA1 DC", "RX Q PGA1 DC", "RX I PGA2 DC", "RX Q PGA2 DC"],
                            ["RX I PGA1 DET", "RX I FILT DET", "RX Q PGA1 DET", "RX Q FILT DET",
                             "RX I PGA1 DC", "RX Q PGA1 DC", "RX I PGA2 DC", "RX Q PGA2 DC"],
                            ["TX DET H 0", "TX DET H 1", "TX DET H 2", "TX DET H 3",
                             "TX DET V 0", "TX DET V 1", "TX DET V 2", "TX DET V 3"],
                            ["AMUX_P/_N [5]", "AMUX_P/_N [5]", "AMUX_P/_N [5]", "AMUX_P/_N [5]",
                             "AMUX_P/_N [5]", "AMUX_P/_N [5]", "AMUX_P/_N [5]", "AMUX_P/_N [5]"]
                           ]
        synth_src_text   = ["VTUNE_SET", "VCO_AMP", "VTUNE_REF", "BIASTOP",
                            "DAC_P", "DAC_N", "GND", "DAC_N"]
        biastop_src_text = ["VDD_1V2", "VCC_RF", "VCC_BB_V", "VCC_BB_H",
                            "LDO_2V7_BB_V", "LDO_2V7_BB_H", "LDO_2V7_VCO", "LDO_2V7_CHP",
                            "LDO_2V7_PLL", "EXT_LO_DET", "BG_1V1", "VCC_SYNTH",
                            "VCC_PA_W", "VCC_PA_E", "BG_1V1_W", "BG_1V1_E"]
        print('')
        print ('{:^21}'.format('Device'),end='')
        if not isinstance(devs, list):
            devs = [devs]
        for dev in devs:
            print ('|{:^{}}'.format(str(dev.chip_num)+' (V)',deci),end='')
        print('')
        print ('{:^21}'.format(21*'-'),end='')
        for i,dev in enumerate(devs):
            print ('|{:^{}}'.format(deci*'-',deci),end='')
        print('')
        for amux_ in range(amux[0], amux[1]):
            print("{:2} {:18}".format(amux_, amux_src_text[amux_]),end='')
            for dev in devs:
                print ('|{:^{}}'.format(deci*' ',deci),end='')
            print('')
            if (amux_ == 5):
                amux8_ = amux8[0]
                for synth_ in range(synth[0], synth[1]):
                    if (synth_ != 3):
                        print("  {:2} {:16}".format(synth_, synth_src_text[synth_]),end='')
                        adc_data = self.get_data(devs, amux_, amux8_, synth_|0x10, None, conv)
                        for i,adc_data_ in enumerate(adc_data):
                            print("| {:>{}.{}f}  ".format(round(adc_data_,prec),3+prec,prec),end='')
                        print('')
                    else:
                        print("  {:2} {:16}".format(synth_, synth_src_text[synth_]),end='')
                        for dev in devs:
                            print ('|{:^{}}'.format(deci*' ',deci),end='')
                        print('')
                        for biastop_ in range(biastop[0], biastop[1]):
                            print("     {:2} {:13}".format(biastop_, biastop_src_text[biastop_]),end='')
                            adc_data = self.get_data(devs, amux_, amux8_, synth_|0x10, biastop_|0x10, conv)
                            for i,adc_data_ in enumerate(adc_data):
                                print("| {:>{}.{}f}  ".format(round(adc_data_,prec),3+prec,prec),end='')
                            print('')
            else:
                for amux8_ in range(amux8[0], amux8[1]):
                    print("  {:2} {:16}".format(amux8_, amux8_src_text[amux_][amux8_]),end='')
                    adc_data = self.get_data(devs, amux_, amux8_, None, None, conv)
                    for i,adc_data_ in enumerate(adc_data):
                        print("| {:>{}.{}f}  ".format(round(adc_data_,prec),3+prec,prec),end='')
                    print('')
        self.spi.wr(devs, 'amux_ctrl_src', amux_ctrl_src)
        self.spi.wr(devs, 'biastop_config', biastop_config)
        self.spi.wr(devs, 'synth_misc', synth_misc)



    @evk_logger.log_call
    def swp_dac(self, devs, start, stop, conv={}):
        x = [i for i in range(start, stop)]
        y = []
        for x_ in x:
            self.dac.set(devs, x_)
            y.append(self.get_data(devs,'ADC DAC',conv)) 
        return x,y

    @evk_logger.log_call
    def swp_vco_amp(self, devs, start, stop, conv={}):
        ibias = self.spi.rd(devs,'vco_ibias')
        ovr = self.spi.wr(devs,'vco_digtune_ibias_override',1)
        x = [i for i in range(start, stop)]
        y = []
        for x_ in x:
            self.spi.wr(devs,'vco_ibias',x_)
            y.append(self.get_data(devs,'VCO_AMP',conv))
        self.spi.wr(devs,'vco_ibias',ibias)
        self.spi.wr(devs,'vco_digtune_ibias_override',ovr)
        return x,y

    def swp_plot(self, x, y):
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.grid()
        plt.show()
