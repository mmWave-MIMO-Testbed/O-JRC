from common import *
import evk_logger
import chip_info

class Amux():

    __instance    = None
    _pin_out_on       = 0x018
    _pin_out_off      = ~0x018
    _pin_in_on        = 0x006
    _pin_in_off       = ~0x006
    _pin_all_off      = _pin_out_off & _pin_in_off
    
    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Amux, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        self._spi       = spi
        self.evk_logger = evk_logger.EvkLogger()
        self._chip_info = chip_info.Chip_info(self._spi)
        self.src = {'ADC DAC':              {'amux':0, 'amux8':0, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'Test Amux':            {'amux':0, 'amux8':1, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'VCM Sense':            {'amux':0, 'amux8':2, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'VCC2V5 Sense':         {'amux':0, 'amux8':3, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'PTAT Sense':           {'amux':0, 'amux8':4, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'VDD1V2 Sense':         {'amux':0, 'amux8':5, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'BG Sense':             {'amux':0, 'amux8':6, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'VTUNE Sense':          {'amux':0, 'amux8':7, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'BF DET V W':           {'amux':1, 'amux8':0, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'BF DET H W':           {'amux':1, 'amux8':1, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'BF DET V E':           {'amux':1, 'amux8':2, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'BF DET H E':           {'amux':1, 'amux8':3, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'COM RX DET V':         {'amux':1, 'amux8':4, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'COM RX DET H':         {'amux':1, 'amux8':5, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'COM RX DAC V':         {'amux':1, 'amux8':6, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'COM RX DAC H':         {'amux':1, 'amux8':7, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'BB V RX I PGA1 DET':   {'amux':2, 'amux8':0, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'BB V RX I FILT DET':   {'amux':2, 'amux8':1, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'BB V RX Q PGA1 DET':   {'amux':2, 'amux8':2, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'BB V RX Q FILT DET':   {'amux':2, 'amux8':3, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'BB V RX I PGA1 DC':    {'amux':2, 'amux8':4, 'synth':None, 'biastop':None, 'mult':2.0, 'offs':False},
                    'BB V RX Q PGA1 DC':    {'amux':2, 'amux8':5, 'synth':None, 'biastop':None, 'mult':2.0, 'offs':False}, 
                    'BB V RX I PGA2 DC':    {'amux':2, 'amux8':6, 'synth':None, 'biastop':None, 'mult':2.0, 'offs':False},
                    'BB V RX Q PGA2 DC':    {'amux':2, 'amux8':7, 'synth':None, 'biastop':None, 'mult':2.0, 'offs':False},
                    'BB H RX I PGA1 DET':   {'amux':3, 'amux8':0, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'BB H RX I FILT DET':   {'amux':3, 'amux8':1, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'BB H RX Q PGA1 DET':   {'amux':3, 'amux8':2, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'BB H RX Q FILT DET':   {'amux':3, 'amux8':3, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'BB H RX I PGA1 DC':    {'amux':3, 'amux8':4, 'synth':None, 'biastop':None, 'mult':2.0, 'offs':False},
                    'BB H RX Q PGA1 DC':    {'amux':3, 'amux8':5, 'synth':None, 'biastop':None, 'mult':2.0, 'offs':False}, 
                    'BB H RX I PGA2 DC':    {'amux':3, 'amux8':6, 'synth':None, 'biastop':None, 'mult':2.0, 'offs':False},
                    'BB H RX Q PGA2 DC':    {'amux':3, 'amux8':7, 'synth':None, 'biastop':None, 'mult':2.0, 'offs':False},
                    'TX DET H 0':           {'amux':4, 'amux8':0, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'TX DET H 1':           {'amux':4, 'amux8':1, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'TX DET H 2':           {'amux':4, 'amux8':2, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'TX DET H 3':           {'amux':4, 'amux8':3, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'TX DET V 0':           {'amux':4, 'amux8':4, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'TX DET V 1':           {'amux':4, 'amux8':5, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False}, 
                    'TX DET V 2':           {'amux':4, 'amux8':6, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'TX DET V 3':           {'amux':4, 'amux8':7, 'synth':None, 'biastop':None, 'mult':1.0, 'offs':False},
                    'VTUNE_SET':            {'amux':5, 'amux8':0, 'synth':0x10|0, 'biastop':None, 'mult':3.0, 'offs':True},
                    'VCO_AMP':              {'amux':5, 'amux8':0, 'synth':0x10|1, 'biastop':None, 'mult':3.0, 'offs':True}, 
                    'VTUNE_REF':            {'amux':5, 'amux8':0, 'synth':0x10|2, 'biastop':None, 'mult':3.0, 'offs':True},
                    'DAC_P':                {'amux':5, 'amux8':0, 'synth':0x10|4, 'biastop':None, 'mult':3.0, 'offs':True}, 
                    'DAC_N':                {'amux':5, 'amux8':0, 'synth':0x10|5, 'biastop':None, 'mult':3.0, 'offs':True},
                    'GND':                  {'amux':5, 'amux8':0, 'synth':0x10|6, 'biastop':None, 'mult':3.0, 'offs':True}, 
                    'DAC_N2':               {'amux':5, 'amux8':0, 'synth':0x10|7, 'biastop':None, 'mult':3.0, 'offs':True},
                    'VDD_1V2':              {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|0, 'mult':3.0, 'offs':True}, 
                    'VCC_RF':               {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|1, 'mult':4.5, 'offs':True},
                    'VCC_BB_V':             {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|2, 'mult':4.5, 'offs':True}, 
                    'VCC_BB_H':             {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|3, 'mult':4.5, 'offs':True},
                    'LDO_2V7_BB_V':         {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|4, 'mult':3.0, 'offs':True}, 
                    'LDO_2V7_BB_H':         {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|5, 'mult':3.0, 'offs':True},
                    'LDO_2V7_VCO':          {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|6, 'mult':3.0, 'offs':True}, 
                    'LDO_2V7_CHP':          {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|7, 'mult':3.0, 'offs':True},
                    'LDO_2V7_PLL':          {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|8, 'mult':3.0, 'offs':True}, 
                    'EXT_LO_DET':           {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|9, 'mult':3.0, 'offs':True},
                    'BG_1V1':               {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|10, 'mult':3.0, 'offs':True}, 
                    'VCC_SYNTH':            {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|11, 'mult':4.5, 'offs':True},
                    'VCC_PA_W':             {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|12, 'mult':4.5, 'offs':True}, 
                    'VCC_PA_E':             {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|13, 'mult':4.5, 'offs':True},
                    'BG_1V1_W':             {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|14, 'mult':3.0, 'offs':True}, 
                    'BG_1V1_E':             {'amux':5, 'amux8':0, 'synth':0x10|3, 'biastop':0x10|15, 'mult':3.0, 'offs':True}
                   }
        self.src_inv = {str((v['amux'],v['amux8'],v['synth'],v['biastop'])): k for k,v in self.src.items()}
        self.src_names = list(self.src.keys())

    
    @evk_logger.log_call
    def set_ovr(self, devs, amux_ovr, amux8_ovr):
        if isinstance(devs, list):
            for i,dev in enumerate(devs):
                self._spi.wr(dev, 'amux_ctrl_override', (amux_ovr[i]<<4) + amux8_ovr[i])
        else:
            self._spi.wr(devs, 'amux_ctrl_override', (amux_ovr<<4) + amux8_ovr)


    @evk_logger.log_call
    def get_ovr(self, devs):
        ovr_regs = self._spi.rd(devs, 'amux_ctrl_override')
        if isinstance(ovr_regs, list):
            amux_ovr  = []
            amux8_ovr = []
            for i,ovr_reg in enumerate(ovr_regs):
                amux_ovr.append((ovr_reg>>4) & 0x7)
                amux8_ovr.append(ovr_reg & 0x7)
        else:
            amux_ovr  = (ovr_regs>>4) & 0x7
            amux8_ovr = ovr_regs & 0x7
        return (amux_ovr, amux8_ovr)



    def src_get_cfg(self, src_name):
        ret = 'No source'
        if isinstance(src_name, str):
            if src_name in self.src:
                ret = self.src[src_name]
        return ret

    def src_get_name(self, amux_src, amux8_src=None, synth_src=None, biastop_src=None):
        if isinstance(amux_src, dict):
            biastop_src = amux_src['biastop']
            synth_src   = amux_src['synth']
            amux8_src   = amux_src['amux8']
            amux_src    = amux_src['amux']
        elif isinstance(amux_src, tuple):
            biastop_src = amux_src[3]
            synth_src   = amux_src[2]
            amux8_src   = amux_src[1]
            amux_src    = amux_src[0]
        
        if amux8_src is None:
            amux8_src = 0
        if synth_src is None:
            synth_src = 0
        if biastop_src is None:
            biastop_src = 0

        if amux_src in range(0,5):
            ret = self.src_inv[str((amux_src,amux8_src,None,None))]
        elif (amux_src == 5):
            if (synth_src & 0x7) == 3:
                ret = self.src_inv[str((amux_src,0,synth_src|0x10,biastop_src|0x10))]
            else:
                ret = self.src_inv[str((amux_src,0,synth_src|0x10,None))]
        else:
            ret = 'No source'
        return ret
        


    @evk_logger.log_call
    def _set(self, dev, amux_src, amux8_src=None, synth_src=None, biastop_src=None):
        ret = {}
        if isinstance(amux_src, dict):
            ret            = self.src_get_cfg(self.src_get_name(amux_src['amux'], amux_src['amux8'], amux_src['synth'], amux_src['biastop']))
            if ret != 'No source':
                ret['amux']    = amux_src['amux']
                ret['amux8']   = amux_src['amux8']
                ret['synth']   = amux_src['synth']
                ret['biastop'] = amux_src['biastop']
        elif isinstance(amux_src, tuple):
            ret            = self.src_get_cfg(self.src_get_name(amux_src[0], amux_src[1], amux_src[2], amux_src[3]))
            if ret != 'No source':
                ret['amux']    = amux_src[0]
                ret['amux8']   = amux_src[1]
                ret['synth']   = amux_src[2]
                ret['biastop'] = amux_src[3]
        elif isinstance(amux_src, str):
            ret            = self.src_get_cfg(amux_src)
        else:
            ret            = self.src_get_cfg(self.src_get_name(amux_src, amux8_src, synth_src, biastop_src))
            if ret != 'No source':
                ret['amux']    = amux_src
                ret['amux8']   = amux8_src
                ret['synth']   = synth_src
                ret['biastop'] = biastop_src

        if ret != 'No source':
            if ret['amux8'] is None:
                ret['amux8'] = 0
            if ret['synth'] is None:
                ret['synth'] = 0
            if ret['biastop'] is None:
                ret['biastop'] = 0
            if 'SW' in self._chip_info.get(dev)['workaround']:
                self._spi.wr(dev, 'synth_misc', (0x17 & ret['synth']))
                self._spi.wr(dev, 'biastop_config', (0x1F & ret['biastop']))
                self._spi.wr(dev, 'amux_ctrl_src', ((7-ret['amux']) << 4) + ret['amux8'])
                self._spi.wr(dev, 'amux_ctrl', 0x11)
                self._spi.wr(dev, 'amux_ctrl', 0x31)
                self._spi.wr(dev, 'amux_ctrl', 0x11)
                self._spi.wr(dev, 'amux_ctrl_src', (ret['amux'] << 4) + (7-ret['amux8']))
                self._spi.wr(dev, 'amux_ctrl', 0x13)
                self._spi.wr(dev, 'amux_ctrl', 0x11)
                self._spi.wr(dev, 'amux_ctrl_src', (ret['amux'] << 4) + (ret['amux8']))
            else:
                self._spi.wr(dev, 'synth_misc', (0x17 & ret['synth']))
                self._spi.wr(dev, 'biastop_config', (0x1F & ret['biastop']))
                self._spi.wr(dev, 'amux_ctrl_src', (ret['amux'] << 4) + ret['amux8'])
                self._spi.wr(dev, 'amux_ctrl', 0x11)
                self._spi.wr(dev, 'amux_ctrl', 0x33)
                self._spi.wr(dev, 'amux_ctrl', 0x11)
        return ret


    @evk_logger.log_call
    def set(self, devs, amux_src, amux8_src=None, synth_src=None, biastop_src=None):
        if isinstance(devs, list):
            ret = []
            if isinstance(biastop_src, list):
                for i,dev in enumerate(devs):
                    ret.append(self._set(dev, amux_src[i], amux8_src[i], synth_src[i], biastop_src[i]))
            elif isinstance(synth_src, list):
                for i,dev in enumerate(devs):
                    ret.append(self._set(dev, amux_src[i], amux8_src[i], synth_src[i], biastop_src))
            elif isinstance(amux8_src, list):
                for i,dev in enumerate(devs):
                    ret.append(self._set(dev, amux_src[i], amux8_src[i], synth_src, biastop_src))
            elif isinstance(amux_src, list):
                for i,dev in enumerate(devs):
                    ret.append(self._set(dev, amux_src[i], amux8_src, synth_src, biastop_src))
            else:
                for i,dev in enumerate(devs):
                    ret.append(self._set(dev, amux_src, amux8_src, synth_src, biastop_src))
        else:
            ret = self._set(devs, amux_src, amux8_src, synth_src, biastop_src)
        return ret


    @evk_logger.log_call
    def _get(self, dev, frmt='name'):
        synth_src     = self._spi.rd(dev, 'synth_misc')
        biastop_src   = self._spi.rd(dev, 'biastop_config')
        amux_ctrl_src = self._spi.rd(dev, 'amux_ctrl_src')
        amux_src      = (amux_ctrl_src >> 4) & 0xF
        amux8_src     = amux_ctrl_src & 0xF
        ret = self.src_get_name(amux_src, amux8_src, synth_src, biastop_src)
        if frmt != 'name':
            ret = self.src_get_cfg(ret)
            ret['amux']    = amux_src
            ret['amux8']   = amux8_src
            ret['synth']   = synth_src
            ret['biastop'] = biastop_src
        return ret


    @evk_logger.log_call
    def get(self, devs, frmt='name'):
        if isinstance(devs, list):
            ret = []
            for dev in devs:
                ret.append(self._get(dev,frmt))        
        else:
            ret = self._get(devs,frmt)
        return ret
        
        
    @evk_logger.log_call
    def _port(self, dev, direction=None, printit=True):
        cur_val = self._spi.rd(dev, 'bist_config')
        if direction is None:
            in_out_val = cur_val & (self._pin_out_on | self._pin_in_on)
            resp = {
                0b00000 : 'off',
                0b00110 : 'in',
                0b11000 : 'out'
                }.get(in_out_val,"Amux pin mixed in/out setting in register 'bist_config': {:}".format(fhex(cur_val)))
        elif direction.lower() == 'out':
            resp    = direction.lower()
            new_val = (cur_val & self._pin_in_off) | self._pin_out_on
            self._spi.wr(dev, 'bist_config',new_val)
        elif direction.lower() == 'in':
            resp    = direction.lower()
            new_val = (cur_val & self._pin_out_off) | self._pin_in_on
            self._spi.wr(dev, 'bist_config',new_val)
        elif direction.lower() == 'off':
            resp    = direction.lower()
            new_val = cur_val & self._pin_all_off
            self._spi.wr(dev, 'bist_config',new_val)
        else:
            resp = "Amux pin setting option '{:}' invalid. Please use 'out', 'in', 'off' or None".format(direction)
        return resp
        
    @evk_logger.log_call
    def port(self, devs, direction=None, printit=True):
        if isinstance(devs, list):
            ret = []
            for i,dev in enumerate(devs):
                if isinstance(direction,list):
                    ret.append(self._port(dev, direction[i], printit))
                else:
                    ret.append(self._port(dev, direction, printit))        
        else:
            ret = self._port(devs, direction, printit)
        return ret

    @evk_logger.log_call
    def pins(self, devs, direction=None, printit=True):
        return self.port(devs, direction, printit)


