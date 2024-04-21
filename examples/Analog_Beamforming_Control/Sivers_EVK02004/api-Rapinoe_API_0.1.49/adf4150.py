import evk_logger
from common import *

class Adf4150():

    #If device is MB2_R1.0, will probably not lock due to standing waves
    settings = {'ref_in': 10e6,
                'ref_out': 245.76e6,
                'chp': 15,                  # Chp current 0-15
                'mod': 4095,                # 2 to 4095. 4095 for finest resolution.
                'rdiv': 32,                 # 1 to 1023 r counter division ratio
                'ldf': 0,                   # 0 = frac mode, 1 = int mode
                'prs': 0,                   # 4/5 prescaler for divn down to 23
                'phase': 1,                 # phase control is not used.
                                            # phase can be used to reduce spurs. phase must be lower than mod
                'mode': 0,                  # 0 = low noise, 4 = low spurs
                'ldp': 0,                   # 40 cycles of 10 ns for lock detect
                'mux': 6,                   # 6 = digital LD, 5 = analog LD, 1=DVDD (was 5)
                'doubler': 1,               # enable/disable doubler
                'rdiv2': 1,                 # enable/disable ref divide by 2
                'buf_en': 0,                # double buffer enable
                'polarity': 1,              # positive
                'power_down': 0,            # not powered down
                'cp': 0,                    # should be 0. charge pump three-state off
                'counter_rst': 0,           # should be 0
                'abp': 0,                   # 0 = 6ns, 1 = 3 ns antibacklash pulse width
                'charge_cancel': 0,         # disabled for frac
                'csr': 0,                   # cycle slip reduction disabled
                'clk_div_en': 0,            # clock divider disabled. used for phase resync or fast lock
                'clk_div': 0,
                'fb_sel': 1,                # 1 = fundamental, 0=divided
                'div': 0,                   # no division
                'mute': 0,                  # do not mute until lock detect
                'rf_out_en': 0,             # rf output disabled
                'pout': 0,                  # -4 dbm output power
                'ld': 1,                    # ld pin (0=low, 1 = digital ld, 2=low, 3=high)
                'ldo': 'VCC3V3_SYS'
               }

    def __init__(self, conn, io_exp, indent=None):
        self._conn = conn
        self._pll  = conn.pll
        self._io   = io_exp
        if indent is None:
            self.indent = evk_logger.evk_logger._indent
        else:
            self.indent = indent

    @evk_logger.log_call
    def setup(self, setting=None):
        cfg = self.settings
        if setting is not None:
            for key in setting:
                cfg[key] = setting[key]

        # Calculate int/frac
        cfg['pfd_freq']  = cfg['ref_in']*(1+cfg['doubler'])/\
                           (cfg['rdiv']*(1+cfg['rdiv2']))
        cfg['int_val']   = int(cfg['ref_out']/cfg['pfd_freq'])
        cfg['frac_val']  = round((cfg['ref_out']/cfg['pfd_freq']-cfg['int_val'])*cfg['mod'])
        cfg['vcxo_freq'] = cfg['pfd_freq']*(cfg['int_val']+cfg['frac_val']/cfg['mod'])

        #Create all register words:
        cfg['reg0'] = mshl(0,31,1)                    | mshl(cfg['int_val'],15,16)   |\
                      mshl(cfg['frac_val'],3,12)      |\
                      0
        cfg['reg1'] = mshl(0,28,4)                    | mshl(cfg['prs'],27,1)        |\
                      mshl(cfg['phase'],15,12)        | mshl(cfg['mod'],3,12)        |\
                      1
        cfg['reg2'] = mshl(0,31,1)                    | mshl(cfg['mode'],29,2)       |\
                      mshl(cfg['mux'],26,3)           | mshl(cfg['doubler'],25,1)    |\
                      mshl(cfg['rdiv2'],24,1)         | mshl(cfg['rdiv'],14,10)      |\
                      mshl(cfg['buf_en'],13,1)        | mshl(cfg['chp'],9,4)         |\
                      mshl(cfg['ldf'],8,1)            | mshl(cfg['ldp'],7,1)         |\
                      mshl(cfg['polarity'],6,1)       | mshl(cfg['power_down'],5,1)  |\
                      mshl(cfg['cp'],4,1)             | mshl(cfg['counter_rst'],3,1) |\
                      2
        cfg['reg3'] = mshl(0,23,9)                    | mshl(cfg['abp'],22,1)        |\
                      mshl(cfg['charge_cancel'],21,1) | mshl(0,19,2)                 |\
                      mshl(cfg['csr'],18,1)           | mshl(0,17,1)                 |\
                      mshl(cfg['clk_div_en'],15,2)    | mshl(cfg['clk_div'],3,12)    |\
                      3
        cfg['reg4'] = mshl(0,24,8)                    | mshl(cfg['fb_sel'],23,1)     |\
                      mshl(cfg['div'],20,3)           | mshl(0,11,9)                 |\
                      mshl(cfg['mute'],10,1)          | mshl(0,6,4)                  |\
                      mshl(cfg['rf_out_en'],5,1)      | mshl(cfg['pout'],3,2)        |\
                      4
        cfg['reg5'] = mshl(0,24,8)                    | mshl(cfg['ld'],22,2)         |\
                      mshl(0,3,19)                    |\
                      5
        self.wr(cfg['reg5'])
        self.wr(cfg['reg4'])
        self.wr(cfg['reg3'])
        self.wr(cfg['reg2'])
        self.wr(cfg['reg1'])
        self.wr(cfg['reg0'])
        
        self.settings = cfg
        return self.settings

    @evk_logger.log_call
    def wr(self, addr, data=None):
        if data is None:
            data = addr
        else:
            data = (data<<3) | addr
        send_data = self._pll.format_spi_write(data)
        self._conn.mb.spi_write(self._conn.board_id, self._pll.chip_select, send_data)
        return send_data

    @evk_logger.log_call
    def status(self,printit=False):
        return self._io.status('PLL_LD',printit=printit)

    @evk_logger.log_call
    def calc_ref_offs(self, ref_out_offs):
        return ref_out_offs*self.settings['rdiv']*(1+self.settings['rdiv2'])/\
               (1+self.settings['doubler'])/\
               (self.settings['int_val'] + self.settings['frac_val']/self.settings['mod'])

    @evk_logger.log_call
    def adjust_ref(self, ref_out_offs):
        return self.setup({'ref_in': self.settings['ref_in']+self.calc_ref_offs(ref_out_offs)})

    @evk_logger.log_call
    def get_ref(self):
        return self.settings['vcxo_freq']

