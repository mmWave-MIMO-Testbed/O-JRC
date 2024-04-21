import chip_info
import evk_logger

class Init():
    __instance = None

    def __new__(cls, spi):
        if cls.__instance is None:
            cls.__instance = super(Init, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, spi):
        self.spi         = spi
        self._chip_info  = chip_info.Chip_info(self.spi)
        self.init_values = {
    'AFTER RESET': {
        'bist_config'           : {'cmd': 'SET', 'data': 0x01}
    },
    'EN VCC HIGH w OVR': {
        'en_vcc_high'           : {'cmd': 'WR', 'data':  0x3F},
        'en_vcc_high_ovr'       : {'cmd': 'WR', 'data':  0x0F}
    },
    'CHIP': {
        'bist_config'           : {'cmd': 'WR',  'data': 0x01},
        'biastop_en'            : {'cmd': 'WR',  'data': 0x20}
    },
    'RCU': {
        'bist_config'           : {'cmd': 'SET', 'data': 0x01},
        'biastop_en'            : {'cmd': 'SET', 'data': 0x3C},
        'pll_en'                : {'cmd': 'SET', 'data': 0xF3},
        'cgu_misc_clk'          : {'cmd': 'WR',  'data': 0x03},
        'cgu_freq_ref'          : {'cmd': 'WR',  'data': 0x8000},
        'rgu_misc_rst'          : {'cmd': 'CLR', 'data': 0x02}
    },
    'DIG_PLL': {
        'bist_config'           : {'cmd': 'SET', 'data': 0x01},
        'biastop_en'            : {'cmd': 'SET', 'data': 0x28},
        'pll_en'                : {'cmd': 'SET', 'data': 0x11},
        'digclk_config_status'  : {'cmd': 'WR', 'data': (20<<8)+255}
    },
    'I2C': {
    },
    'EFC': {
    },
    'AMUX': {
    },
    'ADC': {
        'bist_config'           : {'cmd': 'SET', 'data': 0x001},
        'biastop_en'            : {'cmd': 'SET', 'data': 0x3F},
        'adc_ctrl_cfg'          : {'cmd': 'WR',  'data': 0x10},
        'adc_ctrl_time'         : {'cmd': 'WR',  'data': 0x24},
        'adc_ctrl_rst_time'     : {'cmd': 'WR',  'data': 0x32},
        'adc_ctrl_extension'    : {'cmd': 'WR',  'data': 0x14},
        'adc_offs'              : {'cmd': 'WR',  'data': 0x00},
        'adc_coeff_0'           : {'cmd': 'WR',  'data': 0x20},
        'adc_coeff_1'           : {'cmd': 'WR',  'data': 0x40},
        'adc_coeff_2'           : {'cmd': 'WR',  'data': 0x80},
        'adc_coeff_3'           : {'cmd': 'WR',  'data': 0x100},
        'adc_coeff_4'           : {'cmd': 'WR',  'data': 0x200},
        'adc_coeff_5'           : {'cmd': 'WR',  'data': 0x300},
        'adc_coeff_6'           : {'cmd': 'WR',  'data': 0x500},
        'adc_coeff_7'           : {'cmd': 'WR',  'data': 0xA00},
        'adc_coeff_8'           : {'cmd': 'WR',  'data': 0x1200},
        'adc_coeff_9'           : {'cmd': 'WR',  'data': 0x2000},
        'adc_coeff_10'          : {'cmd': 'WR',  'data': 0x4000},
        'adc_coeff_11'          : {'cmd': 'WR',  'data': 0x7800},
        'adc_enable'            : {'cmd': 'WR',  'data': 0x50},
        'adc_ctrl'              : {'cmd': 'WR',  'data': 0x00},
        'adc_dac_strobe_cfg'    : {'cmd': 'WR',  'data': 0x22},
        'adc_dac_cfg'           : {'cmd': 'WR',  'data': 0x00}
    },
    'TEMP': {
        'bist_config'           : {'cmd': 'SET', 'data': 0x80},
        'biastop_en'            : {'cmd': 'SET', 'data': 0x20}
    },
    'SCHED': {
    },
    'FIR': {
    },
    'SYNTH': {
        'bist_config'                : {'cmd': 'SET', 'data': 0x01},
        'biastop_en'                 : {'cmd': 'SET', 'data': 0x3C},
        'vco_en'                     : {'cmd': 'SET', 'data': 0x53},
        'vco_digtune_ibias_override' : {'cmd': 'WR',  'data': 0x00},
        'vco_pll_bias_trim'          : {'cmd': 'WR',  'data': 0x66},
        'pll_ref_sel'                : {'cmd': 'WR',  'data': 0x01},
        'pll_config'                 : {'cmd': 'WR',  'data': 0x02},
        'pll_ld_config'              : {'cmd': 'WR',  'data': 0x10},
        'pll_en'                     : {'cmd': 'WR',  'data': 0xF3},
        'sm_dac'                     : {'cmd': 'WR',  'data': 181},
        'sm_dac_cal'                 : {'cmd': 'WR',  'data': 0x10},
        'sm_vtune_cal'               : {'cmd': 'WR',  'data': 0x04},
        'sm_en'                      : {'cmd': 'SET', 'data': 0x03}
    },
    'SYNTH_ADC': {
        'bist_config'                : {'cmd': 'SET', 'data': 0x01},
        'biastop_en'                 : {'cmd': 'SET', 'data': 0x38},
        'pll_ref_sel'                : {'cmd': 'WR',  'data': 0x01},
        'sm_clk_config'              : {'cmd': 'WR',  'data': 0x011300C004}
    },
    'PLL': {
        'biastop_en'                 : {'cmd': 'SET', 'data': 0x3C}
    },
    'VCO': {
        'biastop_en'                 : {'cmd': 'SET', 'data': 0x30},
        'vco_en'                     : {'cmd': 'SET', 'data': 0x13},
        'sm_en'                      : {'cmd': 'SET', 'data': 0x01}
    },
    'TRX': {
    },
    'TDD': {
    },
    'BIST': {
    },
    'RX': {
        'biastop_en'                 : {'cmd': 'SET', 'data': 0x03},
        'en_vcc_high'                : {'cmd': 'WR',  'data': 0b111111},
        'en_vcc_high_ovr'            : {'cmd': 'WR',  'data': 0b1111},
        'bf_biasref_en'              : {'cmd': 'WR',  'data': 0b0110011},
        'bf_rx_biasref_trim'         : {'cmd': 'WR',  'data': 0x666},
        'com_misc'                   : {'cmd': 'WR',  'data': 0b000010},
        'com_bias_trim'              : {'cmd': 'SET', 'data': 0x000666606},
        'trx_spare'                  : {'cmd': 'WR',  'data': 0x00000704} # com_bias_trim.com_bias_lo_in_trim[2:0] is trx_spare[10:8] in MMF, trx_spare[2] = trx_spare_reg[2] & sd_ctrl.sd_frac_cfg
        
    },
    'TX': {
        'biastop_en'                 : {'cmd': 'SET', 'data': 0x03},
        'en_vcc_high'                : {'cmd': 'WR',  'data': 0b1111111},
        'en_vcc_high_ovr'            : {'cmd': 'WR',  'data': 0b1111},
        'bf_biasref_en'              : {'cmd': 'WR',  'data': 0b0110011},
        'bf_tx_biasref_trim'         : {'cmd': 'WR',  'data': 0x663},
        'com_misc'                   : {'cmd': 'WR',  'data': 0b000010},
        'com_bias_trim'              : {'cmd': 'SET', 'data': 0x666006660},
        'trx_spare'                  : {'cmd': 'WR',  'data': 0x00000704}, # com_bias_trim.com_bias_lo_in_trim[2:0] is trx_spare[10:8] in MMF, trx_spare[2] = trx_spare_reg[2] & sd_ctrl.sd_frac_cfg
        'bb_tx_ctune'                : {'cmd': 'WR',  'data': 0x44}
    },
    'VALIDATION': {
        'pll_en'                     : {'cmd': 'WR',  'data': 0xF7},
        'sm_clk_config'              : {'cmd': 'WR',  'data': 0x0C3D01FFFF}
    }
    }


    def _spi_access(self, cmd):
        case_func = {
            'WRRD' : self.spi.wrrd,
            'WR'   : self.spi.wr,
            'RD'   : self.spi.rd,
            'SET'  : self.spi.set,
            'CLR'  : self.spi.clr,
            'TGL'  : self.spi.tgl
        }
        return case_func.get(cmd,lambda: 'Init access-command does not exist.')


    @evk_logger.log_call
    def set(self, devs, grps='CHIP', printit=True):
        """Initialise registers.
        Init values are defined in the file init.py.
        Each set of init values can be grouped depending on use case, e.g
        only init values for the group 'SYNTH'.
        The default group 'CHIP' must always exist.
        Examples:
        # Init chip rap0 with values from group 'CHIP'
        set(rap0)
        # Init chip rap0 with values from groups ADC and EFC
        set(rap0, ['ADC', 'EFC'])
        # Init chip rap0 with values from group 'MY GROUP' given on command line
        set(rap0, {'MY GROUP': {'bist_config': {'cmd': 'WR', 'data' : 0x20}}})
        # Init chips rap0 and rap1 with values from group 'CHIP'
        set([rap0, rap1],'CHIP')
        """
        init_vals={}
        
        if isinstance(grps, str):
            grps = [grps]
        
        if isinstance(grps, list):
            for grp in grps:
                if isinstance(grp,str):
                    init_vals[grp] = self.init_values[grp]
                elif isinstance(grp, dict):
                    init_vals.update(grp) 
        elif isinstance(grps, dict):
            init_vals = grps
        else:
            evk_logger.evk_logger.log_error('Init: Incorrectly stated groups: {:}'.format(grps))
            return grps

        for blk,regs in init_vals.items():
            if printit:
                evk_logger.evk_logger.log_info('Init {:<29}|'.format(blk.upper()))
            for addr,dstruct in regs.items():
                cmd   = dstruct['cmd']
                data  = dstruct['data']
                width = self.spi._size(addr)
                old_data = self._spi_access(cmd)(devs, addr, data)
                new_data = self.spi.rd(devs,addr)
                if printit:
                    evk_logger.evk_logger.log_info('  {:<4} {:<27}| {:<}  ({:<} -> {:<})'.format(cmd.lower(), addr, '0x{:0{:}X}'.format(data, width), '0x{:0{:}X}'.format(old_data, width), '0x{:0{:}X}'.format(new_data, width)))

    @evk_logger.log_call
    def get(self, devs, grps=None, printit=False):
        if grps == None:
            return self.init_values
        if not isinstance(grps, list):
            grps = [grps]

        grp_keys = list(self.init_values.keys())
        ret = {}
        for grp in grps:
            if grp.upper() in grp_keys:
                ret[grp.upper()] = (self.init_values[grp.upper()].copy())
        return ret

    @evk_logger.log_call
    def get_grps(self, devs, printit=False):
        return list(self.init_values.keys())
