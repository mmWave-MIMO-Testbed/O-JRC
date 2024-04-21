from math import sqrt
import time
import datetime
import evk_logger
from common import fhex

USE_EXT_POWER_MEAS = False

if USE_EXT_POWER_MEAS:
    import sys
    sys.path.append('C:\dev\pedram_api\drivers\instruments\spectrum_analyzers')
    #import e4448a
    import n9041b

# FOR TESTING
import random

class TxDco():

    def __init__(self, chip):
        self._chip = chip
        self._tx = chip.tx
        self._rx = chip.rx
        self._ram = chip.ram
        self._adc = chip.adc
        self._spi = chip.spi
        self.reg_backup = {}
        self.amux_src = {'VI1': 'BB V RX I PGA1 DC',
                    'VQ1': 'BB V RX Q PGA1 DC',
                    'VI2': 'BB V RX I PGA2 DC',
                    'VQ2': 'BB V RX Q PGA2 DC',
                    'HI1': 'BB H RX I PGA1 DC',
                    'HQ1': 'BB H RX Q PGA1 DC',
                    'HI2': 'BB H RX I PGA2 DC',
                    'HQ2': 'BB H RX Q PGA2 DC'}
        self.lb_ext = 0
        if USE_EXT_POWER_MEAS:
            conf_inst={'address':'TCPIP0::10.1.1.22', 'device':'n9041b'}
            self.sa = n9041b.N9041b(conf_inst)

    def _prepare_mode_params(self, mode):
        self.mode = mode.upper()
        if self.mode == 'BB':
            self.dco_v = 'bb_tx_dco_bb_v'
            self.dco_h = 'bb_tx_dco_bb_h'
            self.field_i_v = 'bbtx_dco_bb_i_v'
            self.field_i_h = 'bbtx_dco_bb_i_h'
            self.field_q_v = 'bbtx_dco_bb_q_v'
            self.field_q_h = 'bbtx_dco_bb_q_h'
            self.field_size = 8
            self.max_reg_value = 0xff
            self.step = [15, 8, 2]
            self.max_rx_gain = 0x35
        elif self.mode == 'IF':
            self.dco_v = 'bb_tx_dco_v'
            self.dco_h = 'bb_tx_dco_h'
            self.field_i_v = 'bbtx_dco_i_v'
            self.field_i_h = 'bbtx_dco_i_h'
            self.field_q_v = 'bbtx_dco_q_v'
            self.field_q_h = 'bbtx_dco_q_h'
            self.field_size = 16
            self.max_reg_value = 0x7ff
            self.step = [30, 5, 2]
            self.max_rx_gain = 0x3f

    def _get_fields(self, reg_dco):
        reg_dco_i = reg_dco & (2**self.field_size-1)
        reg_dco_q = (reg_dco >> self.field_size) & (2**self.field_size-1)

        return {'reg_dco_i' : reg_dco_i, 'reg_dco_q' : reg_dco_q}

    def _merge_fields(self, reg_dco_i, reg_dco_q):
        return (reg_dco_i + (reg_dco_q<<self.field_size))

    def _read_reg(self, dev, polarization):
        if polarization.lower() == 'v':
            return self._spi.rd(dev, self.dco_v)
        return self._spi.rd(dev, self.dco_h)
    
    def _write_reg(self, dev, polarization, value):
        if polarization.lower() == 'v':
            self._spi.wr(dev, self.dco_v, value)
        else:
            self._spi.wr(dev, self.dco_h, value)

    def _clear_tx(self, dev, pol):
        self._spi.wr(dev, 'ssw_cfg_on_bf_en_tx_'+pol.lower(), 0)
        self._spi.wr(dev, 'bb_tx_config_'+pol.lower(), 0)
        if pol.lower() == 'v':
            self._spi.clr(dev, 'ssw_cfg_on_en_tx', 0xf0)
            self._spi.clr(dev, 'ssw_cfg_on_sel_tx', 0xf0)
        else:
            self._spi.clr(dev, 'ssw_cfg_on_en_tx', 0x0f)
            self._spi.clr(dev, 'ssw_cfg_on_sel_tx', 0x0f)

    def _backup_settings(self, dev):
        """Backs up the current values of specified registers
        from the selected device.

        Args:
            dev (Rap object): Device to back up.
            reg_list (list) : List containing names of devices to back up.
        """
        reg_list = ['ssw_cfg_on_bf_en_tx_v', 'ssw_cfg_on_bf_en_tx_h', 'bb_tx_config_v', 'bb_tx_config_h', 'com_bias_trim', 'bb_rx_en_dco', \
                    'bb_rx_config_v', 'bb_rx_config_h', 'ssw_cfg_on_sel_rx', 'ssw_cfg_on_en_rx_h', 'ssw_cfg_on_en_rx_v', \
                    'ssw_cfg_on_bf_en_rx_v', 'ssw_cfg_on_bf_en_rx_h', 'ssw_cfg_on_en_tx', 'ssw_cfg_on_sel_tx', 'bf_tx_biasref_trim']
        self.reg_backup[dev.get_name()] = {}
        for reg in reg_list:
            print (reg, self._spi.rd(dev, reg))
            self.reg_backup[dev.get_name()][reg] = self._spi.rd(dev, reg)

    def _restore_settings(self, dev, tx_pol, rx_pol, gain_index=0):
        """Restores the values of registers that were previously backed up
        by _backup_settings.

        Args:
            dev (Rap object): Device to restore.
        """
        for reg in list(self.reg_backup[dev.get_name()]):
            print (reg, self._spi.rd(dev, reg), ' -> ', self.reg_backup[dev.get_name()][reg])
            self._spi.wr(dev, reg, self.reg_backup[dev.get_name()][reg])

        self._chip.ram.wr(dev, 'tx_ram_'+tx_pol.lower(), gain_index, self.tx_ram_row_backup)
        self._chip.tx.gain_rf(dev, self.current_tx_gain_index, 'T'+tx_pol.upper())

        self._chip.ram.wr(dev, 'rx_ram_'+rx_pol.lower(), 0, self.rx_ram_row_backup)
        self._chip.rx.gain(dev, 0, 'R'+rx_pol.upper())

    def _pre_calibration_settings(self, dev, pol, gain_index=0):
        """Sets the register values that need specific values before starting the calibration.

        Args:
            dev (Rap object): Selected device
        """
        self._spi.clr(dev, 'ssw_cfg_on_sel_rx', 0x44)

        self._spi.clr(dev, 'bf_tx_biasref_trim', 0b00001110000) # bf_biasref_vgatx_trim -> 0

        
        # if pol.lower() == 'v':
        #     self._spi.wr(dev, 'ssw_cfg_on_bf_en_tx_v', 0)
        # else:
        #     self._spi.wr(dev, 'ssw_cfg_on_bf_en_tx_h', 0)
        
        self._spi.wrrd(dev, 'com_bias_trim', 0x666666666) # txvga txpa txmix rxvga rxmix lo_in lo_mid lo_out_tx lo_out_rx

        self.current_tx_gain_index = self._chip.tx.curr_gain_index(dev, pol)
        tx_ram_row = self._chip.ram.rd(dev, 'tx_ram_'+pol.lower(), gain_index)
        self.tx_ram_row_backup = tx_ram_row
        bf_att_com = 0x00
        bf_gain_tx_vga = 0xff
        com_gain_tx_vga = 0x3f
        tx_ram_row = tx_ram_row & 0xF80000
        tx_ram_row = tx_ram_row | (bf_att_com << 14) | (bf_gain_tx_vga <<6) | (com_gain_tx_vga)
        self._chip.ram.wr(dev, 'tx_ram_'+pol.lower(), gain_index, tx_ram_row)
        self._chip.tx.gain_rf(dev, gain_index, 'T'+pol.upper())

    def _meas_slope(self, dev, pol, rx_pol):
        reg_div = 20
        lo_leakage_magn0 = self._meas_lo_leakage_magn(dev, 0, 0, pol, rx_pol=rx_pol, n=1)
        lo_leakage_magn1 = self._meas_lo_leakage_magn(dev, int(self.max_reg_value/reg_div), 0, pol, rx_pol=rx_pol, n=1)
        lo_leakage_magn2 = self._meas_lo_leakage_magn(dev, 0, int(self.max_reg_value/reg_div), pol, rx_pol=rx_pol, n=1)

        return [(lo_leakage_magn0 - lo_leakage_magn1) / (0 - int(self.max_reg_value/reg_div)), (lo_leakage_magn0 - lo_leakage_magn2) / (0 - int(self.max_reg_value/reg_div))]

    def _rx_setup(self, dev, pol, rx_pol):
        self._chip.init(dev, 'RX', printit=False)
        ant_en_v = 0 #self._spi.rd(dev,'ssw_cfg_on_bf_en_rx_v')
        ant_en_h = 0 #self._spi.rd(dev,'ssw_cfg_on_bf_en_rx_h')
        self._chip.rx.setup(dev, 'BB', 'R'+rx_pol.upper(), ant_en_v=ant_en_v, ant_en_h=ant_en_h)
        self.rx_ram_row_backup = self._chip.ram.rd(dev, 'rx_ram_'+rx_pol.lower(), 0)
        rx_gain_base = 0x00000001FFDE00000000
        com_gain_rx_vga = 0x3f
        self._chip.ram.wr(dev, 'rx_ram_'+rx_pol.lower(), 0, rx_gain_base)
        self._chip.rx.gain(dev, 0, 'R'+rx_pol.upper())
        self.set_rx_gain(dev, rx_pol, com_gain_rx_vga)
        self._spi.clr(dev, 'ssw_cfg_on_sel_rx', 0x44)
        self._chip.rx.dco.calibrate(dev, rx_pol.upper(), 0)

    def _select_rx_gain(self, dev, pol, rx_pol):
        evk_logger.evk_logger.log_info('Selecting RX gain')
        rx_gain_base = 0x00000001FFDE00000000
        rx_gain = self._chip.ram.rd(dev, 'rx_ram_'+rx_pol.lower(), 0)
        rx_gain_base = rx_gain_base + (rx_gain & 0xffffffff)
        num_neg_grad = 0
        for com_gain_rx_vga in range(0x3f, -1, -1):
            rx_gain = rx_gain_base + (com_gain_rx_vga << 49)
            self._chip.ram.wr(dev, 'rx_ram_'+rx_pol.lower(), 0, rx_gain)
            self._chip.rx.gain(dev, 0, 'R'+rx_pol.upper())
            [gradient0, gradient1] = self._meas_slope(dev, pol, rx_pol)
            evk_logger.evk_logger.log_info('rx_gain: {} {:>15.10f} {:>15.10f}'.format(fhex(rx_gain, 20), round(gradient0, 10), round(gradient1, 10)), indentation=4)
            if gradient0 < -0.0001 and gradient1 < -0.0001:
                num_neg_grad = num_neg_grad + 1
                if num_neg_grad == 2:
                    self._chip.ram.wr(dev, 'rx_ram_'+rx_pol.lower(), 0, rx_gain)
                    self._chip.rx.gain(dev, 0, 'R'+rx_pol.upper())
                    evk_logger.evk_logger.log_info('Selected RX gain: {}'.format(fhex(rx_gain, 20)))
                    break
                else:
                    prev_rx_gain = rx_gain
            else:
                num_neg_grad = 0

    def _read_dco(self, dev, pol, chan, stage, reps=10):
        """Reads and returns DC offset at the specified point.

        Args:
            dev (_type_): Device ID (e.g. rap0)
            pol (_type_): Polarization ('V' or 'H')
            chan (_type_): Channel ('I' or 'Q')
            stage (_type_): Stage ('1' for PGA1 or '2' for PGA2)
        """
        return self._adc.get_data(dev, self.amux_src[pol.upper()+chan.upper()+str(stage)], reps=reps)

    def _read_tx_pdet(self, dev, pol, pdet_num):
        pol = pol.upper()
        return self._adc.get_data(dev, 'TX DET {} {}'.format(pol, pdet_num))

    def _meas_lo_leakage_magn(self, dev, bbtx_dco_q, bbtx_dco_i, pol, rx_pol, test_data=False, reps=10, n=2):
        """Measures LO leakage magnitude.

        Args:
            dev (Rap object): Selected device.
            bbtx_dco_q (int): Value of bbtx_dco_q to be used (0x0 to 0x7ff for IF and 0x0 to 0xff for BB).
            bbtx_dco_i (int): Value of bbtx_dco_i to be used (0x0 to 0x7ff for IF and 0x0 to 0xff for BB).
            pol (str): Polarization as 'V' or 'H'

        Returns:
            int: Measured LO leakage magnitude.
        """

        if test_data:
            bbtx_dco = self._merge_fields(bbtx_dco_i, bbtx_dco_q)
            lo_leakage = self._get_test_data(bbtx_dco)
        else:
            value = self._merge_fields(bbtx_dco_i, bbtx_dco_q)
            self._write_reg(dev, pol, value)
            mean_lo_leakage = 0
            for i in range(n):
                # MEASURE LO leakage
                #self._spi.clr(dev, 'com_bias_trim', 0x0f0000000) #TX PA trim
                ###self._spi.clr(dev, 'com_bias_trim', 0x00f000000) #TX mix trim
                ###self._spi.clr(dev, 'com_bias_trim', 0xf00000000) #TX vga trim
                self._spi.clr(dev, 'com_bias_trim', 0xfff000000) #TX trim all off
                if pol != rx_pol:
                    self._switch_lb(dev, pol, False)
                i_dco_diff_o = self._read_dco(dev, rx_pol, 'I', 2, reps)
                q_dco_diff_o = self._read_dco(dev, rx_pol, 'Q', 2, reps)

                #self._spi.set(dev, 'com_bias_trim', 0x060000000) #TX PA trim
                ###self._spi.set(dev, 'com_bias_trim', 0x006000000) #TX mix trim
                ###self._spi.set(dev, 'com_bias_trim', 0x600000000) #TX vga trim
                self._spi.set(dev, 'com_bias_trim', 0x666000000) #TX trim all on
                if pol != rx_pol:
                    self._switch_lb(dev, pol, True)

                i_dco_diff = self._read_dco(dev, rx_pol, 'I', 2, reps)
                q_dco_diff = self._read_dco(dev, rx_pol, 'Q', 2, reps)
                lo_leakage = sqrt((i_dco_diff - i_dco_diff_o)**2+ (q_dco_diff - q_dco_diff_o)**2)
                mean_lo_leakage = mean_lo_leakage + lo_leakage
            mean_lo_leakage = mean_lo_leakage / n

        return mean_lo_leakage

    def calibrate_fine_tune(self, dev, pol, rx_pol, search_offset=1, bbtx_dco_reg=None):
        pol = pol.lower()
        if bbtx_dco_reg == None:
            bbtx_dco_reg = self._read_reg(dev, pol)
        bbtx_dco_reg = self._get_fields(bbtx_dco_reg)
        bbtx_dco_q = bbtx_dco_reg['reg_dco_q']
        bbtx_dco_i = bbtx_dco_reg['reg_dco_i']

        q_search_offset = search_offset*10

        if bbtx_dco_q-q_search_offset < 0:
            bbtx_dco_q = q_search_offset
        if bbtx_dco_i-search_offset < 0:
            bbtx_dco_i = search_offset
        
        if bbtx_dco_q+q_search_offset > self.max_reg_value:
            bbtx_dco_q = bbtx_dco_q - q_search_offset
        if bbtx_dco_i-search_offset > self.max_reg_value:
            bbtx_dco_i = bbtx_dco_i - search_offset

        bbtx_dco_q_range = [bbtx_dco_q-q_search_offset, bbtx_dco_q+q_search_offset+1]
        bbtx_dco_i_range = [bbtx_dco_i-search_offset, bbtx_dco_i+search_offset+1]

        min_lo_leakage_magn = 1000
        optimal_bbtx_dco_q = 0
        optimal_bbtx_dco_i = 0
        print('Q \ I', end='\t')
        for bbtx_dco_i in range(bbtx_dco_i_range[0], bbtx_dco_i_range[1]):
            print(hex(bbtx_dco_i), end='\t')

        for bbtx_dco_q in range(bbtx_dco_q_range[0], bbtx_dco_q_range[1]):
            print('')
            for bbtx_dco_i in range(bbtx_dco_i_range[0], bbtx_dco_i_range[1]):
                lo_leakage_magn = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i, pol, rx_pol=rx_pol, reps=10, n=1)
                if (bbtx_dco_i == bbtx_dco_i_range[0]):
                    print (hex(bbtx_dco_q), end='\t')
                if USE_EXT_POWER_MEAS:
                    print('{:.4f}'.format(lo_leakage_magn), '{:5.1f}'.format(self.sa.FindPeak()), end='\t')
                else:
                    print(round(lo_leakage_magn, 4), end='\t')
                if lo_leakage_magn <= min_lo_leakage_magn:
                    min_lo_leakage_magn = lo_leakage_magn
                    optimal_bbtx_dco_q = bbtx_dco_q
                    optimal_bbtx_dco_i = bbtx_dco_i
        print('')

        reg_val = self._merge_fields(optimal_bbtx_dco_i, optimal_bbtx_dco_q)

        self._write_reg(dev, pol, reg_val)

        return { 'reg_dco_q': optimal_bbtx_dco_q, 'reg_dco_i' : optimal_bbtx_dco_i, 'lo_leakage_magn' : min_lo_leakage_magn}

    def _select_init_point(self, dev, pol, rx_pol):
        NUM_OF_POINTS = 12
        init_point = {'best_i_point':0, 'best_q_point':0, 'lowest_lo_leakage':5000}
        points = range(round(self.max_reg_value/NUM_OF_POINTS), self.max_reg_value-round(self.max_reg_value/NUM_OF_POINTS), round(self.max_reg_value/NUM_OF_POINTS))
        for p1 in points:
            for p2 in points:
                reg_val = self._merge_fields(p1, p2)
                self._write_reg(dev, pol, reg_val)
                lo_leakage_magn = self._meas_lo_leakage_magn(dev, p1, p2, pol, rx_pol, n=1)
                if lo_leakage_magn <= init_point['lowest_lo_leakage']:
                    init_point = {'best_i_point':p1, 'best_q_point':p2, 'lowest_lo_leakage':lo_leakage_magn}

        reg_val = self._merge_fields(init_point['best_i_point'], init_point['best_q_point'])
        self._write_reg(dev, pol, reg_val)
        return init_point

    def _switch_lb(self, dev, pol, on_off):
        self._spi.clr(dev, 'com_misc', 0xf0)
        if pol == 'h':
            if self.lb_ext == 0:
                if on_off:
                    self._spi.set(dev, 'com_misc', 0x40)
                else:
                    self._spi.clr(dev, 'com_misc', 0x40)
            else:
                if on_off:
                    self._spi.set(dev, 'com_misc', 0x20)
                else:
                    self._spi.clr(dev, 'com_misc', 0x20)
        else:
            if self.lb_ext == 0:
                if on_off:
                    self._spi.set(dev, 'com_misc', 0x10)
                else:
                    self._spi.clr(dev, 'com_misc', 0x10)
            else:
                if on_off:
                    self._spi.set(dev, 'com_misc', 0x80)
                else:
                    self._spi.clr(dev, 'com_misc', 0x80)

    def nr(self, dev, pol, rx_pol, i_dac_init, i_dac_0, i_dac_1, q_dac_init, q_dac_0, q_dac_1, step, target=None, num_of_meas=1, max_iter=50, slope_check=False, printit=True):
        stop_iteration = False
        num_of_iterations = 0
        bbtx_dco_i = i_dac_init
        bbtx_dco_q = q_dac_init
        d = 0.0
        slope_i = 0.1
        slope_q = 0.1
        max_lo_leakage_magn = 0
        min_lo_leakage_magn = {'magn':1000, 'i_dac':0, 'q_dac':0}
        lo_leakage_magn = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i, pol, rx_pol=rx_pol, n=1)
        prev_lo_leakage_magn = 1
        lo_leakage_magn_a = []
        SLOPE_N = 4
        conv_slope = 100
        while (not stop_iteration):
            lo_leakage_magn_qn = self._meas_lo_leakage_magn(dev, bbtx_dco_q-step, bbtx_dco_i, pol, rx_pol=rx_pol, n=num_of_meas)
            lo_leakage_magn_qp = self._meas_lo_leakage_magn(dev, bbtx_dco_q+step, bbtx_dco_i, pol, rx_pol=rx_pol, n=num_of_meas)
            lo_leakage_magn_in = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i-step, pol, rx_pol=rx_pol, n=num_of_meas)
            lo_leakage_magn_ip = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i+step, pol, rx_pol=rx_pol, n=num_of_meas)
            # calculate the gradients for N-R iteration
            k = 1.0
            prev_d = d
            d = ((lo_leakage_magn_ip-lo_leakage_magn_in)**2 + (lo_leakage_magn_qp-lo_leakage_magn_qn)**2)
            try:
                xi = (k * (lo_leakage_magn_ip-lo_leakage_magn_in)) / d
            except:
                d = prev_d
                xi = (k * (lo_leakage_magn_ip-lo_leakage_magn_in)) / d

            try:
                xq = (k * (lo_leakage_magn_qp-lo_leakage_magn_qn)) / d
            except:
                d = prev_d
                xq = (k * (lo_leakage_magn_qp-lo_leakage_magn_qn)) / d

            if xi != 0:
                slope_i  = 1/xi
            if xq != 0:
                slope_q  = 1/xq

            di = round(-2*lo_leakage_magn/slope_i)
            dq = round(-2*lo_leakage_magn/slope_q)

            if di == 0 and dq == 0:
                #stop_iteration = True
                pass
            else:
                prev_bbtx_dco_i = bbtx_dco_i
                bbtx_dco_i = bbtx_dco_i + di
                if (bbtx_dco_i < i_dac_0) or (bbtx_dco_i > i_dac_1):
                    bbtx_dco_i = prev_bbtx_dco_i
                prev_bbtx_dco_q = bbtx_dco_q
                bbtx_dco_q = bbtx_dco_q + dq
                if (bbtx_dco_q < q_dac_0) or (bbtx_dco_q > q_dac_1):
                    bbtx_dco_q = prev_bbtx_dco_q

            # Calculate new LO leakage magnitude
            prev_lo_leakage_magn = lo_leakage_magn
            lo_leakage_magn = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i, pol, rx_pol=rx_pol, n=num_of_meas)

            if (lo_leakage_magn >=3*prev_lo_leakage_magn) or (prev_lo_leakage_magn >=3*lo_leakage_magn):
                if printit:
                    evk_logger.evk_logger.log_info('Remeasure! ({})'.format(lo_leakage_magn))
                lo_leakage_magn = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i, pol, rx_pol=rx_pol, n=num_of_meas)
            lo_leakage_magn = round(lo_leakage_magn, 3)
            if max_lo_leakage_magn == 0:
                max_lo_leakage_magn = lo_leakage_magn
                if target == None:
                    target = round(max_lo_leakage_magn / 30, 3)
                    print('target: {}'.format(target))
            if len(lo_leakage_magn_a) == SLOPE_N:
                lo_leakage_magn_a.insert(0,lo_leakage_magn)
                lo_leakage_magn_a.pop()
                conv_slope = (lo_leakage_magn_a[0]-lo_leakage_magn_a[SLOPE_N-1])/SLOPE_N
                if slope_check:
                    print('conv_slope',conv_slope)
                    if conv_slope < 0 and conv_slope >= -0.0006:
                        stop_iteration = True
            else:
                lo_leakage_magn_a.insert(0,lo_leakage_magn)
            
            if printit:
                if pol == 'v':
                    if USE_EXT_POWER_MEAS:
                        evk_logger.evk_logger.log_info(self.field_q_v + ': ' + fhex(bbtx_dco_q, 3) + '\t' + self.field_i_v + ': ' + fhex(bbtx_dco_i, 3) + '\t' + 'lo_leakage_magn: ' + '{:.3f}'.format(lo_leakage_magn) + '\tPower: ' + '{:5.1f}'.format(self.sa.FindPeak()) + 'dBm' + '\tstep: ' + str(step))
                    else:
                        evk_logger.evk_logger.log_info('{}: {}  {}: {}  lo_leakage_magn: {:.3f}  step: {:>3}'.format(self.field_q_v, fhex(bbtx_dco_q, 3), self.field_i_v, fhex(bbtx_dco_i, 3), lo_leakage_magn, step))
                else:
                    if USE_EXT_POWER_MEAS:
                        evk_logger.evk_logger.log_info(self.field_q_h + ': ' + fhex(bbtx_dco_q, 3) + '\t' + self.field_i_h + ': ' + fhex(bbtx_dco_i, 3) + '\t' + 'lo_leakage_magn: ' + '{:.3f}'.format(lo_leakage_magn) + '\tPower: ' + '{:5.1f}'.format(self.sa.FindPeak()) + 'dBm'  + '\tstep: ' + str(step))
                    else:
                        evk_logger.evk_logger.log_info('{}: {}  {}: {}  lo_leakage_magn: {:.3f}  step: {:>3}'.format(self.field_q_h, fhex(bbtx_dco_q, 3), self.field_i_h, fhex(bbtx_dco_i, 3), lo_leakage_magn, step))

            if lo_leakage_magn < min_lo_leakage_magn['magn']:
                min_lo_leakage_magn['magn'] = lo_leakage_magn
                min_lo_leakage_magn['i_dac'] = bbtx_dco_i
                min_lo_leakage_magn['q_dac'] = bbtx_dco_q

            if lo_leakage_magn <= target:
                stop_iteration = True
            else:
                num_of_iterations = num_of_iterations + 1
                if (num_of_iterations >= max_iter) and (prev_lo_leakage_magn < lo_leakage_magn):
                    stop_iteration = True

        return min_lo_leakage_magn

    def calibrate(self, dev, mode, pol, cross_pol=True, fine_tune=True):
        """Performs LO leakage calibration.

        Args:
            dev (Rap object): Selected device.
            pol (str): Polarization as 'v' or 'h'.

        Returns:
            dict: A dictionary containing the optimal bbtx_dco_q and bbtx_dco_i values and the resulting LO leakage magnitude.
        """
        init_time = datetime.datetime.now()
        self._backup_settings(dev)
        pol = pol.lower()
        if cross_pol:
            if pol == 'v':
                rx_pol = 'h'
            else:
                rx_pol = 'v'
            self._clear_tx(dev, rx_pol)
        else:
            rx_pol = pol
        mode = mode.upper()
        self._prepare_mode_params(mode)
        if mode == 'IF':
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x8080)
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x0000000)
        else:
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x4000400)
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x0000)

        self._rx_setup(dev, pol, rx_pol)
        if pol != rx_pol:
            self._switch_lb(dev, pol, True)

        self._pre_calibration_settings(dev, pol)

        self._select_rx_gain(dev, pol, rx_pol)

        # Select start DAC values
        init_point = self._select_init_point(dev, pol, rx_pol=rx_pol)
        bbtx_dco_q = init_point['best_q_point']
        bbtx_dco_i = init_point['best_i_point']
        res = self.nr(dev, pol, rx_pol, bbtx_dco_i, 0, self.max_reg_value, bbtx_dco_q, 0, self.max_reg_value, self.step[0])
        print(res)
        self.set_rx_gain(dev, rx_pol, self.max_rx_gain)
        min_lo_leakage_magn = {'magn':1000, 'i_dac':0, 'q_dac':0}
        res = self.nr(dev, pol, rx_pol, res['i_dac'], 0, self.max_reg_value, res['q_dac'], 0, self.max_reg_value, self.step[1], target=res['magn']/4)
        if res['magn'] <= min_lo_leakage_magn['magn']:
            min_lo_leakage_magn = res
        print(res)
        if res['magn'] > 0.0001:
            res = self.nr(dev, pol, rx_pol, res['i_dac'], 0, self.max_reg_value, res['q_dac'], 0, self.max_reg_value, self.step[2], target=0.0, max_iter=25, slope_check=False)
        if res['magn'] <= min_lo_leakage_magn['magn']:
            min_lo_leakage_magn = res
        print(res)
        self.set_rx_gain(dev, rx_pol, 0x3f)
        fine_tune_res = self.calibrate_fine_tune(dev, pol, rx_pol=rx_pol, search_offset=1, bbtx_dco_reg=self._merge_fields(min_lo_leakage_magn['i_dac'], min_lo_leakage_magn['q_dac']))
        print(fine_tune_res)
        result = {'reg_dco_q' : fine_tune_res['reg_dco_q'], 'reg_dco_i' : fine_tune_res['reg_dco_i'], 'lo_leakage_magn' : fine_tune_res['lo_leakage_magn']}

        if pol != rx_pol:
            self._switch_lb(dev, pol, False)
        self._restore_settings(dev, pol, rx_pol)
        end_time = datetime.datetime.now()
        time_elapsed = end_time - init_time
        print('Time elapsed: {}s'.format(time_elapsed.seconds))
        return result

    def sweep(self, dev, mode, pol, rx_pol, gain_index, step=100, q_dac=[0,0x7ff], i_dac=[0,0x7ff], printit=False):
        """SWEEP2

        Args:
            dev (Rap object): Selected device.
            pol (str): Polarization as 'v' or 'h'.

        Returns:
            dict: A dictionary containing the optimal bbtx_dco_q and bbtx_dco_i values and the resulting LO leakage magnitude.
        """
        import numpy as np

        init_time = datetime.datetime.now()
        pol = pol.lower()
        rx_pol = rx_pol.lower()
        mode = mode.upper()
        self._prepare_mode_params(mode)
        if mode == 'IF':
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x8080)
        else:
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x4000400)
        self._backup_settings(dev)

        self._rx_setup(dev, pol, rx_pol)
        if pol != rx_pol:
            self._switch_lb(dev, pol, True)

        self._pre_calibration_settings(dev, pol, gain_index)
        #self._select_rx_gain(dev, pol, rx_pol)
        self.set_rx_gain(dev, rx_pol, 0x3f)

        min_value = {'bbtx_dco_i': 0, 'bbtx_dco_q': 0, 'lo_leakage': 10000}
        lo_leakage = []
        total_num_of_meas = (1 + (q_dac[1] - q_dac[0]) // step) * (1 + (i_dac[1] - i_dac[0]) // step)
        current_meas_num = 1
        prev_progress_procent = 10
        for q in range(q_dac[0], q_dac[1], step):
            lo_leakage_i = []
            prev_magn = -1
            for i in range(i_dac[0], i_dac[1], step):
                progress_procent = round(current_meas_num/total_num_of_meas*100)
                if prev_progress_procent != progress_procent:
                    prev_progress_procent = progress_procent
                    print('\b'*(len(str(progress_procent)) + 1), end='')
                    print (str(progress_procent)+'%', end='')
                current_meas_num = current_meas_num + 1
                try:
                    prev_magn = magn
                except:
                    pass
                magn = self._meas_lo_leakage_magn(dev, q, i, pol, rx_pol, test_data=False, n=1)
                lo_leakage_i.append(magn)
                if magn <= min_value['lo_leakage']:
                    min_value['lo_leakage'] = magn
                    min_value['bbtx_dco_i'] = i
                    min_value['bbtx_dco_q'] = q
            lo_leakage.append(lo_leakage_i)

            print ('Best:', min_value)

        if printit:
            import matplotlib.pyplot as plt
            from matplotlib import cm
            from matplotlib.ticker import LinearLocator

            fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
            X = np.arange(q_dac[0], q_dac[1], step)
            Y = np.arange(i_dac[0], i_dac[1], step)
            X, Y = np.meshgrid(X, Y)
            Z = np.array(lo_leakage)
            surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
            if pol == 'V':
                plt.xlabel(self.field_q_v)
                plt.ylabel(self.field_i_v)
            else:
                plt.xlabel(self.field_q_h)
                plt.ylabel(self.field_i_h)

            ax.zaxis.set_major_formatter('{x:.02f}')
            plt.show()


        if pol != rx_pol:
            self._switch_lb(dev, pol, False)
        self._restore_settings(dev, pol, rx_pol, gain_index)
        end_time = datetime.datetime.now()
        time_elapsed = end_time - init_time
        print('Time elapsed: {}s'.format(time_elapsed.seconds))
        return min_value

    def test_prepare(self, dev, mode, pol, rx_pol, gain_index):
        pol = pol.lower()
        rx_pol = rx_pol.lower()
        mode = mode.upper()
        self._prepare_mode_params(mode)
        if mode == 'IF':
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x8080)
        else:
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x4000400)
        self._backup_settings(dev)

        self._rx_setup(dev, pol, rx_pol)
        if pol != rx_pol:
            self._switch_lb(dev, pol, True)

        self._pre_calibration_settings(dev, pol, gain_index)
        #self._select_rx_gain(dev, pol, rx_pol)
        self.set_rx_gain(dev, rx_pol, 0x3f)


    def test_dac(self, dev, pol, rx_pol, q_dac, i_dac):
        magn = self._meas_lo_leakage_magn(dev, q_dac, i_dac, pol, rx_pol, test_data=False, n=4)
        return magn


    def get_rx_gain(self, dev, rx_pol):
        rx_gain = self._chip.ram.rd(dev, 'rx_ram_'+rx_pol.lower(), 0)
        com_gain_rx_vga = (rx_gain >> 49) & 0b111111
        return com_gain_rx_vga

    def set_rx_gain(self, dev, rx_pol, com_gain_rx_vga):
        rx_gain = self._chip.ram.rd(dev, 'rx_ram_'+rx_pol.lower(), 0)
        rx_gain = (rx_gain & 0x1ffffffffffff) + (com_gain_rx_vga << 49)
        self._chip.ram.wr(dev, 'rx_ram_'+rx_pol.lower(), 0, rx_gain)
        self._chip.rx.gain(dev, 0, 'R'+rx_pol.upper())

    def _generate_test_data(self, plotit=False):

        import numpy as np

        X = np.arange(-40, 60, 100/(self.max_reg_value+1))
        Y = np.arange(-70, 30, 100/(self.max_reg_value+1))
        X, Y = np.meshgrid(X, Y)
        self.Z = (-1.0015**(-(X**2 + Y**2))*2000) + 2000
        if plotit:
            import matplotlib.pyplot as plt
            from matplotlib import cm
            from matplotlib.ticker import LinearLocator

            fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
            surf = ax.plot_surface(X, Y, self.Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
            ax.zaxis.set_major_formatter('{x:.02f}')
            plt.show()

    def _get_test_data(self, reg_bbtx_dco):
        reg = self._get_fields(reg_bbtx_dco)
        return self.Z[reg['reg_dco_q']][reg['reg_dco_i']]


    def sweep_sa_meas(self, dev, mode, pol, gain_index,first_bbtx_dco_q=0, last_bbtx_dco_q=None, first_bbtx_dco_i=0, last_bbtx_dco_i=None, step=1, plotit=True):
        import sys
        sys.path.append('C:\dev\Validation\drivers\instruments\spectrum_analyzers')
        import csv
        import e4448a
        conf_inst={'address':'TCPIP0::10.1.1.2', 'device':'e4448a'}
        sa = e4448a.E4448a(conf_inst)
        sa.FindPeak()

        with open('lo_leakage.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            pol = pol.lower()
            mode = mode.upper()
            self._prepare_mode_params(mode)
            if mode == 'IF':
                self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x8080)
            else:
                self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x7ff07ff)

            import numpy as np
            if last_bbtx_dco_q == None:
                last_bbtx_dco_q = self.max_reg_value + 1
            if last_bbtx_dco_i == None:
                last_bbtx_dco_i = self.max_reg_value + 1

            min_value = {'bbtx_dco_i': 0, 'bbtx_dco_q': 0, 'lo_leakage': 10000}
            pol = pol.upper()
            lo_leakage = []
            total_num_of_meas = (1 + (last_bbtx_dco_q - first_bbtx_dco_q) // step) * (1 + (last_bbtx_dco_i - first_bbtx_dco_i) // step)
            current_meas_num = 1
            prev_progress_procent = 10
            for q in range(first_bbtx_dco_q, last_bbtx_dco_q, step):
                lo_leakage_i = []
                for i in range(first_bbtx_dco_i, last_bbtx_dco_i, step):
                    progress_procent = round(current_meas_num/total_num_of_meas*100)
                    if prev_progress_procent != progress_procent:
                        prev_progress_procent = progress_procent
                        print('\b'*(len(str(progress_procent)) + 1), end='')
                        print (str(progress_procent)+'%', end='')
                    current_meas_num = current_meas_num + 1
                    value = self._merge_fields(i, q)
                    self._write_reg(dev, pol, value)
                    magn = sa.FindPeak()
                    lo_leakage_i.append(magn)
                    writer.writerow([i, q, magn])
                    if magn <= min_value['lo_leakage']:
                        min_value['lo_leakage'] = magn
                        min_value['bbtx_dco_i'] = i
                        min_value['bbtx_dco_q'] = q
                lo_leakage.append(lo_leakage_i)

            X = np.arange(first_bbtx_dco_q, last_bbtx_dco_q, step)
            Y = np.arange(first_bbtx_dco_i, last_bbtx_dco_i, step)
            X, Y = np.meshgrid(X, Y)
            Z = np.array(lo_leakage)
            np.savetxt("lo_leakage_X.csv", X, delimiter=";")
            np.savetxt("lo_leakage_Y.csv", Y, delimiter=";")
            np.savetxt("lo_leakage_Z.csv", Z, delimiter=";")

        if plotit:
            import matplotlib.pyplot as plt
            from matplotlib import cm
            from matplotlib.ticker import LinearLocator

            fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
            surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
            if pol == 'V':
                plt.xlabel(self.field_q_v)
                plt.ylabel(self.field_i_v)
            else:
                plt.xlabel(self.field_q_h)
                plt.ylabel(self.field_i_h)

            ax.zaxis.set_major_formatter('{x:.02f}')
            plt.show()

        return min_value