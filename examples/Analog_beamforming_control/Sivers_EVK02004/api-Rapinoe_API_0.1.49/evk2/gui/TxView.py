from time import time
from common import fhex
import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import Variables as var

import actions.tx_actions as tx_actions

class TxView():

    def __init__(self, parent, gui_data, dev, main_view, *args, **kwargs):
        self.gui_data = gui_data
        self.dev = dev
        self.parent = parent
        self.main_view = main_view
        self.label_frame = tk.LabelFrame(self.parent, relief=tk.GROOVE, text='TX')

        self.MAX_BEAM_INDEX = 255
        self.current_beam_index = 0
        self.current_beam_pol = 'TVTH'

        self._add_override_frame()
        self._add_setup_frame()
        self._add_bb_gain_frame()
        self._add_rf_gain_frame()
        self._add_beam_frame()
        self._add_calib_frame()

        self.label_frame.pack(expand=True, fill='both')

        self.ta = tx_actions.TxActions(self.gui_data)

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
            beam_index = int(self.selected_beam_index.get())
        except:
            try:
                beam_index = int(self.selected_beam_index.get(), 16)
            except:
                beam_index = None
                self.beam_index_selector.configure(style='Red.TCombobox')
                return

        if beam_index == None or (not (beam_index >= 0 and beam_index <= self.MAX_BEAM_INDEX)):
            self.beam_index_selector.configure(style='Red.TCombobox')
            return
        self.beam_index_selector.configure(style='TCombobox')

        pol = self.selected_beam_pol.get()
        self.ta.beam(pol, beam_index)
        self.beam_set_button.configure(fg='green')

    def _rf_gain_set(self):
        style = ttk.Style()
        style.configure("Red.TCombobox", fieldbackground= "red")
        try:
            rf_gain_index = int(self.selected_rfidx.get())
        except:
            try:
                rf_gain_index = int(self.selected_rfidx.get(), 16)
            except:
                rf_gain_index = None
                self.rfidx_selector.configure(style="Red.TCombobox")
                return

        gain_pol = self.selected_gain_pol.get()

        if not (rf_gain_index >= 0x00 and rf_gain_index <= 63):
            rf_gain_index = None
            self.rfidx_selector.configure(style="Red.TCombobox")
            return

        if rf_gain_index != None:
            self.rfidx_selector.configure(style="TCombobox")
            self.ta.rf_gain(gain_pol, rf_gain_index)
            self.rf_gain_set_button.configure(fg='green')

    def _bb_gain_set(self):
        style = ttk.Style()
        style.configure("Red.TCombobox", fieldbackground= "red")
        try:
            bb_v = int(self.selected_bbv.get())
        except:
            try:
                bb_v = int(self.selected_bbv.get(), 16)
            except:
                bb_v = None
                self.bbv_selector.configure(style='Red.TCombobox')
        try:
            bb_h = int(self.selected_bbh.get())
        except:
            try:
                bb_h = int(self.selected_bbh.get(), 16)
            except:
                bb_h = None
                self.bbh_selector.configure(style='Red.TCombobox')

        if not (bb_h >= 0x00 and bb_h <= 0x1f):
            bb_h = None
            self.bbh_selector.configure(style='Red.TCombobox')

        if not (bb_v >= 0x00 and bb_v <= 0x1f):
            bb_v = None
            self.bbv_selector.configure(style='Red.TCombobox')

        if bb_v != None and bb_h != None:
            self.bbh_selector.configure(style='TCombobox')
            self.bbv_selector.configure(style='TCombobox')
            self.ta.bb_gain(bb_v, bb_h)
            self.bb_gain_set_button.configure(fg='green')


    def setup_set(self):
        mode = self.selected_mode.get()
        pol = self.selected_polarization.get()
        latitude = 'WE'
        ant_en_v = int(self.selected_ant_en_v.get(), 16)
        ant_en_h = int(self.selected_ant_en_h.get(), 16)
        self.ta.setup(mode, pol, latitude, ant_en_v, ant_en_h)
        self.setup_set_button.configure(fg='green')

    def busy_detect(self):
        if self.main_view.busy:
            self.main_view.parent.wm_attributes('-disabled', 'True')
            self.main_view.parent.after(2000, lambda: self.busy_detect())
        else:
            self.main_view.parent.wm_attributes('-disabled', 'False')

    def _calibrate(self):
        style = ttk.Style()
        style.configure("Red.TCombobox", fieldbackground= "red")
        mode = self.selected_mode.get()
        tx_pol = self.selected_calib_pol.get()
        cross_pol = self.selected_cross_pol_calib.get()
        # a = lambda : self.main_view.set_busy(True)
        # b = lambda : self.ta.dco_calibrate(self.dev, mode, tx_pol, cross_pol)
        # c = lambda : self.main_view.set_busy(False)
        # print (a)
        # print (b)
        # print (c)
        self.main_view.TH.put(lambda : self.main_view.set_busy(True))
        self.main_view.TH.put(lambda : self.ta.dco_calibrate(mode, tx_pol, cross_pol))
        self.main_view.TH.put(lambda : self.main_view.set_busy(False))
        self.main_view.parent.after(1000, lambda: self.busy_detect())
        self.calibrate_button.configure(fg='green')

    def _add_beam_frame(self):
        beam_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Beam', width=10)
        row_frame = [None]*7
        row_frame[0] = p.Page(beam_frame)
        row_frame[1] = p.Page(beam_frame)
        row_frame[2] = p.Page(beam_frame)
        row_frame[3] = p.Page(beam_frame)

        self.beam_index_label = tk.Label(row_frame[0], text='Index')
        beam_index_value_list = list(range(0,self.MAX_BEAM_INDEX+1))
        self.selected_beam_index = tk.StringVar(value=beam_index_value_list[0])
        def on_beam_index_changed(beam_index):
            if beam_index.get() != str(self.set_beam_index['idx']):
                self.beam_set_button.configure(fg='red')
        self.selected_beam_index.trace('w', lambda *_, beam_index=self.selected_beam_index: on_beam_index_changed(beam_index))
        self.beam_index_selector = ttk.Combobox(row_frame[0], values=beam_index_value_list, width=10, textvariable=self.selected_beam_index)

        self.beam_pol_label = tk.Label(row_frame[1], text='Polarization')
        beam_pol_value_list = ['TVTH', 'TV', 'TH']
        self.selected_beam_pol = tk.StringVar(value=beam_pol_value_list[0])
        def on_beam_pol_changed(beam_pol):
            if beam_pol.get() != str(self.set_beam_index['pol']):
                self.beam_set_button.configure(fg='red')
        self.selected_beam_pol.trace('w', lambda *_, beam_pol=self.selected_beam_pol: on_beam_pol_changed(beam_pol))
        self.beam_pol_selector = ttk.Combobox(row_frame[1], values=beam_pol_value_list, width=10, state='readonly', textvariable=self.selected_beam_pol)

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

    def _add_bb_gain_frame(self):
        gain_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='BB Gain', width=10)
        row_frame = [None]*4
        row_frame[0] = p.Page(gain_frame)
        row_frame[1] = p.Page(gain_frame)
        row_frame[2] = p.Page(gain_frame)
        row_frame[3] = p.Page(gain_frame)

        self.tx_bb_gain_value_list = []
        for n in range(0x20):
            self.tx_bb_gain_value_list.append(fhex(n,2))

        self.bbv_label = tk.Label(row_frame[0], text='V')
        self.selected_bbv = tk.StringVar(value=self.tx_bb_gain_value_list[0])
        def on_bbv_gain_changed(bbv_gain):
            if bbv_gain.get() != str(self.set_bb_gain['bbv']):
                self.bb_gain_set_button.configure(fg='red')
        self.selected_bbv.trace('w', lambda *_, bbv_gain=self.selected_bbv: on_bbv_gain_changed(bbv_gain))
        self.bbv_selector = ttk.Combobox(row_frame[0], values=self.tx_bb_gain_value_list, width=10, textvariable=self.selected_bbv)

        self.bbh_label = tk.Label(row_frame[1], text='H')
        self.selected_bbh = tk.StringVar(value=self.tx_bb_gain_value_list[0])
        def on_bbh_gain_changed(bbh_gain):
            if bbh_gain.get() != str(self.set_bb_gain['bbh']):
                self.bb_gain_set_button.configure(fg='red')
        self.selected_bbh.trace('w', lambda *_, bbh_gain=self.selected_bbh: on_bbh_gain_changed(bbh_gain))
        self.bbh_selector = ttk.Combobox(row_frame[1], values=self.tx_bb_gain_value_list, width=10, textvariable=self.selected_bbh)

        separator = ttk.Separator(row_frame[2], orient='horizontal')

        self.bb_gain_set_button = tk.Button(row_frame[3], text='Set', command=self._bb_gain_set)

        # Pack section

        self.bbv_label.pack(side='left', padx=4, pady=4)
        self.bbv_selector.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.bbh_label.pack(side='left', padx=4, pady=4)
        self.bbh_selector.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        self.bb_gain_set_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        gain_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')
        self.set_bb_gain = {'bbv':None, 'bbh':None}


    def _add_rf_gain_frame(self):
        gain_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='RF Gain', width=10)
        row_frame = [None]*4
        row_frame[0] = p.Page(gain_frame)
        row_frame[1] = p.Page(gain_frame)
        row_frame[2] = p.Page(gain_frame)
        row_frame[3] = p.Page(gain_frame)

        self.rfidx_value_list = []
        for n in range(64):
            self.rfidx_value_list.append(n)
        self.rfidx_label = tk.Label(row_frame[0], text='RF index')
        self.selected_rfidx = tk.StringVar(value=self.rfidx_value_list[0])
        def on_rfidx_changed(rfidx):
            if rfidx.get() != str(self.set_rf_gain['idx']):
                self.rf_gain_set_button.configure(fg='red')
        self.selected_rfidx.trace('w', lambda *_, rfidx=self.selected_rfidx: on_rfidx_changed(rfidx))
        self.rfidx_selector = ttk.Combobox(row_frame[0], values=self.rfidx_value_list, width=10, textvariable=self.selected_rfidx)

        self.gain_pol_label = tk.Label(row_frame[1], text='Polarization')
        self.gain_pol_value_list = ['TVTH', 'TV', 'TH']
        self.selected_gain_pol = tk.StringVar(value=self.gain_pol_value_list[0])
        def on_gain_pol_changed(gain_pol):
            if gain_pol.get() != str(self.set_rf_gain['pol']):
                self.rf_gain_set_button.configure(fg='red')
        self.selected_gain_pol.trace('w', lambda *_, gain_pol=self.selected_gain_pol: on_gain_pol_changed(gain_pol))
        self.gain_pol_selector = ttk.Combobox(row_frame[1], state='readonly', values=self.gain_pol_value_list, width=10, textvariable=self.selected_gain_pol)

        separator = ttk.Separator(row_frame[2], orient='horizontal')

        self.rf_gain_set_button = tk.Button(row_frame[3], text='Set', command=self._rf_gain_set)

        # Pack section

        self.rfidx_label.pack(side='left', padx=4, pady=4)
        self.rfidx_selector.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.gain_pol_label.pack(side='left', padx=4, pady=4)
        self.gain_pol_selector.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        self.rf_gain_set_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        gain_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')
        self.set_rf_gain = {'idx':None, 'pol':None}

    def _add_calib_frame(self):
        calib_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Calibrate DCO', width=10)
        row_frame = [None]*5
        row_frame[0] = p.Page(calib_frame)
        row_frame[1] = p.Page(calib_frame)
        row_frame[2] = p.Page(calib_frame)
        row_frame[3] = p.Page(calib_frame)
        row_frame[4] = p.Page(calib_frame)

        #self.calib_gain_index_label = tk.Label(row_frame[0], text='Gain index')
        #calib_gain_index_value_list = list(range(64))
        #self.selected_calib_gain_index = tk.StringVar(value=calib_gain_index_value_list[0])
        #self.calib_gain_index_selector = ttk.Combobox(row_frame[0], values=calib_gain_index_value_list, width=10, textvariable=self.selected_calib_gain_index)

        self.calib_pol_label = tk.Label(row_frame[1], text='TX Polarization')
        calib_pol_value_list = ['TH', 'TV']
        self.selected_calib_pol = tk.StringVar(value=calib_pol_value_list[0])
        def on_tx_pol_changed(tx_pol):
            if tx_pol.get() != str(self.set_calib_setting['tx_pol']):
                self.calibrate_button.configure(fg='red')
        self.selected_calib_pol.trace('w', lambda *_, tx_pol=self.selected_calib_pol: on_tx_pol_changed(tx_pol))
        self.calib_pol_selector = ttk.Combobox(row_frame[1], values=calib_pol_value_list, width=10, state='readonly', textvariable=self.selected_calib_pol)

        self.cross_pol_calib_label = tk.Label(row_frame[2], text='Cross Pol. Calib.')
        cross_pol_calib_value_list = ['Yes', 'No']
        self.selected_cross_pol_calib = tk.StringVar(value=cross_pol_calib_value_list[0])
        def on_cross_pol_calib_changed(cross_pol_calib):
            if cross_pol_calib.get() != str(self.set_calib_setting['cross_pol']):
                self.calibrate_button.configure(fg='red')
        self.selected_cross_pol_calib.trace('w', lambda *_, cross_pol_calib=self.selected_cross_pol_calib: on_cross_pol_calib_changed(cross_pol_calib))
        self.cross_pol_calib_selector = ttk.Combobox(row_frame[2], values=cross_pol_calib_value_list, width=10, state='readonly', textvariable=self.selected_cross_pol_calib)


        separator = ttk.Separator(row_frame[3], orient='horizontal')

        self.calibrate_button = tk.Button(row_frame[4], text='Calibrate', command=self._calibrate)

        # Pack section

        #self.calib_gain_index_label.pack(side='left', padx=4, pady=4)
        #self.calib_gain_index_selector.pack(side='right', padx=4, pady=4)
        #row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.calib_pol_label.pack(side='left', padx=4, pady=4)
        self.calib_pol_selector.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        self.cross_pol_calib_label.pack(side='left', padx=4, pady=4)
        self.cross_pol_calib_selector.pack(side='right', padx=4, pady=4)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[3].pack(side = 'top', expand = True, fill = 'both')

        self.calibrate_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[4].pack(side = 'top', expand = True, fill = 'both')

        calib_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')

        self.set_calib_setting = {'tx_pol':None, 'cross_pol':None}

    def _add_override_frame(self):
        override_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Override', width=10)
        row_frame = [None]*4
        row_frame[0] = p.Page(override_frame)

        self.override_label = tk.Label(row_frame[0], text='')
        override_value_list = ['On','Off']
        self.selected_override = tk.StringVar(value=override_value_list[0])
        def on_selected_override_changed(override):
            self.ta.override(self.dev, override.get())
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
        mode_value_list = ['IF','BB']
        self.selected_mode = tk.StringVar(value=mode_value_list[0])
        def on_mode_changed(mode):
            if mode.get() != str(self.set_setup['mode']):
                self.setup_set_button.configure(fg='red')
        self.selected_mode.trace('w', lambda *_, mode=self.selected_mode: on_mode_changed(mode))
        self.mode_selector = ttk.Combobox(row_frame[0], values=mode_value_list, state='readonly', width=10, textvariable=self.selected_mode)

        self.polarization_label = tk.Label(row_frame[1], text='Polarization')
        polarization_value_list = ['TVTH', 'TH', 'TV']
        self.selected_polarization = tk.StringVar(value=polarization_value_list[0])
        def on_pol_changed(pol):
            if pol.get() != str(self.set_setup['pol']):
                self.setup_set_button.configure(fg='red')
        self.selected_polarization.trace('w', lambda *_, pol=self.selected_polarization: on_pol_changed(pol))
        self.polarization_selector = ttk.Combobox(row_frame[1], values=polarization_value_list, state='readonly', width=10, textvariable=self.selected_polarization)

        self.ant_en_v_label = tk.Label(row_frame[2], text='ANT_EN_V')
        ant_en_value_list = ['0x0000', '0x0100', '0x0180', '0x0380', '0x03c0', '0x07c0', '0x07e0', '0x0fe0', '0x0ff0', '0x1ff0', '0x1ff8', '0x3ff8', '0x3ffc', '0x7ffc', '0x7ffe', '0xfffe', '0xffff']
        self.selected_ant_en_v = tk.StringVar(value=ant_en_value_list[16])
        def on_ant_en_v_changed(ant_en_v):
            if ant_en_v.get() != str(self.set_setup['ant_en_v']):
                self.setup_set_button.configure(fg='red')
        self.selected_ant_en_v.trace('w', lambda *_, ant_en_v=self.selected_ant_en_v: on_ant_en_v_changed(ant_en_v))
        self.ant_en_v_selector = ttk.Combobox(row_frame[2], values=ant_en_value_list, state='normal', width=10, textvariable=self.selected_ant_en_v)

        self.ant_en_h_label = tk.Label(row_frame[3], text='ANT_EN_H')
        self.selected_ant_en_h = tk.StringVar(value=ant_en_value_list[16])
        def on_ant_en_h_changed(ant_en_h):
            if ant_en_h.get() != str(self.set_setup['ant_en_h']):
                self.setup_set_button.configure(fg='red')
        self.selected_ant_en_h.trace('w', lambda *_, ant_en_h=self.selected_ant_en_h: on_ant_en_h_changed(ant_en_h))
        self.ant_en_h_selector = ttk.Combobox(row_frame[3], values=ant_en_value_list, state='normal', width=10, textvariable=self.selected_ant_en_h)

        separator = ttk.Separator(row_frame[4], orient='horizontal')

        self.setup_set_button = tk.Button(row_frame[5], text='Set', command=self.setup_set)
        self.set_setup = {'mode':None, 'pol':None, 'lat':None, 'ant_en_v':None, 'ant_en_h':None}

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
        self.bb_gain_set_button.configure(fg='black')
        self.rf_gain_set_button.configure(fg='black')
        self.beam_set_button.configure(fg='black')
        self.calibrate_button.configure(fg='black')
        self.override_selector.current(0)

