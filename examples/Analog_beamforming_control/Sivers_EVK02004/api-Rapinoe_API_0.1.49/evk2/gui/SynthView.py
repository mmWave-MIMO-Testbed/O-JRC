import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import Variables as var

import actions.synth_actions as synth_actions

class SynthView():

    def __init__(self, parent, gui_handler, dev, *args, **kwargs):
        self.gui_handler = gui_handler
        self.host = gui_handler.host
        self.dev = dev
        self.parent = parent
        self.label_frame = tk.LabelFrame(self.parent, relief=tk.GROOVE, text='Synth')

        self._add_setup_frame()
        #self._add_gain_frame()
        #self._add_beam_frame()

        self.label_frame.pack(expand=True, fill='both')


    def _add_setup_frame(self):
        setup_frame = tk.LabelFrame(self.label_frame, relief=tk.GROOVE, text='Setup', width=10)
        row_frame = [None]*7
        row_frame[0] = p.Page(setup_frame)
        row_frame[1] = p.Page(setup_frame)
        row_frame[2] = p.Page(setup_frame)
        row_frame[3] = p.Page(setup_frame)
        row_frame[4] = p.Page(setup_frame)
        row_frame[5] = p.Page(setup_frame)
        row_frame[6] = p.Page(setup_frame)

        self.rf_freq_label = tk.Label(row_frame[0], text='RF Freq. [Hz]')
        self.rf_freq = tk.StringVar(value='26000000000')
        self.rf_freq_entry = ttk.Entry(row_frame[0], width=12, textvariable=self.rf_freq)

        self.fractional_label = tk.Label(row_frame[1], text='Fractional')
        self.fractional_value_list = ['Yes', 'No']
        self.selected_fractional = tk.StringVar(value=self.fractional_value_list[0])
        self.fractional_selector = ttk.Combobox(row_frame[1], values=self.fractional_value_list, state='readonly', width=10, textvariable=self.selected_fractional)

        self.sd_order_label = tk.Label(row_frame[2], text='SD order')
        self.sd_order_value_list = ['0','1','2', '3']
        self.selected_sd_order = tk.StringVar(value=self.sd_order_value_list[2])
        self.sd_order_selector = ttk.Combobox(row_frame[2], values=self.sd_order_value_list, state='readonly', width=10, textvariable=self.selected_sd_order)

        separator = ttk.Separator(row_frame[5], orient='horizontal')

        self.setup_set_button = tk.Button(row_frame[6], text='Set', command=self.setup_set)

        # Pack section

        self.rf_freq_label.pack(side='left', padx=4, pady=4)
        self.rf_freq_entry.pack(side='right', padx=4, pady=4)
        row_frame[0].pack(side = 'top', expand = True, fill = 'both')

        self.fractional_label.pack(side='left', padx=4, pady=4)
        self.fractional_selector.pack(side='right', padx=4, pady=4)
        row_frame[1].pack(side = 'top', expand = True, fill = 'both')

        self.sd_order_label.pack(side='left', padx=4, pady=4)
        self.sd_order_selector.pack(side='right', padx=4, pady=4)
        row_frame[2].pack(side = 'top', expand = True, fill = 'both')

        separator.pack(side='left', padx=4, pady=12, fill='x', expand=True)
        row_frame[5].pack(side = 'top', expand = True, fill = 'both')

        self.setup_set_button.pack(side='left', padx=20, pady=4, expand = True, fill = 'both')
        row_frame[6].pack(side = 'top', expand = True, fill = 'both')

        setup_frame.pack(side='left', expand=False, fill='none', padx=4, anchor='nw')

    def setup_set(self):
        try:
            freq_rff = int(self.rf_freq.get())
        except:
            pass
        if self.selected_fractional.get() == 'Yes':
            frac_mode = True
        else:
            frac_mode = False

        sd_order = int(self.selected_sd_order.get())

        sa = synth_actions.SynthActions(self.host)
        sa.setup_set(freq_rff, frac_mode, sd_order)


        #self.host.chip.init(self.dev, 'CHIP')
        #self.host.chip.init(self.dev, 'SYNTH')
        #self.host.chip.init(self.dev, 'VALIDATION')
        #self.host.chip.init(self.dev, 'ADC')
        #self.host.chip.synth.setup(self.dev)
        #self.host.chip.synth.set(self.dev,freq_rff, frac_mode=frac_mode, sd_order=sd_order)
