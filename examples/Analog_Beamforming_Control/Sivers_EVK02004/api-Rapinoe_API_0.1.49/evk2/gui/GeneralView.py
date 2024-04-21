import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import Variables as var

import actions.synth_actions as synth_actions
import actions.general_actions as general_actions


class GeneralView():

    def __init__(self, parent, gui_data, dev, main_frame, *args, **kwargs):
        self.gui_data = gui_data
        self.dev = dev
        self.parent = parent
        self.main_frame = main_frame
        self.label_frame = tk.LabelFrame(self.parent, relief=tk.GROOVE, text='General')

        self.ga = general_actions.GeneralActions(self.gui_data)
        self.sa = synth_actions.SynthActions(self.gui_data)
        self._add_reset_frame()
        try:
            s = self.ga.pwr_status()
            pow_exists = True
        except:
            pow_exists = False
        if pow_exists:
            self._add_power_frame()

        try:
            s = self.ga.misc_status()
            misc_exists = True
        except:
            misc_exists = False
        if misc_exists:
            self._add_misc_frame()

        self._add_init_frame()
        self._add_synth_frame()
        self._add_state_frame()

        self.label_frame.pack(expand=True, fill='both')

    def _add_reset_frame(self):
        reset_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Reset', width=10)
        row_frame = [None]*1
        row_frame[0] = p.Page(reset_frame)

        self.reset_button = tk.Button(row_frame[0], text='Reset', command=self._reset_action)

        # Pack section

        self.reset_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        reset_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')

    def _add_power_frame(self):
        power_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Power', width=10)
        row_frame = [None]*4
        row_frame[0] = p.Page(power_frame)
        row_frame[1] = p.Page(power_frame)
        row_frame[2] = p.Page(power_frame)
        row_frame[3] = p.Page(power_frame)

        self.pwr_button = {}

        self.pwr_button['VDD1V8'] = tk.Button(row_frame[0], text='VDD1V8', command=lambda: self._pwr('VDD1V8'), width=10)
        self.pwr_button['VCC3V3_A1'] = tk.Button(row_frame[1], text='VCC3V3_A1', command=lambda: self._pwr('VCC3V3_A1'), width=10)
        self.pwr_button['VCC3V3_A2'] = tk.Button(row_frame[1], text='VCC3V3_A2', command=lambda: self._pwr('VCC3V3_A2'), width=10)
        self.pwr_button['VCC3V3_B1'] = tk.Button(row_frame[2], text='VCC3V3_B1', command=lambda: self._pwr('VCC3V3_B1'), width=10)
        self.pwr_button['VCC3V3_B2'] = tk.Button(row_frame[2], text='VCC3V3_B2', command=lambda: self._pwr('VCC3V3_B2'), width=10)
        self.pwr_button['VCC3V3_SYNTH_A'] = tk.Button(row_frame[3], text='VCC3V3_SYNTH_A', command=lambda: self._pwr('VCC3V3_SYNTH_A'), width=14)
        self.pwr_button['VCC3V3_SYNTH_B'] = tk.Button(row_frame[3], text='VCC3V3_SYNTH_B', command=lambda: self._pwr('VCC3V3_SYNTH_B'), width=14)

        self.pwr_button['VDD1V8'].pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.pwr_button['VCC3V3_A1'].pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.pwr_button['VCC3V3_A2'].pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.pwr_button['VCC3V3_B1'].pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.pwr_button['VCC3V3_B2'].pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.pwr_button['VCC3V3_SYNTH_A'].pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.pwr_button['VCC3V3_SYNTH_B'].pack(side='left', padx=4, pady=4, expand = True, fill = 'both')

        row_frame[0].pack(side = 'top', expand = True, fill = 'both')
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        power_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')
        self._update_pwr_button_status()

    def _add_misc_frame(self):
        misc_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Misc.', width=10)
        row_frame = [None]*1
        row_frame[0] = p.Page(misc_frame)

        self.misc_button = {}

        self.misc_button['VCXO'] = tk.Button(row_frame[0], text='VCXO', command=lambda: self._misc('VCXO'), width=10)
        self.misc_button['PLL'] = tk.Button(row_frame[0], text='PLL', command=lambda: self._misc('PLL'), width=10)

        self.misc_button['VCXO'].pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.misc_button['PLL'].pack(side='left', padx=4, pady=4, expand = True, fill = 'both')

        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        misc_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')
        self._update_misc_button_status()


    def _add_state_frame(self):
        state_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='State', width=10)
        row_frame = [None]*4
        row_frame[0] = p.Page(state_frame)
        row_frame[1] = p.Page(state_frame)
        row_frame[2] = p.Page(state_frame)
        row_frame[3] = p.Page(state_frame)

        self.h_state_label = tk.Label(row_frame[0], text='H')
        self.h_state_value_list = ['None', 'TX', 'RX', 'SLEEP', 'SX']
        self.selected_h_state = tk.StringVar(value=self.h_state_value_list[0])
        def on_h_state_changed(h_state):
            if h_state.get() != str(self.set_state['h']):
                self.state_set_button.configure(fg='red')
        self.selected_h_state.trace('w', lambda *_, h_state=self.selected_h_state: on_h_state_changed(h_state))
        self.h_state_selector = ttk.Combobox(row_frame[0], values=self.h_state_value_list, state='readonly', width=10, textvariable=self.selected_h_state)
        self.h_state_selector.bind('<<ComboboxSelected>>', self.h_state_selected)

        self.v_state_label = tk.Label(row_frame[1], text='V')
        self.v_state_value_list = ['None', 'TX', 'RX', 'SLEEP', 'SX']
        self.selected_v_state = tk.StringVar(value=self.v_state_value_list[0])
        def on_v_state_changed(v_state):
            if v_state.get() != str(self.set_state['v']):
                self.state_set_button.configure(fg='red')
        self.selected_v_state.trace('w', lambda *_, v_state=self.selected_v_state: on_v_state_changed(v_state))
        self.v_state_selector = ttk.Combobox(row_frame[1], values=self.v_state_value_list, state='readonly', width=10, textvariable=self.selected_v_state)
        self.v_state_selector.bind('<<ComboboxSelected>>', self.v_state_selected)

        separator = ttk.Separator(row_frame[2], orient='horizontal')

        self.state_set_button = tk.Button(row_frame[3], text='Set', command=self._state_set)

        self.h_state_label.pack(side='left', padx=4, pady=4)
        self.h_state_selector.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.v_state_label.pack(side='left', padx=4, pady=4)
        self.v_state_selector.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        self.state_set_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')


        state_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')

        self.set_state = {'h':None, 'v':None}

    def v_state_selected(self, event):
        if self.selected_v_state.get() == 'SX' or self.selected_v_state.get() == 'SLEEP':
            self.selected_h_state.set(self.selected_v_state.get())
        else:
            if self.selected_h_state.get() == 'SX' or self.selected_h_state.get() == 'SLEEP':
                self.selected_h_state.set(self.selected_v_state.get())

    def h_state_selected(self, event):
        if self.selected_h_state.get() == 'SX' or self.selected_h_state.get() == 'SLEEP':
            self.selected_v_state.set(self.selected_h_state.get())
        else:
            if self.selected_v_state.get() == 'SX' or self.selected_v_state.get() == 'SLEEP':
                self.selected_v_state.set(self.selected_h_state.get())


    def _add_init_frame(self):
        init_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Init', width=10)
        row_frame = [None]*3
        row_frame[0] = p.Page(init_frame)
        row_frame[1] = p.Page(init_frame)
        row_frame[2] = p.Page(init_frame)

        self.init_chip_button = tk.Button(row_frame[0], text='Chip', command=lambda: self._init('CHIP'), width=10)
        self.init_synth_button = tk.Button(row_frame[0], text='Synth', command=lambda: self._init('SYNTH'), width=10)
        self.init_adc_button = tk.Button(row_frame[1], text='ADC', command=lambda: self._init('ADC'), width=10)
        self.init_val_button = tk.Button(row_frame[1], text='VAL.', command=lambda: self._init('VALIDATION'), width=10)
        self.init_tx_button = tk.Button(row_frame[2], text='TX', command=lambda: self._init('TX'), width=10)
        self.init_rx_button = tk.Button(row_frame[2], text='RX', command=lambda: self._init('RX'), width=10)

        self.init_chip_button.pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.init_synth_button.pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.init_adc_button.pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.init_val_button.pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.init_tx_button.pack(side='left', padx=4, pady=4, expand = True, fill = 'both')
        self.init_rx_button.pack(side='left', padx=4, pady=4, expand = True, fill = 'both')

        row_frame[0].pack(side = 'top', expand = True, fill = 'both')
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        init_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')


    def _reset_action(self):
        self.ga.reset()
        self.actual_rf_freq.set('')
        self.selected_h_state.set('None')
        self.selected_v_state.set('None')
        self._reset_button_colors()

    def _state_set(self):
        if self.selected_h_state.get() == 'TX':
            state = 'TH'
        elif self.selected_h_state.get() == 'RX':
            state = 'RH'
        elif self.selected_h_state.get() == 'None':
            state = ''
        elif self.selected_h_state.get() == 'SLEEP':
            state = 'SLEEP'
        elif self.selected_h_state.get() == 'SX':
            state = 'SX'

        if self.selected_v_state.get() == 'TX':
            state = state + 'TV'
        elif self.selected_v_state.get() == 'RX':
            state = state + 'RV'
        elif self.selected_v_state.get() == 'None':
            state = state + ''
        elif self.selected_v_state.get() == 'SLEEP':
            state = 'SLEEP'
        elif self.selected_v_state.get() == 'SX':
            state = 'SX'

        if not state == '':
            self.ga.state_set(state)
            self.state_set_button.configure(fg='green')
    def _init(self, block):
        self.ga.init(block)
        if block == 'CHIP':
            self.init_chip_button.configure(fg='green')
        elif block == 'SYNTH':
            self.init_synth_button.configure(fg='green')
        elif block == 'ADC':
            self.init_adc_button.configure(fg='green')
        elif block == 'VALIDATION':
            self.init_val_button.configure(fg='green')
        elif block == 'TX':
            self.init_tx_button.configure(fg='green')
        elif block == 'RX':
            self.init_rx_button.configure(fg='green')

    def _update_pwr_button_status(self):
        status = self.ga.pwr_status()
        for key in status.keys():
            try:
                if status[key]:
                    self.pwr_button[key].configure(fg='green')
                else:
                    self.pwr_button[key].configure(fg='red')
            except:
                pass

    def _update_misc_button_status(self):
        status = self.ga.misc_status()
        for key in status.keys():
            try:
                if status[key]:
                    self.misc_button[key].configure(fg='green')
                else:
                    self.misc_button[key].configure(fg='red')
            except:
                pass

    def _pwr(self, port):
        status = self.ga.pwr_status(port)
        if status:
            status = self.ga.pwr_off(port)
        else:
            status = self.ga.pwr_on(port)
        if status:
            self.pwr_button[port].configure(fg='green')
        else:
            self.pwr_button[port].configure(fg='red')

    def _misc(self, port):
        status = self.ga.misc_status(port)
        print(status)
        if status:
            status = self.ga.misc_off(port)
        else:
            status = self.ga.misc_on(port)
        if status:
            self.misc_button[port].configure(fg='green')
        else:
            self.misc_button[port].configure(fg='red')

    def _add_synth_frame(self):
        setup_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Synth', width=10)
        row_frame = [None]*7
        row_frame[0] = p.Page(setup_frame)
        row_frame[1] = p.Page(setup_frame)
        row_frame[2] = p.Page(setup_frame)
        row_frame[3] = p.Page(setup_frame)
        row_frame[4] = p.Page(setup_frame)
        row_frame[5] = p.Page(setup_frame)
        row_frame[6] = p.Page(setup_frame)

        self.set_synth_setting = {'freq_rff':None, 'frac_mode':None, 'sd_order':None}

        self.ref_freq_label = tk.Label(row_frame[0], text='Ref. clk. Freq. [Hz]')
        self.ref_freq = tk.StringVar(value='245760000')
        self.ref_freq_entry = ttk.Entry(row_frame[0], width=12, textvariable=self.ref_freq, state= "readonly", justify='right')

        self.rf_freq_label = tk.Label(row_frame[1], text='Target RF Freq. [Hz]')
        self.rf_freq = tk.StringVar(value='26000000000')
        def on_rf_freq_changed(rf_freq):
            if rf_freq.get() != str(self.set_synth_setting['freq_rff']):
                self.setup_set_button.configure(fg='red')
            # else:
            #     if self.set_synth_setting['freq_rff'] == None:
            #         self.setup_set_button.configure(fg='black')
            #     else:
            #         self.setup_set_button.configure(fg='green')
        self.rf_freq.trace('w', lambda *_, rf_freq=self.rf_freq: on_rf_freq_changed(rf_freq))
        self.rf_freq_entry = ttk.Entry(row_frame[1], width=12, textvariable=self.rf_freq, justify='right')

        self.fractional_label = tk.Label(row_frame[2], text='Fractional')
        self.fractional_value_list = ['Yes', 'No']
        self.selected_fractional = tk.StringVar(value=self.fractional_value_list[0])
        def on_frac_mode_changed(frac_mode):
            if frac_mode.get() == 'No':
                fractional = False
            else:
                fractional = True
            if fractional != self.set_synth_setting['frac_mode']:
                self.setup_set_button.configure(fg='red')
            # else:
            #     if self.set_synth_setting['frac_mode'] == None:
            #         self.setup_set_button.configure(fg='black')
            #     else:
            #         self.setup_set_button.configure(fg='green')
        self.selected_fractional.trace('w', lambda *_, frac_mode=self.selected_fractional: on_frac_mode_changed(frac_mode))
        self.fractional_selector = ttk.Combobox(row_frame[2], values=self.fractional_value_list, state='readonly', width=10, textvariable=self.selected_fractional)

        self.sd_order_label = tk.Label(row_frame[3], text='SD order')
        self.sd_order_value_list = ['1','2', '3']
        self.selected_sd_order = tk.StringVar(value=self.sd_order_value_list[1])
        def on_sd_order_changed(sd_order):
            if sd_order.get() != self.set_synth_setting['sd_order']:
                self.setup_set_button.configure(fg='red')
        self.selected_sd_order.trace('w', lambda *_, sd_order=self.selected_sd_order: on_sd_order_changed(sd_order))
        self.sd_order_selector = ttk.Combobox(row_frame[3], values=self.sd_order_value_list, state='readonly', width=10, textvariable=self.selected_sd_order)

        #self.dithering_label = tk.Label(row_frame[3], text='Dithering')
        #self.dithering_value_list = ['1','2', '3']
        #self.selected_dithering = tk.StringVar(value=self.dithering_value_list[2])
        #self.dithering_selector = ttk.Combobox(row_frame[3], values=self.dithering_value_list, state='readonly', width=10, textvariable=self.selected_dithering)

        self.actual_rf_freq_label = tk.Label(row_frame[4], text='Actual RF Freq. [Hz]')
        self.actual_rf_freq = tk.StringVar(value='')
        self.actual_rf_freq_entry = ttk.Entry(row_frame[4], width=12, textvariable=self.actual_rf_freq, state= "readonly", justify='right')

        separator = ttk.Separator(row_frame[5], orient='horizontal')

        self.setup_set_button = tk.Button(row_frame[6], text='Set', command=self.setup_set)

        # Pack section

        self.ref_freq_label.pack(side='left', padx=4, pady=4)
        self.ref_freq_entry.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.rf_freq_label.pack(side='left', padx=4, pady=4)
        self.rf_freq_entry.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        self.fractional_label.pack(side='left', padx=4, pady=4)
        self.fractional_selector.pack(side='right', padx=4, pady=4)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        self.sd_order_label.pack(side='left', padx=4, pady=4)
        self.sd_order_selector.pack(side='right', padx=4, pady=4)
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        #self.dithering_label.pack(side='left', padx=4, pady=4)
        #self.dithering_selector.pack(side='right', padx=4, pady=4)
        #row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        self.actual_rf_freq_label.pack(side='left', padx=4, pady=4)
        self.actual_rf_freq_entry.pack(side='right', padx=4, pady=4)
        row_frame[4].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[5].pack(side = 'top', expand = True, fill = 'both')

        self.setup_set_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[6].pack(side = 'top', expand = True, fill = 'both')

        setup_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')

    def setup_set(self):
        try:
            freq_rff = int(self.rf_freq.get())
        except:
            try:
                freq_rff = float(self.rf_freq.get())
                freq_rff = int(freq_rff)
            except:
                return
        if self.selected_fractional.get() == 'Yes':
            frac_mode = True
        else:
            frac_mode = False

        sd_order = int(self.selected_sd_order.get())

        vcxo_freq = self.sa.setup_set(freq_rff, frac_mode, sd_order)
        print('vcxo_freq: ', vcxo_freq)
        self.ref_freq.set(round(vcxo_freq, 2))

        actual_rf_freq = self.sa.get_rf_freq()
        self.actual_rf_freq.set(actual_rf_freq)

        self.set_synth_setting = {'freq_rff':freq_rff, 'frac_mode':frac_mode, 'sd_order':sd_order}
        self.setup_set_button.configure(fg='green')

    def _reset_button_colors(self):
        self.init_chip_button.configure(fg='black')
        self.init_synth_button.configure(fg='black')
        self.init_adc_button.configure(fg='black')
        self.init_val_button.configure(fg='black')
        self.init_tx_button.configure(fg='black')
        self.init_rx_button.configure(fg='black')
        self.state_set_button.configure(fg='black')
        self.setup_set_button.configure(fg='black')
        self.set_synth_setting = {'freq_rff':None, 'frac_mode':None, 'sd_order':None}
        self.main_frame.reset()

