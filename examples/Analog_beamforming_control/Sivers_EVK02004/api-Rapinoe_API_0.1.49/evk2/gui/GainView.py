import os
import sys

import Page as p
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkFileDialog


import RegFieldView
import actions.gain__actions
import RamFileSelector

class GainView():

    def __init__(self, parent, gui_data, dev, mode, main_view, *args, **kwargs):
        self.gui_data = gui_data
        self.dev = dev
        self.parent = parent
        self.mode = mode.upper() # 'TX' or 'RX'
        self.top_row = p.Page(parent)
        self.bottom_row = p.Page(parent)

        self.gva = actions.gain__actions.GainActions(self.gui_data)

        self._add_load_and_select_frame()
        self._add_gain_adjust_frame()

        self.top_row.pack(side=tk.TOP, expand=True, anchor='nw')
        self.bottom_row.pack(side=tk.BOTTOM, expand=True, anchor='nw')

    def _add_load_and_select_frame(self):
        load_and_select_frame_frame = tk.Frame(self.top_row, relief=tk.GROOVE, width=50, height=100, padx=10, pady=10)
        row_frame = [None]*1
        row_frame[0] = p.Page(load_and_select_frame_frame)
        if self.mode == 'TX':
            load_ram_text = 'Load TX gain table'
        else:
            load_ram_text = 'Load RX gain table'
        self.ram_file_button = tk.Button(row_frame[0], text=load_ram_text, command=self.open_table_selector, width=16)
        self.ram_file_button.configure(bg='light grey')
        self.ram_file_button.pack(side='top', anchor='nw')

        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        load_and_select_frame_frame.pack(side='bottom', expand=False, fill='none', padx=10, anchor='nw', ipady=5)

    def _add_gain_adjust_frame(self):
        gain_adjust_frame = tk.Frame(self.bottom_row, relief=tk.GROOVE, width=50, height=100, padx=10, pady=10)
        row_frame = [None]*2
        row_frame[0] = p.Page(gain_adjust_frame)
        row_frame[0].pack(side = 'left', expand = True, fill = 'both', padx=10)
        row_frame[1] = p.Page(gain_adjust_frame)
        row_frame[1].pack(side = 'left', expand = True, fill = 'both', padx=10)

        # Left frame
        top_left_frame = p.Page(row_frame[0])
        bottom_left_frame = p.Page(row_frame[0])
        top_left_frame.pack(side = 'top', expand = True, fill = 'both')
        bottom_left_frame.pack(side = 'bottom', expand = True, fill = 'both')

        gain_index_label = tk.Label(top_left_frame, text=self.mode+' Gain Index')
        gain_index_value_list = list(range(64))
        if self.mode == 'RX':
            print('@@@@@@@@@@@@@@@@@')
            self.selected_gain_index_v = tk.IntVar(value=self.gui_data.read_register('rx_gain_indx_v'))
        else:
            command = "self._host.chip.tx.curr_gain_index(__RAP__, 'V')"
            value = self.gui_data.exec_command(command)
            self.selected_gain_index_v = tk.IntVar(value)
        def on_gain_index_v_changed(gain_index):
            self.ram_v_regfield.row = gain_index.get()
            self._update('V')
        self.selected_gain_index_v.trace('w', lambda *_, gain_index=self.selected_gain_index_v: on_gain_index_v_changed(gain_index))
        self.gain_index_v_selector = ttk.Combobox(top_left_frame, values=gain_index_value_list, width=10, state='readonly', textvariable=self.selected_gain_index_v)
        self.set_gain_index_button_v = tk.Button(top_left_frame, text='Set', command=self.set_gain_index_v, width=11)
        self.set_gain_index_button_v.pack(side='top', anchor='nw')
        gain_index_label.pack(side='left', anchor='nw', padx=4, pady=4)
        self.gain_index_v_selector.pack(side='left', anchor='nw', padx=4, pady=4)
        self.set_gain_index_button_v.pack(side='left', anchor='nw')

        # Right frame
        top_right_frame = p.Page(row_frame[1])
        bottom_right_frame = p.Page(row_frame[1])
        top_right_frame.pack(side = 'top', expand = True, fill = 'both')
        bottom_right_frame.pack(side = 'bottom', expand = True, fill = 'both')

        gain_index_label = tk.Label(top_right_frame, text=self.mode+' Gain Index')
        if self.mode == 'RX':
            self.selected_gain_index_h = tk.IntVar(value=self.gui_data.read_register('rx_gain_indx_h'))
        else:
            command = "self._host.chip.tx.curr_gain_index(__RAP__, 'H')"
            value = self.gui_data.exec_command(command)
            self.selected_gain_index_h = tk.IntVar(value)
        def on_gain_index_h_changed(gain_index):
            self.ram_h_regfield.row = gain_index.get()
            self._update('H')
        self.selected_gain_index_h.trace('w', lambda *_, gain_index=self.selected_gain_index_h: on_gain_index_h_changed(gain_index))
        self.gain_index_h_selector = ttk.Combobox(top_right_frame, values=gain_index_value_list, width=10, state='readonly', textvariable=self.selected_gain_index_h)
        self.set_gain_index_button_h = tk.Button(top_right_frame, text='Set', command=self.set_gain_index_h, width=11)
        self.set_gain_index_button_h.pack(side='top', anchor='nw')
        gain_index_label.pack(side='left', anchor='nw', padx=4, pady=4)
        self.gain_index_h_selector.pack(side='left', anchor='nw', padx=4, pady=4)
        self.set_gain_index_button_h.pack(side='left', anchor='nw')


        self.ram_v_regfield = RegFieldView.RegFieldView(bottom_left_frame, self._ram_v_value_changed_externally, self.gui_data, self.dev, self.mode.lower()+'_ram_v', wr_button_text='Write & Sync', rd_button_text=None)
        self.ram_v_regfield.row = self.selected_gain_index_v.get()
        self.ram_h_regfield = RegFieldView.RegFieldView(bottom_right_frame, self._ram_h_value_changed_externally, self.gui_data, self.dev, self.mode.lower()+'_ram_h', wr_button_text='Write & Sync', rd_button_text=None)
        self.ram_h_regfield.row = self.selected_gain_index_h.get()
        gain_adjust_frame.pack(side='bottom', expand=False, fill='none', padx=10, anchor='nw')
        self._update()

    def _ram_h_value_changed_externally(self):
        if self.mode == 'RX':
            self.gva.rx_gain(self.selected_gain_index_h.get(), 'H')
        else:
            self.gva.tx_gain(self.selected_gain_index_h.get(), 'H')

    def _ram_v_value_changed_externally(self):
        if self.mode == 'RX':
            self.gva.rx_gain(self.selected_gain_index_v.get(), 'V')
        else:
            self.gva.tx_gain(self.selected_gain_index_v.get(), 'V')

    def _update(self, pol=None):
        if pol == 'V' or pol == None:
            self.ram_v_regfield.read_reg_value()
        if pol == 'H' or pol == None:
            self.ram_h_regfield.read_reg_value()

    def open_table_selector(self):
        filename = tkFileDialog.askopenfile(initialdir = "./config/ram",title = "Select RAM file",defaultextension=".xml",filetypes = (("XML files","*.xml"),("all files","*.*")))
        if filename != None:
            if self.mode == 'RX':
                filter = ['RX_RAM_H', 'RX_RAM_V']
            else:
                filter = ['TX_RAM_H', 'TX_RAM_V']
            ram_file_selector = RamFileSelector.RamFileSelector(self.parent, filename.name, filter=filter, select_callback=self.ram_table_selected)

    def ram_table_selected(self, filename, table_id):
        r = self.gui_handler.host.chip.ram.fill(self.dev, table_id=table_id, filename=filename)
        self._update()

    def set_gain_index_v(self):
        if self.mode == 'RX':
            self.host.chip.rx.gain(self.dev, self.selected_gain_index_v.get(), 'RV')
        else:
            self.host.chip.tx.gain_rf(self.dev, self.selected_gain_index_v.get(), 'TV')

    def set_gain_index_h(self):
        if self.mode == 'RX':
            self.host.chip.rx.gain(self.dev, self.selected_gain_index_h.get(), 'RH')
        else:
            self.host.chip.tx.gain_rf(self.dev, self.selected_gain_index_h.get(), 'TH')
