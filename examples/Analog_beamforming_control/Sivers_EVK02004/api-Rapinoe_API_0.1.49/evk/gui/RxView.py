import evk.gui.Page as p
import tkinter as tk
import tkinter.ttk as ttk

import evk.gui.Variables as var
import evk.gui.actions.rx_actions as rx_actions

class RxView():

    def __init__(self, parent, gui_handler, dev, main_view, *args, **kwargs):
        self.gui_handler = gui_handler
        self.host = gui_handler.host
        self.dev = dev
        self.parent = parent
        self.main_view = main_view
        self.label_frame = tk.LabelFrame(self.parent, relief=tk.GROOVE, text='RX')

        self.MAX_BEAM_INDEX = 255
        self.current_beam_index = 0
        self.current_beam_pol = 'TVTH'

        self.ra = rx_actions.RxActions(self.host)

        self._add_override_frame()
        self._add_setup_frame()
        self._add_gain_frame()
        self._add_beam_frame()
        self._add_calib_frame()

        self.label_frame.pack(expand=True, fill='both')

    def read_beam_index_field(self):
        try:
            index = int(self.beam_index.get())
        except:
            try:
                index = int(self.beam_index.get(),16)
            except:
                return None
        return index

    def _beam_set(self):
        style = ttk.Style()
        style.configure("Red.TCombobox", fieldbackground= "red")
        try:
            beam_index = int(self.beam_index_selector.get())
        except:
            try:
                beam_index = int(self.beam_index_selector.get(), 16)
            except:
                beam_index = None
                self.beam_index_selector.configure(style="Red.TCombobox")
                return

        beam_pol = self.beam_pol_selector.get()

        if not (beam_index >= 0 and beam_index <= self.MAX_BEAM_INDEX):
            beam_index = None
            self.beam_index_selector.configure(style="Red.TCombobox")

        if beam_index != None:
            self.beam_index_selector.configure(style="TCombobox")
            self.ra.beam(self.dev, beam_pol, beam_index)
            self.beam_set_button.configure(fg='green')

    def _gain_set(self):
        style = ttk.Style()
        style.configure("Red.TCombobox", fieldbackground= "red")
        try:
            gain_index = int(self.rfidx_selector.get())
        except:
            try:
                gain_index = int(self.rfidx_selector.get(), 16)
            except:
                gain_index = None
                self.rfidx_selector.configure(style="Red.TCombobox")
                return

        gain_pol = self.gain_pol_selector.get()

        if not (gain_index >= 0x00 and gain_index <= 63):
            gain_index = None
            self.rfidx_selector.configure(style="Red.TCombobox")

        if gain_index != None:
            self.rfidx_selector.configure(style="TCombobox")
            self.ra.rf_gain(self.dev, gain_pol, gain_index)
            self.gain_set_button.configure(fg='green')

    def setup_set(self):
        mode = self.selected_mode.get()
        pol = self.selected_polarization.get()
        latitude = 'WE'
        ant_en_v = int(self.selected_ant_en_v.get(), 16)
        ant_en_h = int(self.selected_ant_en_h.get(), 16)
        self.ra.setup(self.dev, mode, pol, latitude, ant_en_v, ant_en_h)
        self.setup_set_button.configure(fg='green')

    def _calibrate(self):
        style = ttk.Style()
        style.configure("Red.TCombobox", fieldbackground= "red")
        try:
            gain_index = int(self.selected_calib_gain_index.get())
        except:
            try:
                gain_index = int(self.selected_calib_gain_index.get(), 16)
            except:
                self.calib_gain_index_selector.configure(style='Red.TCombobox')
                gain_index = None
                return
        pol = self.selected_calib_pol.get()
        if pol == 'RV':
            pol = 'V'
        else:
            pol = 'H'
        self.ra.dco_calibrate(self.dev, pol, gain_index)
        self.calibrate_button.configure(fg='green')


    def _add_beam_frame(self):
        beam_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Beam', width=10)
        row_frame = [None]*4
        row_frame[0] = p.Page(beam_frame)
        row_frame[1] = p.Page(beam_frame)
        row_frame[2] = p.Page(beam_frame)
        row_frame[3] = p.Page(beam_frame)

        self.beam_index_label = tk.Label(row_frame[0], text='Index')
        self.beam_index_value_list = list(range(0,self.MAX_BEAM_INDEX+1))
        self.beam_index = tk.StringVar(value=self.beam_index_value_list[0])
        def on_beam_index_changed(beam_index):
            if beam_index.get() != str(self.set_beam_index['idx']):
                self.beam_set_button.configure(fg='red')
        self.beam_index.trace('w', lambda *_, beam_index=self.beam_index: on_beam_index_changed(beam_index))
        self.beam_index_selector = ttk.Combobox(row_frame[0], values=self.beam_index_value_list, width=10, textvariable=self.beam_index)

        self.beam_pol_label = tk.Label(row_frame[1], text='Polarization')
        self.beam_pol_value_list = ['RVRH', 'RH', 'RV']
        self.beam_pol = tk.StringVar(value=self.beam_pol_value_list[0])
        def on_beam_pol_changed(beam_pol):
            if beam_pol.get() != str(self.set_beam_index['pol']):
                self.beam_set_button.configure(fg='red')
        self.beam_pol.trace('w', lambda *_, beam_pol=self.beam_pol: on_beam_pol_changed(beam_pol))
        self.beam_pol_selector = ttk.Combobox(row_frame[1], values=self.beam_pol_value_list, width=10, state='readonly', textvariable=self.beam_pol)

        separator = ttk.Separator(row_frame[2], orient='horizontal')

        self.beam_set_button = tk.Button(row_frame[3], text='Set', command=self._beam_set)

        # Pack section

        self.beam_index_label.pack(side='left', padx=4, pady=4)
        self.beam_index_selector.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.beam_pol_label.pack(side='left', padx=4, pady=4)
        self.beam_pol_selector.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        self.beam_set_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        beam_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')

        self.set_beam_index = {'idx':None, 'pol':None}

    def _add_calib_frame(self):
        calib_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Calibrate DCO', width=10)
        row_frame = [None]*4
        row_frame[0] = p.Page(calib_frame)
        row_frame[1] = p.Page(calib_frame)
        row_frame[2] = p.Page(calib_frame)
        row_frame[3] = p.Page(calib_frame)

        self.calib_gain_index_label = tk.Label(row_frame[0], text='Gain index')
        calib_gain_index_value_list = list(range(64))
        self.selected_calib_gain_index = tk.StringVar(value=calib_gain_index_value_list[0])
        def on_calib_gain_index_changed(gain_index):
            if gain_index.get() != str(self.set_calib_setting['gain_idx']):
                self.calibrate_button.configure(fg='red')
        self.selected_calib_gain_index.trace('w', lambda *_, gain_index=self.selected_calib_gain_index: on_calib_gain_index_changed(gain_index))
        self.calib_gain_index_selector = ttk.Combobox(row_frame[0], values=calib_gain_index_value_list, width=10, textvariable=self.selected_calib_gain_index)

        self.calib_pol_label = tk.Label(row_frame[1], text='Polarization')
        calib_pol_value_list = ['RH', 'RV']
        self.selected_calib_pol = tk.StringVar(value=calib_pol_value_list[0])
        def on_calib_pol_changed(pol):
            if pol.get() != str(self.set_calib_setting['rx_pol']):
                self.calibrate_button.configure(fg='red')
        self.selected_calib_pol.trace('w', lambda *_, pol=self.selected_calib_pol: on_calib_pol_changed(pol))
        self.calib_pol_selector = ttk.Combobox(row_frame[1], values=calib_pol_value_list, width=10, state='readonly', textvariable=self.selected_calib_pol)

        separator = ttk.Separator(row_frame[2], orient='horizontal')

        self.calibrate_button = tk.Button(row_frame[3], text='Calibrate', command=lambda:self._calibrate())

        # Pack section

        self.calib_gain_index_label.pack(side='left', padx=4, pady=4)
        self.calib_gain_index_selector.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.calib_pol_label.pack(side='left', padx=4, pady=4)
        self.calib_pol_selector.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        self.calibrate_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        calib_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')

        self.set_calib_setting = {'rx_pol':None, 'gain_idx':None}


    def _add_gain_frame(self):
        gain_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Gain', width=10)
        row_frame = [None]*4
        row_frame[0] = p.Page(gain_frame)
        row_frame[1] = p.Page(gain_frame)
        row_frame[2] = p.Page(gain_frame)
        row_frame[3] = p.Page(gain_frame)

        self.rfidx_label = tk.Label(row_frame[0], text='RF index')
        self.rfidx_value_list = list(range(64))
        self.selected_rfidx = tk.StringVar(value=self.rfidx_value_list[0])
        def on_rfidx_changed(rfidx):
            if rfidx.get() != str(self.set_rf_gain['idx']):
                self.gain_set_button.configure(fg='red')
        self.selected_rfidx.trace('w', lambda *_, rfidx=self.selected_rfidx: on_rfidx_changed(rfidx))
        self.rfidx_selector = ttk.Combobox(row_frame[0], values=self.rfidx_value_list, width=10, textvariable=self.selected_rfidx)

        self.gain_pol_label = tk.Label(row_frame[1], text='Polarization')
        self.gain_pol_value_list = ['RVRH', 'RH', 'RV']
        self.selected_gain_pol = tk.StringVar(value=self.gain_pol_value_list[0])
        def on_gain_pol_changed(gain_pol):
            if gain_pol.get() != str(self.set_rf_gain['pol']):
                self.gain_set_button.configure(fg='red')
        self.selected_gain_pol.trace('w', lambda *_, gain_pol=self.selected_gain_pol: on_gain_pol_changed(gain_pol))
        self.gain_pol_selector = ttk.Combobox(row_frame[1], values=self.gain_pol_value_list, width=10, textvariable=self.selected_gain_pol, state='readonly')

        separator = ttk.Separator(row_frame[2], orient='horizontal')

        self.gain_set_button = tk.Button(row_frame[3], text='Set', command=self._gain_set)

        # Pack section
        self.rfidx_label.pack(side='left', padx=4, pady=4)
        self.rfidx_selector.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.gain_pol_label.pack(side='left', padx=4, pady=4)
        self.gain_pol_selector.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        self.gain_set_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        gain_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')
        self.set_rf_gain = {'idx':None, 'pol':None}

    def _add_override_frame(self):
        override_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Override', width=10)
        row_frame = [None]*4
        row_frame[0] = p.Page(override_frame)

        self.override_label = tk.Label(row_frame[0], text='')
        override_value_list = ['On','Off']
        self.selected_override = tk.StringVar(value=override_value_list[0])
        def on_selected_override_changed(override):
            self.ra.override(self.dev, override.get())
        self.selected_override.trace('w', lambda *_, override=self.selected_override: on_selected_override_changed(override))
        self.override_selector = ttk.Combobox(row_frame[0], values=override_value_list, state='readonly', width=10, textvariable=self.selected_override)

        self.override_label.pack(side='left', padx=4, pady=4)
        self.override_selector.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        override_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')

    def _add_setup_frame(self):
        setup_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Setup', width=10)
        row_frame = [None]*6
        row_frame[0] = p.Page(setup_frame)
        row_frame[1] = p.Page(setup_frame)
        row_frame[2] = p.Page(setup_frame)
        row_frame[3] = p.Page(setup_frame)
        row_frame[4] = p.Page(setup_frame)
        row_frame[5] = p.Page(setup_frame)

        #self.setup_label_frame = tk.LabelFrame(setup_frame, text='Setup')

        self.mode_label = tk.Label(row_frame[0], text='Mode')
        self.mode_value_list = ['IF','BB']
        self.selected_mode = tk.StringVar(value=self.mode_value_list[0])
        def on_mode_changed(mode):
            if mode.get() != str(self.set_setup['mode']):
                self.setup_set_button.configure(fg='red')
        self.selected_mode.trace('w', lambda *_, mode=self.selected_mode: on_mode_changed(mode))
        self.mode_selector = ttk.Combobox(row_frame[0], values=self.mode_value_list, state='readonly', width=10, textvariable=self.selected_mode)

        self.polarization_label = tk.Label(row_frame[1], text='Polarization')
        self.polarization_value_list = ['RVRH', 'RH', 'RV']
        self.selected_polarization = tk.StringVar(value=self.polarization_value_list[0])
        def on_pol_changed(pol):
            if pol.get() != str(self.set_setup['pol']):
                self.setup_set_button.configure(fg='red')
        self.selected_polarization.trace('w', lambda *_, pol=self.selected_polarization: on_pol_changed(pol))
        self.polarization_selector = ttk.Combobox(row_frame[1], values=self.polarization_value_list, state='readonly', width=10, textvariable=self.selected_polarization)

        self.ant_en_v_label = tk.Label(row_frame[2], text='ANT_EN_V')
        self.ant_en_value_list = ['0x0000', '0x0100', '0x0180', '0x0380', '0x03c0', '0x07c0', '0x07e0', '0x0fe0', '0x0ff0', '0x1ff0', '0x1ff8', '0x3ff8', '0x3ffc', '0x7ffc', '0x7ffe', '0xfffe', '0xffff']
        self.selected_ant_en_v = tk.StringVar(value=self.ant_en_value_list[16])
        def on_ant_en_v_changed(ant_en_v):
            if ant_en_v.get() != str(self.set_setup['ant_en_v']):
                self.setup_set_button.configure(fg='red')
        self.selected_ant_en_v.trace('w', lambda *_, ant_en_v=self.selected_ant_en_v: on_ant_en_v_changed(ant_en_v))
        self.ant_en_v_selector = ttk.Combobox(row_frame[2], values=self.ant_en_value_list, width=10, textvariable=self.selected_ant_en_v)

        self.ant_en_h_label = tk.Label(row_frame[3], text='ANT_EN_H')
        self.selected_ant_en_h = tk.StringVar(value=self.ant_en_value_list[16])
        def on_ant_en_h_changed(ant_en_h):
            if ant_en_h.get() != str(self.set_setup['ant_en_h']):
                self.setup_set_button.configure(fg='red')
        self.selected_ant_en_h.trace('w', lambda *_, ant_en_h=self.selected_ant_en_h: on_ant_en_h_changed(ant_en_h))
        self.ant_en_h_selector = ttk.Combobox(row_frame[3], values=self.ant_en_value_list, width=10, textvariable=self.selected_ant_en_h)

        separator = ttk.Separator(row_frame[4], orient='horizontal')

        self.setup_set_button = tk.Button(row_frame[5], text='Set', command=self.setup_set)

        # Pack section

        self.mode_label.pack(side='left', padx=4, pady=4)
        self.mode_selector.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.polarization_label.pack(side='left', padx=4, pady=4)
        self.polarization_selector.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        self.ant_en_v_label.pack(side='left', padx=4, pady=4)
        self.ant_en_v_selector.pack(side='right', padx=4, pady=4)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        self.ant_en_h_label.pack(side='left', padx=4, pady=4)
        self.ant_en_h_selector.pack(side='right', padx=4, pady=4)
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[4].pack(side = 'top', expand = True, fill = 'both')

        self.setup_set_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[5].pack(side = 'top', expand = True, fill = 'both')

        setup_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')

        self.set_setup = {'mode':None, 'pol':None, 'lat':None, 'ant_en_v':None, 'ant_en_h':None}


    def _add_first_row_buttons(self):
        # Add two buttons
        row_page = p.Page(self.label_frame)
        button0 = tk.Button(row_page, text='Setup0')
        button1 = tk.Button(row_page, text='Setup1')

        button0.pack(expand=False, fill='none', side='left', padx=4)
        button1.pack(expand=False, fill='none', side='left', padx=4)
        row_page.pack(side ='left', expand=True, fill='y')

    def _add_second_row_buttons(self):
        # Add two buttons
        row_page = p.Page(self.label_frame)
        button0 = tk.Button(row_page, text='Setup0')
        button1 = tk.Button(row_page, text='Setup1')

        button0.pack(expand=False, fill='none', side='left', padx=4)
        button1.pack(expand=False, fill='none', side='left', padx=4)
        row_page.pack(side ='left', expand=True, fill='y')

    def reset(self):
        self.set_setup = {'mode':None, 'pol':None, 'lat':None, 'ant_en_v':None, 'ant_en_h':None}
        self.setup_set_button.configure(fg='black')
        self.gain_set_button.configure(fg='black')
        self.beam_set_button.configure(fg='black')
        self.calibrate_button.configure(fg='black')
        self.override_selector.current(0)
