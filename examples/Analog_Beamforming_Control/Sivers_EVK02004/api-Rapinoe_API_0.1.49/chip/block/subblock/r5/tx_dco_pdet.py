from math import sqrt, log10
import time
import datetime
import evk_logger
from common import fhex

USE_EXT_POWER_MEAS = False

if USE_EXT_POWER_MEAS:
    import sivers_instrument_drivers.instruments.spectrum_analyzers.n9040b as n9040b

ADC_REP = 10
DCO_STAGE = 1

class TxDcoPdet():

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
            conf_inst={'address':'TCPIP0::10.1.1.22', 'device':'n9040b'}
            self.sa = n9040b.N9040b(conf_inst)

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
            self.step = [3, 2, 1]
            self.sweep_step = [6, 5, 2, 1]
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
            self.step = [30, 15, 2]
            self.sweep_step = [40, 10, 5, 1]
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
        reg_list = ['ssw_cfg_on_bf_en_tx_v', 'ssw_cfg_on_bf_en_tx_h', 'bb_tx_config_v', 'bb_tx_config_h', 'com_bias_lo_trim', \
                    'com_bias_tx_trim', 'com_lo_det_ctrl', \
                    'ssw_cfg_on_en_tx', 'ssw_cfg_on_sel_tx', 'bf_tx_biasref_trim']
        self.reg_backup[dev.get_name()] = {}
        for reg in reg_list:
            print (reg, self._spi.rd(dev, reg))
            self.reg_backup[dev.get_name()][reg] = self._spi.rd(dev, reg)

    def _restore_settings(self, dev, tx_pol, gain_index=0):
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

    def _pre_calibration_settings(self, dev, pol, gain_index=0):
        """Sets the register values that need specific values before starting the calibration.

        Args:
            dev (Rap object): Selected device
        """
        self.current_tx_gain_index = self._chip.tx.curr_gain_index(dev, pol)
        tx_ram_row = self._chip.ram.rd(dev, 'tx_ram_'+pol.lower(), gain_index)
        self.tx_ram_row_backup = tx_ram_row
        bf_att_com = 0x1f
        bf_gain_tx_vga = 0x00 #0xff
        com_gain_tx_vga = 0x3f
        #com_gain_tx_vga = 0x0
        tx_ram_row = tx_ram_row & 0xF80000
        tx_ram_row = tx_ram_row | (bf_att_com << 14) | (bf_gain_tx_vga <<6) | (com_gain_tx_vga)
        #self._chip.ram.wr(dev, 'tx_ram_'+pol.lower(), gain_index, tx_ram_row)
        #self._chip.tx.gain_rf(dev, gain_index, 'T'+pol.upper())

    def _meas_slope(self, dev, pol, rx_pol):
        reg_div = 20
        lo_leakage_magn0 = self._meas_lo_leakage_magn(dev, 0, 0, pol, rx_pol=rx_pol, n=1)
        lo_leakage_magn1 = self._meas_lo_leakage_magn(dev, int(self.max_reg_value/reg_div), 0, pol, rx_pol=rx_pol, n=1)
        lo_leakage_magn2 = self._meas_lo_leakage_magn(dev, 0, int(self.max_reg_value/reg_div), pol, rx_pol=rx_pol, n=1)

        return [(lo_leakage_magn0 - lo_leakage_magn1) / (0 - int(self.max_reg_value/reg_div)), (lo_leakage_magn0 - lo_leakage_magn2) / (0 - int(self.max_reg_value/reg_div))]

    def _read_tx_pdet(self, dev, pol, pdet_num, num_of_meas=4):
        pol = pol.upper()
        amux_ctrl_cfg = self._spi.rd(dev, 'amux_ctrl_cfg')
        self._spi.clr(dev, 'amux_ctrl_cfg', 0x300000)
        pdet = 0
        for n in range(num_of_meas):
            pdet += self._adc.get_data(dev, 'TX DET {} {}'.format(pol, pdet_num))
        pdet = pdet / num_of_meas
        self._spi.wr(dev, 'amux_ctrl_cfg', amux_ctrl_cfg)
        return pdet

    def _meas_lo_leakage_magn(self, dev, bbtx_dco_q, bbtx_dco_i, pol, num_of_meas=1, use_pdet=[0,1,2,3]):
        """Measures LO leakage magnitude.

        Args:
            dev (Rap object): Selected device.
            bbtx_dco_q (int): Value of bbtx_dco_q to be used (0x0 to 0x7ff for IF and 0x0 to 0xff for BB).
            bbtx_dco_i (int): Value of bbtx_dco_i to be used (0x0 to 0x7ff for IF and 0x0 to 0xff for BB).
            pol (str): Polarization as 'V' or 'H'

        Returns:
            int: Measured LO leakage magnitude.
        """
        value = self._merge_fields(bbtx_dco_i, bbtx_dco_q)
        self._write_reg(dev, pol, value)
        time.sleep(0.001)
        n = 0
        p = 0
        if 0 in use_pdet:
            p = self._read_tx_pdet(dev, pol, 0, num_of_meas=num_of_meas)
            n += 1
        if 1 in use_pdet:
            p += self._read_tx_pdet(dev, pol, 1, num_of_meas=num_of_meas)
            n += 1
        if 2 in use_pdet:
            p += self._read_tx_pdet(dev, pol, 2, num_of_meas=num_of_meas)
            n += 1
        if 3 in use_pdet:
            p += self._read_tx_pdet(dev, pol, 3, num_of_meas=num_of_meas)
            n += 1
        return p/n

    def calibrate_fine_tune(self, dev, pol, search_offset=2, bbtx_dco_reg=None, num_of_meas=1):
        pol = pol.lower()
        if bbtx_dco_reg == None:
            bbtx_dco_reg = self._read_reg(dev, pol)
        bbtx_dco_reg = self._get_fields(bbtx_dco_reg)
        bbtx_dco_q = bbtx_dco_reg['reg_dco_q']
        bbtx_dco_i = bbtx_dco_reg['reg_dco_i']

        q_search_offset = search_offset*1

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
                lo_leakage_magn = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i, pol, num_of_meas=num_of_meas)
                while lo_leakage_magn < 0.0:
                    lo_leakage_magn = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i, pol, num_of_meas=num_of_meas)
                if (bbtx_dco_i == bbtx_dco_i_range[0]):
                    print (hex(bbtx_dco_q), end='\t')
                print(round(lo_leakage_magn, 4), end='\t')
                if lo_leakage_magn <= min_lo_leakage_magn:
                    min_lo_leakage_magn = lo_leakage_magn
                    optimal_bbtx_dco_q = bbtx_dco_q
                    optimal_bbtx_dco_i = bbtx_dco_i
        print('')

        reg_val = self._merge_fields(optimal_bbtx_dco_i, optimal_bbtx_dco_q)

        self._write_reg(dev, pol, reg_val)

        return { 'reg_dco_q': optimal_bbtx_dco_q, 'reg_dco_i' : optimal_bbtx_dco_i, 'lo_leakage_magn' : min_lo_leakage_magn}

    def _select_init_point(self, dev, pol):
        NUM_OF_POINTS = 6
        init_point = {'best_i_point':0, 'best_q_point':0, 'lowest_lo_leakage':5000}
        points = range(round(self.max_reg_value/NUM_OF_POINTS), self.max_reg_value-round(self.max_reg_value/NUM_OF_POINTS), round(self.max_reg_value/NUM_OF_POINTS))
        for p1 in points:
            for p2 in points:
                reg_val = self._merge_fields(p1, p2)
                self._write_reg(dev, pol, reg_val)
                lo_leakage_magn = self._read_tx_pdet(dev, pol, 0)
                if lo_leakage_magn <= init_point['lowest_lo_leakage']:
                    init_point = {'best_i_point':p1, 'best_q_point':p2, 'lowest_lo_leakage':lo_leakage_magn}

        reg_val = self._merge_fields(init_point['best_i_point'], init_point['best_q_point'])
        self._write_reg(dev, pol, reg_val)
        return init_point

    def sweep(self, dev, pol, i_q, fixed_point, dac_0, step=100, num_of_meas=4, use_pdet=[0,1,2,3], p_change=0.05):
        min_lo_leakage_magn = {'magn':1000, 'i_dac':0, 'q_dac':0}
        if dac_0 < 0 : dac_0 = 0
        exit_counter = 5
        for dac in range(dac_0, self.max_reg_value, step):
            if i_q == 'i':
                lo_leakage_magn = self._meas_lo_leakage_magn(dev, fixed_point, dac, pol, num_of_meas=num_of_meas, use_pdet=use_pdet)
            else:
                lo_leakage_magn = self._meas_lo_leakage_magn(dev, dac, fixed_point, pol, num_of_meas=num_of_meas, use_pdet=use_pdet)
            print(i_q, dac, round(lo_leakage_magn,3))
            if lo_leakage_magn <= min_lo_leakage_magn['magn']:
                min_lo_leakage_magn['magn'] = lo_leakage_magn
                if i_q == 'i':
                    min_lo_leakage_magn['i_dac'] = dac
                    min_lo_leakage_magn['q_dac'] = fixed_point
                else:
                    min_lo_leakage_magn['i_dac'] = fixed_point
                    min_lo_leakage_magn['q_dac'] = dac
            else:
                if lo_leakage_magn > min_lo_leakage_magn['magn']*(1+p_change) :
                    if exit_counter == 0:
                        break
                    else:
                        exit_counter -= 1

        return min_lo_leakage_magn

    def nr(self, dev, pol, i_dac_init, i_dac_0, i_dac_1, q_dac_init, q_dac_0, q_dac_1, step, target=None, num_of_meas=4, max_iter=60, slope_check=True, printit=True):
        stop_iteration = False
        num_of_iterations = 0
        bbtx_dco_i = i_dac_init
        bbtx_dco_q = q_dac_init
        d = 0.0
        slope_i = 0.1
        slope_q = 0.1
        max_lo_leakage_magn = 0
        min_lo_leakage_magn = {'magn':1000, 'i_dac':0, 'q_dac':0}
        lo_leakage_magn = self._read_tx_pdet(dev, pol, 0)
        prev_lo_leakage_magn = 1
        lo_leakage_magn_a = []
        SLOPE_N = 4
        conv_slope = 100
        while (not stop_iteration):
            lo_leakage_magn_qn = self._meas_lo_leakage_magn(dev, bbtx_dco_q-step, bbtx_dco_i, pol, num_of_meas=num_of_meas)
            lo_leakage_magn_qp = self._meas_lo_leakage_magn(dev, bbtx_dco_q+step, bbtx_dco_i, pol, num_of_meas=num_of_meas)
            lo_leakage_magn_in = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i-step, pol, num_of_meas=num_of_meas)
            lo_leakage_magn_ip = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i+step, pol, num_of_meas=num_of_meas)
            # calculate the gradients for N-R iteration
            k = 1.0
            prev_d = d
            d = ((lo_leakage_magn_ip-lo_leakage_magn_in)**2 + (lo_leakage_magn_qp-lo_leakage_magn_qn)**2)
            try:
                xi = (k * (lo_leakage_magn_ip-lo_leakage_magn_in)) / d
            except:
                #d = prev_d
                continue
                #xi = (k * (lo_leakage_magn_ip-lo_leakage_magn_in)) / d

            try:
                xq = (k * (lo_leakage_magn_qp-lo_leakage_magn_qn)) / d
            except:
                #d = prev_d
                continue
                #xq = (k * (lo_leakage_magn_qp-lo_leakage_magn_qn)) / d

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
            lo_leakage_magn = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i, pol, num_of_meas=num_of_meas)

            if (lo_leakage_magn >=3*prev_lo_leakage_magn) or (prev_lo_leakage_magn >=3*lo_leakage_magn):
                if printit:
                    evk_logger.evk_logger.log_info('Remeasure! ({})'.format(lo_leakage_magn))
                lo_leakage_magn = self._meas_lo_leakage_magn(dev, bbtx_dco_q, bbtx_dco_i, pol, num_of_meas=num_of_meas)
            lo_leakage_magn = round(lo_leakage_magn, 3)
            if max_lo_leakage_magn == 0:
                max_lo_leakage_magn = lo_leakage_magn
                if target == None:
                    target = round(max_lo_leakage_magn / 3.0, 3)
                    print('target: {}'.format(target))
            if len(lo_leakage_magn_a) == SLOPE_N:
                lo_leakage_magn_a.insert(0,lo_leakage_magn)
                lo_leakage_magn_a.pop()
                conv_slope = (lo_leakage_magn_a[0]-lo_leakage_magn_a[SLOPE_N-1])/SLOPE_N
                if slope_check:
                    #print('conv_slope',conv_slope)
                    if conv_slope < 0 and conv_slope >= -0.0006:
                        stop_iteration = True
            else:
                lo_leakage_magn_a.insert(0,lo_leakage_magn)
            
            if printit:
                if USE_EXT_POWER_MEAS:
                    if pol == 'v':
                        evk_logger.evk_logger.log_info('{}: {}  {}: {}  lo_leakage_magn: {:.3f} sa: {}dBm  step: {:>3}'.format(self.field_q_v, fhex(bbtx_dco_q, 3), self.field_i_v, fhex(bbtx_dco_i, 3), lo_leakage_magn, self.sa.FindPeak(), step))
                    else:
                        evk_logger.evk_logger.log_info('{}: {}  {}: {}  lo_leakage_magn: {:.3f} sa: {}dBm  step: {:>3}'.format(self.field_q_h, fhex(bbtx_dco_q, 3), self.field_i_h, fhex(bbtx_dco_i, 3), lo_leakage_magn, self.sa.FindPeak(), step))
                else:
                    if pol == 'v':
                        evk_logger.evk_logger.log_info('{}: {}  {}: {}  lo_leakage_magn: {:.4f}  step: {:>3}'.format(self.field_q_v, fhex(bbtx_dco_q, 3), self.field_i_v, fhex(bbtx_dco_i, 3), lo_leakage_magn, step))
                    else:
                        evk_logger.evk_logger.log_info('{}: {}  {}: {}  lo_leakage_magn: {:.4f}  step: {:>3}'.format(self.field_q_h, fhex(bbtx_dco_q, 3), self.field_i_h, fhex(bbtx_dco_i, 3), lo_leakage_magn, step))

            if lo_leakage_magn <= min_lo_leakage_magn['magn']:
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

    def calibrate2(self, dev, mode, pol, com_lo_det_gain=0x7):
        """Performs LO leakage calibration.

        Args:
            dev (Rap object): Selected device.
            pol (str): Polarization as 'v' or 'h'.

        Returns:
            dict: A dictionary containing the optimal bbtx_dco_q and bbtx_dco_i values and the resulting LO leakage magnitude.
        """
        init_time = datetime.datetime.now()
        self._adc.enable(dev)
        pol = pol.lower()
        if pol == 'v' or pol == 'tv':
            pol = 'v'
        elif pol == 'h' or pol == 'th':
            pol = 'h'
        else:
            print("pol should be either 'v', 'tv', 'h' or 'th'.")
            return None

        mode = mode.upper()
        if mode != 'IF' and mode != 'BB':
            print("mode should be either 'if' or 'bb'.")
            return None
        self._backup_settings(dev)

        if pol == 'v':
            self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':1, 'com_lo_det_en_h':0, 'com_lo_det_gain_v':com_lo_det_gain, 'com_lo_det_gain_h':0})
        else:
            self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':0, 'com_lo_det_en_h':1, 'com_lo_det_gain_v':0, 'com_lo_det_gain_h':com_lo_det_gain})

        self._prepare_mode_params(mode)
        if mode == 'IF':
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x8080)
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x0000000)
        else:
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x4000400)
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x0000)

        self._pre_calibration_settings(dev, pol)

        # Select start DAC values
        init_point = self._select_init_point(dev, pol)
        bbtx_dco_q = init_point['best_q_point']
        bbtx_dco_i = init_point['best_i_point']
        print('init_point', init_point)
        res = self.nr(dev, pol, bbtx_dco_i, 0, self.max_reg_value, bbtx_dco_q, 0, self.max_reg_value, self.step[0], num_of_meas=1, slope_check=False)
        print(res)
        min_lo_leakage_magn = {'magn':1000, 'i_dac':0, 'q_dac':0}
        #res = self.nr(dev, pol, rx_pol, res['i_dac'], 0, self.max_reg_value, res['q_dac'], 0, self.max_reg_value, self.step[1], target=res['magn']/4)
        if res['magn'] <= min_lo_leakage_magn['magn']:
            min_lo_leakage_magn = res
        print(res)

        #if res['magn'] > 0.001:
        #    res = self.nr(dev, pol, res['i_dac'], 0, self.max_reg_value, res['q_dac'], 0, self.max_reg_value, self.step[1], target=0.0, max_iter=25, num_of_meas=2, slope_check=False)
        if res['magn'] <= min_lo_leakage_magn['magn']:
            min_lo_leakage_magn = res
        print(res)

        if pol == 'v':
            self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':1, 'com_lo_det_en_h':0, 'com_lo_det_gain_v':0xf, 'com_lo_det_gain_h':0})
        else:
            self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':0, 'com_lo_det_en_h':1, 'com_lo_det_gain_v':0, 'com_lo_det_gain_h':0xf})

        fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(min_lo_leakage_magn['i_dac'], min_lo_leakage_magn['q_dac']), num_of_meas=2)
        fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(fine_tune_res['reg_dco_i'], fine_tune_res['reg_dco_q']), num_of_meas=2)
        fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(fine_tune_res['reg_dco_i'], fine_tune_res['reg_dco_q']), num_of_meas=2)
        fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(fine_tune_res['reg_dco_i'], fine_tune_res['reg_dco_q']), num_of_meas=2)
        fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(fine_tune_res['reg_dco_i'], fine_tune_res['reg_dco_q']), num_of_meas=2)
        print(fine_tune_res)
        result = {'reg_dco_q' : fine_tune_res['reg_dco_q'], 'reg_dco_i' : fine_tune_res['reg_dco_i'], 'lo_leakage_magn' : fine_tune_res['lo_leakage_magn']}

        if True:
            if mode == 'BB':
                # Adjust IF DACs
                print('Adjusting IF DACs')
                #value = self._merge_fields(result['reg_dco_i']+1, result['reg_dco_q']+1)
                #self._write_reg(dev, pol, value)
                if pol == 'v':
                    self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':1, 'com_lo_det_en_h':0, 'com_lo_det_gain_v':com_lo_det_gain, 'com_lo_det_gain_h':0})
                else:
                    self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':0, 'com_lo_det_en_h':1, 'com_lo_det_gain_v':0, 'com_lo_det_gain_h':com_lo_det_gain})
                self._prepare_mode_params('IF')
                init_point = self._select_init_point(dev, pol)
                bbtx_dco_q = init_point['best_q_point']
                bbtx_dco_i = init_point['best_i_point']
                res = self.nr(dev, pol, bbtx_dco_i, 0, self.max_reg_value, bbtx_dco_q, 0, self.max_reg_value, self.step[1], target=0.0, num_of_meas=1, slope_check=False, max_iter=20)
                if pol == 'v':
                    self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':1, 'com_lo_det_en_h':0, 'com_lo_det_gain_v':com_lo_det_gain, 'com_lo_det_gain_h':0})
                else:
                    self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':0, 'com_lo_det_en_h':1, 'com_lo_det_gain_v':0, 'com_lo_det_gain_h':com_lo_det_gain})

                fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(res['i_dac'], res['q_dac']))
                fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(fine_tune_res['reg_dco_i'], fine_tune_res['reg_dco_q']))
                fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(fine_tune_res['reg_dco_i'], fine_tune_res['reg_dco_q']))
                fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(fine_tune_res['reg_dco_i'], fine_tune_res['reg_dco_q']))
                fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=1, bbtx_dco_reg=self._merge_fields(fine_tune_res['reg_dco_i'], fine_tune_res['reg_dco_q']))
                #reg_val = self._merge_fields(res['i_dac'], res['q_dac'])
                #self._write_reg(dev, pol, reg_val)
                self._prepare_mode_params('BB')
                #value = self._merge_fields(result['reg_dco_i'], result['reg_dco_q'])
                #self._write_reg(dev, pol, value)
#            else:
#                # Adjust BB DACs
#                print('Adjusting BB DACs')
#                self._prepare_mode_params('BB')
#                init_point = self._select_init_point(dev, pol)
#                bbtx_dco_q = init_point['best_q_point']
#                bbtx_dco_i = init_point['best_i_point']
#                res = self.nr(dev, pol, bbtx_dco_i, 0, self.max_reg_value, bbtx_dco_q, 0, self.max_reg_value, self.step[1], target=-1, num_of_meas=1, slope_check=False)
#                fine_tune_res = self.calibrate_fine_tune(dev, pol, search_offset=3, bbtx_dco_reg=self._merge_fields(res['i_dac'], res['q_dac']))
#                #reg_val = self._merge_fields(res['i_dac'], res['q_dac'])
#                #self._write_reg(dev, pol, reg_val)
#                self._prepare_mode_params('IF')

        self._restore_settings(dev, pol)
        end_time = datetime.datetime.now()
        time_elapsed = end_time - init_time
        print('Time elapsed: {}s'.format(time_elapsed.seconds))
        return result
    
    def calibrate(self, dev, mode, pol, com_lo_det_gain=0xf, use_pdet=[0,1,2,3]):
        """Performs LO leakage calibration.

        Args:
            dev (Rap object): Selected device.
            pol (str): Polarization as 'v' or 'h'.

        Returns:
            dict: A dictionary containing the optimal bbtx_dco_q and bbtx_dco_i values and the resulting LO leakage magnitude.
        """
        init_time = datetime.datetime.now()
        self._adc.enable(dev)
        pol = pol.lower()
        if pol == 'v' or pol == 'tv':
            pol = 'v'
        elif pol == 'h' or pol == 'th':
            pol = 'h'
        else:
            print("pol should be either 'v', 'tv', 'h' or 'th'.")
            return None

        mode = mode.upper()
        if mode != 'IF' and mode != 'BB':
            print("mode should be either 'if' or 'bb'.")
            return None

        if isinstance(use_pdet, int):
            use_pdet = [use_pdet]

        self._backup_settings(dev)

        if pol == 'v':
            self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':1, 'com_lo_det_en_h':0, 'com_lo_det_gain_v':com_lo_det_gain, 'com_lo_det_gain_h':0})
        else:
            self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':0, 'com_lo_det_en_h':1, 'com_lo_det_gain_v':0, 'com_lo_det_gain_h':com_lo_det_gain})

        self._prepare_mode_params(mode)
        if mode == 'IF':
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x8080)
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x0000000)
        else:
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x4000400)
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x0000)

        self._pre_calibration_settings(dev, pol)

        # Select start DAC values
        init_point = self._select_init_point(dev, pol)
        bbtx_dco_q = init_point['best_q_point']
        bbtx_dco_i = init_point['best_i_point']
        print('init_point', init_point)

        ############################################
        NUM_OF_ITER = 4
        min_lo_leakage_magn = [None]*(NUM_OF_ITER*2+2)
        min_lo_leakage_magn[0] = self.sweep(dev, pol, 'i', bbtx_dco_q, 0, step=self.sweep_step[0], num_of_meas=1, use_pdet=use_pdet)
        print(min_lo_leakage_magn[0])
        min_lo_leakage_magn[1] = self.sweep(dev, pol, 'q', min_lo_leakage_magn[0]['i_dac'], 0, step=self.sweep_step[0], num_of_meas=1, use_pdet=use_pdet)
        print(min_lo_leakage_magn[1])

        dac_backoff = [-10, -10, -5, -5]
        num_of_meas = [2, 2, 2, 6]
        for n in range(0, NUM_OF_ITER):
            min_lo_leakage_magn[n*2+2] = self.sweep(dev, pol, 'i', min_lo_leakage_magn[n*2+1]['q_dac'], min_lo_leakage_magn[n*2+1]['i_dac']+dac_backoff[n], step=self.sweep_step[n], num_of_meas=num_of_meas[n], use_pdet=use_pdet)
            print(min_lo_leakage_magn[n*2+2])
            min_lo_leakage_magn[n*2+3] = self.sweep(dev, pol, 'q', min_lo_leakage_magn[n*2+2]['i_dac'], min_lo_leakage_magn[n*2+2]['q_dac']+dac_backoff[n], step=self.sweep_step[n], num_of_meas=num_of_meas[n], use_pdet=use_pdet)
            print(min_lo_leakage_magn[n*2+3])

        value = self._merge_fields(min_lo_leakage_magn[NUM_OF_ITER*2+1]['i_dac'], min_lo_leakage_magn[NUM_OF_ITER*2+1]['q_dac'])
        self._write_reg(dev, pol, value)

        ############################################

        self._restore_settings(dev, pol)
        end_time = datetime.datetime.now()
        time_elapsed = end_time - init_time
        print('Time elapsed: {}s'.format(time_elapsed.seconds))

        result = {'reg_dco_q' : min_lo_leakage_magn[NUM_OF_ITER*2+1]['q_dac'], 'reg_dco_i' : min_lo_leakage_magn[NUM_OF_ITER*2+1]['i_dac'], 'lo_leakage_magn' : min_lo_leakage_magn[NUM_OF_ITER*2+1]['magn']}

        if True:
            if mode == 'BB':
                # Adjust IF DACs
                print('Adjusting IF DACs')
                if pol == 'v':
                    self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':1, 'com_lo_det_en_h':0, 'com_lo_det_gain_v':com_lo_det_gain, 'com_lo_det_gain_h':0})
                else:
                    self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':0, 'com_lo_det_en_h':1, 'com_lo_det_gain_v':0, 'com_lo_det_gain_h':com_lo_det_gain})
                self._prepare_mode_params('IF')
                init_point = self._select_init_point(dev, pol)
                bbtx_dco_q = init_point['best_q_point']
                bbtx_dco_i = init_point['best_i_point']

                ###########################################
                NUM_OF_ITER = 4
                min_lo_leakage_magn = [None]*(NUM_OF_ITER*2+2)
                min_lo_leakage_magn[0] = self.sweep(dev, pol, 'i', bbtx_dco_q, 0, step=self.sweep_step[0], num_of_meas=1, use_pdet=use_pdet)
                print(min_lo_leakage_magn[0])
                min_lo_leakage_magn[1] = self.sweep(dev, pol, 'q', min_lo_leakage_magn[0]['i_dac'], 0, step=self.sweep_step[0], num_of_meas=1, use_pdet=use_pdet)
                print(min_lo_leakage_magn[1])

                dac_backoff = [-10, -10, -5, -5]
                num_of_meas = [2, 2, 2, 6]
                for n in range(0, NUM_OF_ITER):
                    min_lo_leakage_magn[n*2+2] = self.sweep(dev, pol, 'i', min_lo_leakage_magn[n*2+1]['q_dac'], min_lo_leakage_magn[n*2+1]['i_dac']+dac_backoff[n], step=self.sweep_step[n], num_of_meas=num_of_meas[n], use_pdet=use_pdet)
                    print(min_lo_leakage_magn[n*2+2])
                    min_lo_leakage_magn[n*2+3] = self.sweep(dev, pol, 'q', min_lo_leakage_magn[n*2+2]['i_dac'], min_lo_leakage_magn[n*2+2]['q_dac']+dac_backoff[n], step=self.sweep_step[n], num_of_meas=num_of_meas[n], use_pdet=use_pdet)
                    print(min_lo_leakage_magn[n*2+3])

                value = self._merge_fields(min_lo_leakage_magn[NUM_OF_ITER*2+1]['i_dac'], min_lo_leakage_magn[NUM_OF_ITER*2+1]['q_dac'])
                self._write_reg(dev, pol, value)

                ###########################################

                if pol == 'v':
                    self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':1, 'com_lo_det_en_h':0, 'com_lo_det_gain_v':com_lo_det_gain, 'com_lo_det_gain_h':0})
                else:
                    self._spi.wr(dev, 'com_lo_det_ctrl', {'com_lo_det_readout_en':1, 'com_lo_det_en_v':0, 'com_lo_det_en_h':1, 'com_lo_det_gain_v':0, 'com_lo_det_gain_h':com_lo_det_gain})

                self._prepare_mode_params('BB')

        self._restore_settings(dev, pol)
        end_time = datetime.datetime.now()
        time_elapsed = end_time - init_time
        print('Time elapsed: {}s'.format(time_elapsed.seconds))
        return result


    def sweep_if(self, dev, pol, step=100, q_dac=[0,0x7ff], i_dac=[0,0x7ff], printit=True, com_lo_det_ctrl=0x60700):
        """SWEEP2

        Args:
            dev (Rap object): Selected device.
            pol (str): Polarization as 'v' or 'h'.

        Returns:
            dict: A dictionary containing the optimal bbtx_dco_q and bbtx_dco_i values and the resulting LO leakage magnitude.
        """
        import numpy as np

        init_time = datetime.datetime.now()
        self._adc.enable(dev)
        self._spi.wr(dev, 'com_lo_det_ctrl', com_lo_det_ctrl)
        pol = pol.lower()
        mode = 'IF'
        self._prepare_mode_params(mode)
        if mode == 'IF':
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x8080)
        else:
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x4000400)

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
                magn = self._meas_lo_leakage_magn(dev, q, i, pol)
                lo_leakage_i.append(magn)
                if magn <= min_value['lo_leakage']:
                    min_value['lo_leakage'] = magn
                    min_value['bbtx_dco_i'] = i
                    min_value['bbtx_dco_q'] = q
            lo_leakage.append(lo_leakage_i)

            #print ('Best:', min_value)
        value = self._merge_fields(min_value['bbtx_dco_i'], min_value['bbtx_dco_q'])
        self._write_reg(dev, pol, value)

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
            if pol == 'v':
                plt.xlabel(self.field_q_v)
                plt.ylabel(self.field_i_v)
            else:
                plt.xlabel(self.field_q_h)
                plt.ylabel(self.field_i_h)

            ax.zaxis.set_major_formatter('{x:.02f}')
            plt.show()

        end_time = datetime.datetime.now()
        time_elapsed = end_time - init_time
        print('Time elapsed: {}s'.format(time_elapsed.seconds))
        return min_value

    def sweep_bb(self, dev, pol, step=10, q_dac=[0,0xff], i_dac=[0,0xff], printit=True, com_lo_det_ctrl=0x60700):
        """SWEEP_BB

        Args:
            dev (Rap object): Selected device.
            pol (str): Polarization as 'v' or 'h'.

        Returns:
            dict: A dictionary containing the optimal bbtx_dco_q and bbtx_dco_i values and the resulting LO leakage magnitude.
        """
        import numpy as np

        init_time = datetime.datetime.now()
        self._adc.enable(dev)
        self._spi.wr(dev, 'com_lo_det_ctrl', com_lo_det_ctrl)
        pol = pol.lower()
        mode = 'BB'
        self._prepare_mode_params(mode)
        if mode == 'IF':
            self._spi.wr(dev, 'bb_tx_dco_bb_'+pol, 0x8080)
        else:
            self._spi.wr(dev, 'bb_tx_dco_'+pol, 0x4000400)

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
                magn = self._meas_lo_leakage_magn(dev, q, i, pol)
                lo_leakage_i.append(magn)
                if magn <= min_value['lo_leakage']:
                    min_value['lo_leakage'] = magn
                    min_value['bbtx_dco_i'] = i
                    min_value['bbtx_dco_q'] = q
            lo_leakage.append(lo_leakage_i)

            #print ('Best:', min_value)

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
            if pol == 'v':
                plt.xlabel(self.field_q_v)
                plt.ylabel(self.field_i_v)
            else:
                plt.xlabel(self.field_q_h)
                plt.ylabel(self.field_i_h)

            ax.zaxis.set_major_formatter('{x:.02f}')
            plt.show()

        end_time = datetime.datetime.now()
        time_elapsed = end_time - init_time
        print('Time elapsed: {}s'.format(time_elapsed.seconds))
        return min_value
