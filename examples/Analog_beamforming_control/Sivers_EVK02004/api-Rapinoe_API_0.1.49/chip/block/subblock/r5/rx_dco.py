import evk_logger
from common import fhex

ADC_REPS = 4
class RxDco():

    __instance = None

    def __new__(cls, rx, ram, adc):
        if cls.__instance is None:
            cls.__instance = super(RxDco, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, rx, ram, adc):
        self._rx = rx
        self._spi = self._rx._spi
        self._ram = ram
        self._adc = adc
        self.amux_src = {'VI1': 'BB V RX I PGA1 DC',
                         'VQ1': 'BB V RX Q PGA1 DC',
                         'VIF': 'BB V RX I FILT DC',
                         'VQF': 'BB V RX Q FILT DC',
                         'VI2': 'BB V RX I PGA2 DC',
                         'VQ2': 'BB V RX Q PGA2 DC',
                         'HI1': 'BB H RX I PGA1 DC',
                         'HQ1': 'BB H RX Q PGA1 DC',
                         'HIF': 'BB H RX I FILT DC',
                         'HQF': 'BB H RX Q FILT DC',
                         'HI2': 'BB H RX I PGA2 DC',
                         'HQ2': 'BB H RX Q PGA2 DC'}

        self.field_index = {'bbrx_i_dco_drv':15,
                            'bbrx_i_dco_filter':14,
                            'bbrx_i_dco_input':13,
                            'bbrx_q_dco_drv':12,
                            'bbrx_q_dco_filter':11,
                            'bbrx_q_dco_input':10,
                            'bbrx_i_pga2_gain':9,
                            'bbrx_i_filter_gain':8,
                            'bbrx_q_pga2_gain':7,
                            'bbrx_q_filter_gain':6,
                            'bbrx_iq_filter_gain':5,
                            'bbrx_iq_pga1_gain':4,
                            'com_gain_rx_vga':3,
                            'bf_gain_rx_vga':2,
                            'bf_gain_lna':1,
                            'bf_att_com':0}

        fields = list(self._spi.register_map.reg_map['rx_ram_v'])
        self.field_details = [None]*len(fields)
        n = 0
        for field in fields:
            lsb = self._spi.register_map.reg_map['rx_ram_v'][field]['Lsb']
            msb = self._spi.register_map.reg_map['rx_ram_v'][field]['Msb']
            self.field_details[n] = {'field':field, 'lsb':lsb, 'msb':msb, 'size':msb-lsb+1}
            n = n + 1

        self.field_sizes = [n['size'] for n in self.field_details]

        self._row_value = None
        self._backup_row_value = {}


    def _separate_value(self, value):
        v = [0]*len(self.field_sizes)
        for j in range(len(v)):
            xmask = 2**self.field_sizes[len(v)-j-1]-1
            v[len(v)-j-1] = (value & xmask)
            value = value >> self.field_sizes[len(v)-j-1]
        return v

    def _compact_value(self, values):
        value = 0
        for n in range(len(self.field_sizes)):
            try:
                value += ((values[n]&(2**self.field_details[n]['size']-1))<<self.field_details[n]['lsb'])
            except:
                values[n] = None

        if None in values:
            value = None
        return value

    def _write_row(self, dev, pol, gain_index, row_data):
        if isinstance(row_data, list):
            compact_row_data = self._compact_value(row_data)
        else:
            compact_row_data = row_data
        if pol.upper() == 'V':
            self._ram.wr(dev, 'rx_ram_v', gain_index, compact_row_data)
            self._rx.gain(dev, gain_index, pol='RV')
        else:
            self._ram.wr(dev, 'rx_ram_h', gain_index, compact_row_data)
            self._rx.gain(dev, gain_index, pol='RH')


    def _backup_settings(self, dev, pol, gain_index):
        """Backs up gain setting in the index which will be modified during calibration.
        Use _restore_settings to write back the backed up settings to RAM.

        Args:
            dev (_type_): Device ID (e.g. rap0)
            pol (_type_): Polarization ('V' or 'H')
            gain_index (_type_): _description_
        """
        if pol.upper() == 'V':
            x = self._ram.rd(dev, 'rx_ram_v', gain_index)
        else:
            x = self._ram.rd(dev, 'rx_ram_h', gain_index)
        self._row_value = self._separate_value(x)
        for field in list(self.field_index):
            self._backup_row_value[field] = self._row_value[self.field_index[field]]

    def _restore_settings(self, dev, pol, gain_index):
        """Restores gain settings in the specified index in RAM which were previously backed up.

        Args:
            dev (_type_): Device ID (e.g. rap0)
            pol (_type_): Polarization ('V' or 'H')
            gain_index (_type_): _description_
        """
        if pol.upper() == 'V':
            x = self._ram.rd(dev, 'rx_ram_v', gain_index)
        else:
            x = self._ram.rd(dev, 'rx_ram_h', gain_index)
        self._row_value = self._separate_value(x)
        evk_logger.evk_logger.log_info('Changing RX gain to original settings:')
        evk_logger.evk_logger.log_info('--------------------------------------')
        exclude_fields = ['bbrx_i_dco_drv', 'bbrx_i_dco_filter', 'bbrx_i_dco_input', 'bbrx_q_dco_drv', 'bbrx_q_dco_filter', 'bbrx_q_dco_input', 'not_used']
        for field in list(self.field_index):
            if not field in exclude_fields:
                evk_logger.evk_logger.log_info('{:<19} {:>8} -> {:>5}'.format(field, hex(self._row_value[self.field_index[field]]), hex(self._backup_row_value[field])), indentation=4)
                self._row_value[self.field_index[field]] = self._backup_row_value[field]

        self._write_row(dev, pol, gain_index, self._row_value)
        evk_logger.evk_logger.log_info('')

    def _calibration_setting_stage_2(self, dev, pol, gain_index, bf_gain_lna=0, bf_gain_rx_vga=0, bf_att_com=0x1f, com_gain_rx_vga=0, bbrx_filter_gain=0, bbrx_iq_filter_gain=0, bbrx_iq_pga1_gain=0, bbrx_pga2_gain=2, bbrx_dco_input=0x40):
        row_data = self._read_row(dev, pol, gain_index)
        evk_logger.evk_logger.log_info('Changing RX gain settings before PGA2 stage calibration:')
        evk_logger.evk_logger.log_info('-----------------------------------------------------')
        evk_logger.evk_logger.log_info('bf_gain_lna         {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bf_gain_lna']]), hex(bf_gain_lna)), indentation=4)
        row_data[self.field_index['bf_gain_lna']] = bf_gain_lna
        evk_logger.evk_logger.log_info('bf_gain_rx_vga      {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bf_gain_rx_vga']]), hex(bf_gain_rx_vga)), indentation=4)
        row_data[self.field_index['bf_gain_rx_vga']] = bf_gain_rx_vga
        evk_logger.evk_logger.log_info('bf_att_com          {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bf_att_com']]), hex(bf_att_com)), indentation=4)
        row_data[self.field_index['bf_att_com']] = bf_att_com
        evk_logger.evk_logger.log_info('com_gain_rx_vga     {:>8} -> {:>5}'.format(hex(row_data[self.field_index['com_gain_rx_vga']]), hex(com_gain_rx_vga)), indentation=4)
        row_data[self.field_index['com_gain_rx_vga']] = com_gain_rx_vga
        evk_logger.evk_logger.log_info('bbrx_i_filter_gain  {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bbrx_i_filter_gain']]), hex(bbrx_filter_gain)), indentation=4)
        row_data[self.field_index['bbrx_i_filter_gain']] = bbrx_filter_gain
        evk_logger.evk_logger.log_info('bbrx_q_filter_gain  {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bbrx_q_filter_gain']]), hex(bbrx_filter_gain)), indentation=4)
        row_data[self.field_index['bbrx_q_filter_gain']] = bbrx_filter_gain
        evk_logger.evk_logger.log_info('bbrx_iq_filter_gain {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bbrx_iq_filter_gain']]), hex(bbrx_iq_filter_gain)), indentation=4)
        row_data[self.field_index['bbrx_iq_filter_gain']] = bbrx_iq_filter_gain
        evk_logger.evk_logger.log_info('bbrx_iq_pga1_gain   {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bbrx_iq_pga1_gain']]), hex(bbrx_iq_pga1_gain)), indentation=4)
        row_data[self.field_index['bbrx_iq_pga1_gain']] = bbrx_iq_pga1_gain
        evk_logger.evk_logger.log_info('bbrx_i_pga2_gain    {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bbrx_i_pga2_gain']]), hex(bbrx_pga2_gain)), indentation=4)
        row_data[self.field_index['bbrx_i_pga2_gain']] = bbrx_pga2_gain
        evk_logger.evk_logger.log_info('bbrx_q_pga2_gain    {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bbrx_q_pga2_gain']]), hex(bbrx_pga2_gain)), indentation=4)
        row_data[self.field_index['bbrx_q_pga2_gain']] = bbrx_pga2_gain

        evk_logger.evk_logger.log_info('bbrx_i_dco_input    {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bbrx_i_dco_input']]), hex(bbrx_dco_input)), indentation=4)
        row_data[self.field_index['bbrx_i_dco_input']] = bbrx_dco_input
        evk_logger.evk_logger.log_info('bbrx_q_dco_input    {:>8} -> {:>5}'.format(hex(row_data[self.field_index['bbrx_q_dco_input']]), hex(bbrx_dco_input)), indentation=4)
        row_data[self.field_index['bbrx_q_dco_input']] = bbrx_dco_input

        evk_logger.evk_logger.log_info('')

        row_compact = self._compact_value(row_data)
        if pol.upper() == 'V':
            self._ram.wr(dev, 'rx_ram_v', gain_index, row_compact)
            self._rx.gain(dev, gain_index, pol='RV')
        else:
            self._ram.wr(dev, 'rx_ram_h', gain_index, row_compact)
            self._rx.gain(dev, gain_index, pol='RH')

    def report(self, dev, pol, indentation=0, return_results=True, printit=True):

        ## Workaround for ADC issue
        amux_ctrl_cfg = self._spi.rd(dev, 'amux_ctrl_cfg')
        self._spi.clr(dev, 'amux_ctrl_cfg', 0x300000)

        bb_rx_config_dco_v_backup = self._spi.rd(dev, 'bb_rx_config_dco_v')
        bb_rx_config_dco_v = bb_rx_config_dco_v_backup
        bb_rx_config_dco_h_backup = self._spi.rd(dev, 'bb_rx_config_dco_h')
        bb_rx_config_dco_h = bb_rx_config_dco_h_backup
        if pol == 'V':
            bb_rx_config_dco_v = 0x0707
            self._spi.wr(dev, 'bb_rx_config_dco_v', bb_rx_config_dco_v)
        else:
            bb_rx_config_dco_h = 0x0707
            self._spi.wr(dev, 'bb_rx_config_dco_h', bb_rx_config_dco_h)
        self._adc.enable(dev)

        dco_i2_V = self._read_dco(dev, pol, 'I', 2)
        dco_q2_V = self._read_dco(dev, pol, 'Q', 2)
        dco_if_V = self._read_dco(dev, pol, 'I', 'F')
        dco_qf_V = self._read_dco(dev, pol, 'Q', 'F')
        dco_i1_V = self._read_dco(dev, pol, 'I', 1)
        dco_q1_V = self._read_dco(dev, pol, 'Q', 1)

        if pol == 'V':
            self._spi.wr(dev, 'bb_rx_config_dco_v', bb_rx_config_dco_v_backup)
        else:
            self._spi.wr(dev, 'bb_rx_config_dco_h', bb_rx_config_dco_h_backup)

        ## Workaround for ADC issue
        self._spi.wr(dev, 'amux_ctrl_cfg', amux_ctrl_cfg)

        if printit:
            evk_logger.evk_logger.log_info('{} DCO report - {} polarization:'.format(dev.get_name(), pol.upper()), indentation)
            evk_logger.evk_logger.log_info('--------------------------------', indentation)
            evk_logger.evk_logger.log_info('PGA2 I: {:{width}.{prec}f} mV'.format(dco_i2_V*1000, width=7, prec=2), indentation=indentation+4)
            evk_logger.evk_logger.log_info('PGA2 Q: {:{width}.{prec}f} mV'.format(dco_q2_V*1000, width=7, prec=2), indentation=indentation+4)
            evk_logger.evk_logger.log_info('FILTER I: {:{width}.{prec}f} mV'.format(dco_if_V*1000, width=7, prec=2), indentation=indentation+4)
            evk_logger.evk_logger.log_info('FILTER Q: {:{width}.{prec}f} mV'.format(dco_qf_V*1000, width=7, prec=2), indentation=indentation+4)
            evk_logger.evk_logger.log_info('PGA1 I: {:{width}.{prec}f} mV'.format(dco_i1_V*1000, width=7, prec=2), indentation=indentation+4)
            evk_logger.evk_logger.log_info('PGA1 Q: {:{width}.{prec}f} mV'.format(dco_q1_V*1000, width=7, prec=2), indentation=indentation+4)
            evk_logger.evk_logger.log_info('')
        if return_results:
            return {'dco_pga1_i':dco_i1_V, 'dco_pga1_q':dco_q1_V, 'dco_filter_i':dco_if_V, 'dco_filter_q':dco_qf_V, 'dco_pga2_i':dco_i2_V, 'dco_pga2_q':dco_q2_V}

    def _read_dco(self, dev, pol, chan, stage):
        """Reads and returns DC offset at the specified point.

        Args:
            dev (_type_): Device ID (e.g. rap0)
            pol (_type_): Polarization ('V' or 'H')
            chan (_type_): Channel ('I' or 'Q')
            stage (_type_): Stage ('1' for PGA1 or '2' for PGA2 or 'F' for FILTER)
        """
        data = self._adc.get_data(dev, self.amux_src[pol.upper()+chan.upper()+str(stage)], reps=ADC_REPS)
        return data

    def _read_row(self, dev, pol, gain_index):
        if pol.upper() == 'V':
            row = self._ram.rd(dev, 'rx_ram_v', gain_index)
        else:
            row = self._ram.rd(dev, 'rx_ram_h', gain_index)
        return self._separate_value(row)

    def _set_field(self, dev, pol, gain_index, field_name, value):
        # field_name should be bbrx_i_dco_drv, bbrx_q_dco_drv, bbrx_i_dco_input and bbrx_q_dco_input
        row_data = self._read_row(dev, pol, gain_index)
        row_data[self.field_index[field_name.lower()[:-2]]] = value
        row_compact = self._compact_value(row_data)
        if pol.upper() == 'V':
            self._ram.wr(dev, 'rx_ram_v', gain_index, row_compact)
            self._rx.gain(dev, gain_index, pol='RV')
        else:
            self._ram.wr(dev, 'rx_ram_h', gain_index, row_compact)
            self._rx.gain(dev, gain_index, pol='RH')

    def _calib(self, dev, pol, chan, stage, gain_index, meas_stage=2):
        START = 0
        MID = 1
        END = 2
        meas_retry = 3
        dco_reg  = [0,0,0]
        dco_diff = [0,0,0]
        sign = lambda x: x and (1, -1)[x < 0]
        if stage == 1:
            dco_reg[START] = 0
            dco_reg[END] = 0x7f
            bbrx_dco_drv = 'bbrx_' + chan.lower() + '_dco_input_' + pol.lower()
        elif stage == 2:
            dco_reg[START] = 0
            dco_reg[END] = 0x7f
            bbrx_dco_drv = 'bbrx_' + chan.lower() + '_dco_drv_' + pol.lower()
        else:
            dco_reg[START] = 0
            dco_reg[END] = 0x7f
            bbrx_dco_drv = 'bbrx_' + chan.lower() + '_dco_filter_' + pol.lower()

        average = (dco_reg[START] + dco_reg[END]) / 2
        dco_reg[MID] = int(round(average, 0))


        while (not dco_reg[START] == dco_reg[MID]) and (not dco_reg[END] == dco_reg[MID]):
            self._set_field(dev, pol, gain_index, bbrx_dco_drv, dco_reg[START])
            dco_diff[START] = self._read_dco(dev, pol, chan, meas_stage)
            self._set_field(dev, pol, gain_index, bbrx_dco_drv, dco_reg[MID])
            dco_diff[MID] = self._read_dco(dev, pol, chan, meas_stage)
            self._set_field(dev, pol, gain_index, bbrx_dco_drv, dco_reg[END])
            dco_diff[END] = self._read_dco(dev, pol, chan, meas_stage)
            if abs(dco_diff[START]) < abs(dco_diff[END]):
                dco_reg[END] = dco_reg[MID]
                self._set_field(dev, pol, gain_index, bbrx_dco_drv, dco_reg[END])
                dco_diff[END] = self._read_dco(dev, pol, chan, meas_stage)
            elif abs(dco_diff[END]) < abs(dco_diff[START]):
                dco_reg[START] = dco_reg[MID]
                self._set_field(dev, pol, gain_index, bbrx_dco_drv, dco_reg[START])
                dco_diff[START] = self._read_dco(dev, pol, chan, meas_stage)
            else:
                if sign(dco_diff[START]) != sign(dco_diff[END]):
                    if sign(dco_diff[START]) != sign(dco_diff[MID]):
                        dco_reg[END] = dco_reg[MID]
                        self._set_field(dev, pol, gain_index, bbrx_dco_drv, dco_reg[END])
                        dco_diff[END] = self._read_dco(dev, pol, chan, meas_stage)
                    elif sign(dco_diff[END]) != sign(dco_diff[MID]):
                        dco_reg[START] = dco_reg[MID]
                        self._set_field(dev, pol, gain_index, bbrx_dco_drv, dco_reg[START])
                        dco_diff[START] = self._read_dco(dev, pol, chan, meas_stage)
                else:
                    if meas_retry == 0:
                        # Calibration failure
                        evk_logger.evk_logger.log_error('RX DCO ({} {} {}) calibration failed'.format(pol, chan, stage))
                        return {bbrx_dco_drv:None, 'pga2_dco_'+bbrx_dco_drv:None}

            average = (dco_reg[START] + dco_reg[END]) / 2
            dco_reg[MID] = int(round(average, 0))
            self._set_field(dev, pol, gain_index, bbrx_dco_drv, dco_reg[MID])
            dco_diff[MID] = self._read_dco(dev, pol, chan, meas_stage)
            #print('dco_reg[MID]', dco_reg[MID])
            #print('dco_diff[MID]', dco_diff[MID])

            if dco_diff[START] == dco_diff[MID] == dco_diff[END]:
                self._set_field(dev, pol, gain_index, bbrx_dco_drv, dco_reg[START])
                return {bbrx_dco_drv:dco_reg[START], 'pga2_dco_'+bbrx_dco_drv:dco_diff[START]}

        self._backup_row_value[bbrx_dco_drv[:-2]] = dco_reg[MID]
        return {bbrx_dco_drv:dco_reg[MID], 'pga2_dco_'+bbrx_dco_drv:dco_diff[MID]}

    def calibrate(self, dev, pol, gain_index, return_results=True):
        """Calibrates RX DCO for the specified polarization and RX gain index.
        e.g.
        host.rx.dco.calibrate(rap0, 'V', 0)

        Args:
            dev (rapX):       Device ID (e.g. rap0)
            pol (str):        Polarization ('V' or 'H')
            gain_index (int): Gain index in RX RAM (0-63)
        """
        calib_res = {}

        ## Workaround for ADC issue
        amux_ctrl_cfg = self._spi.rd(dev, 'amux_ctrl_cfg')
        self._spi.clr(dev, 'amux_ctrl_cfg', 0x300000)

        # Back up current gain settings
        self._backup_settings(dev, pol, gain_index)

        bb_rx_config_dco_v = self._spi.rd(dev, 'bb_rx_config_dco_v')
        bb_rx_config_dco_h = self._spi.rd(dev, 'bb_rx_config_dco_h')

        if pol == 'V':
            bb_rx_config_dco_h_backup = bb_rx_config_dco_h
            #self._spi.wr(dev, 'bb_rx_config_dco_h', 0x0000)
            bb_rx_config_dco_v = 0x0707
            #bb_rx_config_dco_v = 0x5757
            self._spi.wr(dev, 'bb_rx_config_dco_v', bb_rx_config_dco_v)
        else:
            bb_rx_config_dco_v_backup = bb_rx_config_dco_v
            #self._spi.wr(dev, 'bb_rx_config_dco_v', 0x0000)
            bb_rx_config_dco_h = 0x0707
            #bb_rx_config_dco_h = 0x5757
            self._spi.wr(dev, 'bb_rx_config_dco_h', bb_rx_config_dco_h)

        self._adc.enable(dev)

        # Set all DACs to middle setting
        self._set_field(dev, pol, gain_index, 'bbrx_i_dco_input_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_q_dco_input_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_i_dco_filter_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_q_dco_filter_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_i_dco_drv_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_q_dco_drv_' + pol.lower(), 0x40)


        evk_logger.evk_logger.log_info('\nBefore DCO calibration')
        evk_logger.evk_logger.log_info('======================')
        self.report(dev, pol, indentation=4)

        # Change gain settings
        self._calibration_setting_stage_2(dev, pol, gain_index)
        evk_logger.evk_logger.log_info('\nRX DCO calibration starting:\n')

        res = self._calib(dev, pol.upper(), 'I', 2, gain_index)
        if not None in res.values():
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_i_dco_drv_'+pol.lower(), hex(res['bbrx_i_dco_drv_'+pol.lower()]), res['pga2_dco_bbrx_i_dco_drv_'+pol.lower()]*1000), indentation=4)
        else:
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_i_dco_drv_'+pol.lower(), None, None), indentation=4)
        calib_res.update(res)
        res = self._calib(dev, pol.upper(), 'Q', 2, gain_index)
        if not None in res.values():
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_q_dco_drv_'+pol.lower(), hex(res['bbrx_q_dco_drv_'+pol.lower()]), res['pga2_dco_bbrx_q_dco_drv_'+pol.lower()]*1000), indentation=4)
        else:
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_q_dco_drv_'+pol.lower(), None, None), indentation=4)
        calib_res.update(res)
        evk_logger.evk_logger.log_info('')

        self._restore_settings(dev, pol, gain_index)


        res = self._calib(dev, pol.upper(), 'I', 'F', gain_index)
        if not None in res.values():
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_i_dco_filter_'+pol.lower(), hex(res['bbrx_i_dco_filter_'+pol.lower()]), res['pga2_dco_bbrx_i_dco_filter_'+pol.lower()]*1000), indentation=4)
        else:
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_i_dco_filter_'+pol.lower(), None, None), indentation=4)
        calib_res.update(res)
        res = self._calib(dev, pol.upper(), 'Q', 'F', gain_index)
        if not None in res.values():
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_q_dco_filter_'+pol.lower(), hex(res['bbrx_q_dco_filter_'+pol.lower()]), res['pga2_dco_bbrx_q_dco_filter_'+pol.lower()]*1000), indentation=4)
        else:
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_q_dco_filter_'+pol.lower(), None, None), indentation=4)
        calib_res.update(res)
        evk_logger.evk_logger.log_info('')


        res = self._calib(dev, pol.upper(), 'I', 1, gain_index)
        if not None in res.values():
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_i_dco_input_'+pol.lower(), hex(res['bbrx_i_dco_input_'+pol.lower()]), res['pga2_dco_bbrx_i_dco_input_'+pol.lower()]*1000), indentation=4)
        else:
            evk_logger.evk_logger.log_error('{} -> {}  (DCO: {} mV) [FAIL]'.format('bbrx_i_dco_input_'+pol.lower(), None, None), indentation=4)
        calib_res.update(res)
        res = self._calib(dev, pol.upper(), 'Q', 1, gain_index)
        if not None in res.values():
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_q_dco_input_'+pol.lower(), hex(res['bbrx_q_dco_input_'+pol.lower()]), res['pga2_dco_bbrx_q_dco_input_'+pol.lower()]*1000), indentation=4)
        else:
            evk_logger.evk_logger.log_error('{} -> {}  (DCO: {} mV) [FAIL]'.format('bbrx_q_dco_input_'+pol.lower(), None, None), indentation=4)
        calib_res.update(res)
        evk_logger.evk_logger.log_info('\nRX DCO calibration complete.\n')
        evk_logger.evk_logger.log_info('After DCO calibration')
        evk_logger.evk_logger.log_info('=====================')
        self.report(dev, pol, indentation=4)

        if pol == 'V':
            self._spi.wr(dev, 'bb_rx_config_dco_h', bb_rx_config_dco_h_backup)
        else:
            self._spi.wr(dev, 'bb_rx_config_dco_v', bb_rx_config_dco_v_backup)

        ## Workaround for ADC issue
        self._spi.wr(dev, 'amux_ctrl_cfg', amux_ctrl_cfg)

        if return_results:
            return calib_res

    def calibrate_stage_1(self, dev, pol, gain_index, return_results=True):
        """Calibrates RX DCO for the specified polarization and RX gain index.
        e.g.
        host.rx.dco.calibrate(rap0, 'V', 0)

        Args:
            dev (rapX):       Device ID (e.g. rap0)
            pol (str):        Polarization ('V' or 'H')
            gain_index (int): Gain index in RX RAM (0-63)
        """
        calib_res = {}

        ## Workaround for ADC issue
        amux_ctrl_cfg = self._spi.rd(dev, 'amux_ctrl_cfg')
        self._spi.clr(dev, 'amux_ctrl_cfg', 0x300000)

        # Back up current gain settings
        self._backup_settings(dev, pol, gain_index)

        bb_rx_config_dco_v = self._spi.rd(dev, 'bb_rx_config_dco_v')
        bb_rx_config_dco_h = self._spi.rd(dev, 'bb_rx_config_dco_h')

        if pol == 'V':
            bb_rx_config_dco_h_backup = bb_rx_config_dco_h
            bb_rx_config_dco_v = 0x0707
            self._spi.wr(dev, 'bb_rx_config_dco_v', bb_rx_config_dco_v)
        else:
            bb_rx_config_dco_v_backup = bb_rx_config_dco_v
            bb_rx_config_dco_h = 0x0707
            self._spi.wr(dev, 'bb_rx_config_dco_h', bb_rx_config_dco_h)

        self._adc.enable(dev)

        # Set all DACs to middle setting
        self._set_field(dev, pol, gain_index, 'bbrx_i_dco_input_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_q_dco_input_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_i_dco_filter_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_q_dco_filter_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_i_dco_drv_' + pol.lower(), 0x40)
        self._set_field(dev, pol, gain_index, 'bbrx_q_dco_drv_' + pol.lower(), 0x40)


        evk_logger.evk_logger.log_info('\nBefore DCO calibration')
        evk_logger.evk_logger.log_info('======================')
        self.report(dev, pol, indentation=4)


        res = self._calib(dev, pol.upper(), 'I', 1, gain_index, meas_stage=1)
        if not None in res.values():
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_i_dco_input_'+pol.lower(), hex(res['bbrx_i_dco_input_'+pol.lower()]), res['pga2_dco_bbrx_i_dco_input_'+pol.lower()]*1000), indentation=4)
        else:
            evk_logger.evk_logger.log_error('{} -> {}  (DCO: {} mV) [FAIL]'.format('bbrx_i_dco_input_'+pol.lower(), None, None), indentation=4)
        calib_res.update(res)
        res = self._calib(dev, pol.upper(), 'Q', 1, gain_index, meas_stage=1)
        if not None in res.values():
            evk_logger.evk_logger.log_info('{} -> {}  (DCO: {} mV)'.format('bbrx_q_dco_input_'+pol.lower(), hex(res['bbrx_q_dco_input_'+pol.lower()]), res['pga2_dco_bbrx_q_dco_input_'+pol.lower()]*1000), indentation=4)
        else:
            evk_logger.evk_logger.log_error('{} -> {}  (DCO: {} mV) [FAIL]'.format('bbrx_q_dco_input_'+pol.lower(), None, None), indentation=4)
        calib_res.update(res)
        evk_logger.evk_logger.log_info('\nRX DCO calibration complete.\n')
        evk_logger.evk_logger.log_info('After DCO calibration')
        evk_logger.evk_logger.log_info('=====================')
        self.report(dev, pol, indentation=4)

        if pol == 'V':
            self._spi.wr(dev, 'bb_rx_config_dco_h', bb_rx_config_dco_h_backup)
        else:
            self._spi.wr(dev, 'bb_rx_config_dco_v', bb_rx_config_dco_v_backup)

        ## Workaround for ADC issue
        self._spi.wr(dev, 'amux_ctrl_cfg', amux_ctrl_cfg)

        if return_results:
            return calib_res