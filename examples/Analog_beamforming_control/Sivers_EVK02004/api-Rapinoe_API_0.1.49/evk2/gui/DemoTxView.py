import os
import sys

import Page as p
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkFileDialog

import RegFieldView
import actions.demo_actions

DEMO_TX_RAM_INDEX = 0

class DemoTxView():

    def __init__(self, parent, gui_data, dev, *args, **kwargs):
        self.gui_data = gui_data
        self.dev = dev
        self.parent = parent
        self.da = actions.demo_actions.DemoActions(self.gui_data)

        self._tx_add_setup_and_update_frame()
        self._tx_add_lo_leakage_adjust_frame()
        self._tx_add_tx_gain_adjust_frame()

    def _tx_add_setup_and_update_frame(self):
        # Setup and Update
        setup_update_frame = tk.LabelFrame(self.parent, relief=tk.GROOVE, text='Setup and Update', width=50, height=100, padx=15, pady=15)
        row_frame = [None]*3
        row_frame[0] = p.Page(setup_update_frame)
        row_frame[1] = p.Page(setup_update_frame)
        row_frame[2] = p.Page(setup_update_frame)
        self.script_name = tk.StringVar()
        self.script_name.set('demo_setup.py')
        self.script_name_field = tk.Entry(row_frame[0], width=27, textvariable=self.script_name)
        script_select_button = tk.Button(row_frame[0], text='...', command=self.select_script)
        self.setup_button = tk.Button(row_frame[1], text='Run', width=20, padx=20, pady=20, command=self._setup)
        self.update_button = tk.Button(row_frame[2], text='Update regs.', width=20, padx=20, pady=20, command=self._update)

        # Pack  section
        self.script_name_field.pack(side=tk.LEFT)
        script_select_button.pack(side=tk.LEFT)
        self.setup_button.pack()
        self.update_button.pack()
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')
        row_frame[2].pack(side = 'bottom', expand = True, fill = 'both')
        setup_update_frame.pack(side='left', expand=False, fill='none', padx=10, anchor='nw', ipady=10)

    def _tx_add_lo_leakage_adjust_frame(self):
        lo_leakage_adjust_frame = tk.LabelFrame(self.parent, relief=tk.GROOVE, text='LO leakage adjust', width=50, height=100, padx=15, pady=15)
        row_frame = [None]*2
        row_frame[0] = p.Page(lo_leakage_adjust_frame)
        row_frame[1] = p.Page(lo_leakage_adjust_frame)

        row_frame[0].pack(side = 'top', expand = True, fill = 'both')
        row_frame[1].pack(side = 'bottom', expand = True, fill = 'both')

        #parent, update_callback, host, dev, reg, button_text='Write changes',
        self.regfield_v = RegFieldView.RegFieldView(row_frame[0], self._value_changed_externally, self.gui_data, self.dev, 'bb_tx_dco_v', wr_button_text='Write', rd_button_text=None)
        self.regfield_h = RegFieldView.RegFieldView(row_frame[1], self._value_changed_externally, self.gui_data, self.dev, 'bb_tx_dco_h', wr_button_text='Write', rd_button_text=None)

        # Pack section
        lo_leakage_adjust_frame.pack(side='left', expand=False, fill='none', padx=10, anchor='nw', ipady=10)

    def _tx_add_tx_gain_adjust_frame(self):
        tx_gain_adjust_frame = tk.LabelFrame(self.parent, relief=tk.GROOVE, text='TX Gain', width=50, height=100, padx=15, pady=15)
        row_frame = [None]*3
        row_frame[0] = p.Page(tx_gain_adjust_frame)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')
        row_frame[1] = p.Page(tx_gain_adjust_frame)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')
        row_frame[2] = p.Page(tx_gain_adjust_frame)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')
        self.bb_tx_gain_regfield = RegFieldView.RegFieldView(row_frame[0], self._value_changed_externally, self.gui_data, self.dev, 'bb_tx_gain', wr_button_text='Write', rd_button_text=None)
        #tx_gain_adjust_frame.pack(side='left', expand=False, fill='none', padx=10, anchor='nw', ipady=10)
        self.tx_ram_v_regfield = RegFieldView.RegFieldView(row_frame[1], self._tx_ram_v_value_changed_externally, self.gui_data, self.dev, 'tx_ram_v', wr_button_text='Write & Sync', rd_button_text=None)
        self.tx_ram_v_regfield.row = DEMO_TX_RAM_INDEX
        #tx_gain_adjust_frame.pack(side='left', expand=False, fill='none', padx=10, anchor='nw')
        self.tx_ram_h_regfield = RegFieldView.RegFieldView(row_frame[2], self._tx_ram_h_value_changed_externally, self.gui_data, self.dev, 'tx_ram_h', wr_button_text='Write & Sync', rd_button_text=None)
        self.tx_ram_h_regfield.row = DEMO_TX_RAM_INDEX
        tx_gain_adjust_frame.pack(side='left', expand=False, fill='none', padx=10, anchor='nw')

    def _tx_ram_h_value_changed_externally(self):
        self.host.chip.tx.gain_rf(self.dev, DEMO_TX_RAM_INDEX, 'TH')

    def _tx_ram_v_value_changed_externally(self):
        self.host.chip.tx.gain_rf(self.dev, DEMO_TX_RAM_INDEX, 'TV')


    def _value_changed_externally(self):
        pass

    def _setup(self):
        script_file = self.script_name.get()
        if not script_file.endswith('.py'):
            script_file = script_file+'.py'
        if os.path.isfile(script_file):
            script_file_exist = True
        else:
            script_file_exist = False
            for dir in ['tests']:
                if os.path.isfile(os.path.join(dir,script_file)):
                    script_file = os.path.join(dir,script_file)
                    script_file_exist = True
                    break
            if not script_file_exist:
                print('No file found matching {}'.format(script_file))
                possible_script_files = []
                for dir in ['tests']+sys.path:
                    if os.path.isfile(os.path.join(dir,os.path.basename(script_file))):
                        possible_script_files.append(os.path.join(dir,os.path.basename(script_file)))
                if len(possible_script_files) > 0:
                    print('Maybe you meant one of these files?')
                    for file in possible_script_files:
                        print(file)
        if script_file_exist:
            self.da.run_script(script_file)

    def _update(self):
        self.regfield_v.read_reg_value()
        self.regfield_h.read_reg_value()
        self.bb_tx_gain_regfield.read_reg_value()
        self.tx_ram_v_regfield.read_reg_value()
        self.tx_ram_h_regfield.read_reg_value()

    def select_script(self):
        filename = tkFileDialog.askopenfile(initialdir = ".",title = "Select script file",defaultextension=".py",filetypes = (("Python files","*.py"),("all files","*.*")))
        if filename.name != None:
            self.script_name.set(filename.name)
            self.script_name_field.focus()
            self.script_name_field.xview_moveto(1)
