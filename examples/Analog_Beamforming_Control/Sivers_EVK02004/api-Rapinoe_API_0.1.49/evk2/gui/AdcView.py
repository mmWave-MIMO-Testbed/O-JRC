import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import Variables as var

class AdcView():

    def __init__(self, parent, main_view, dev, *args, **kwargs):
        self.main_view = main_view
        self.dev = dev
        self.id = id

        self.amux_src = list(main_view.gui_data.exec_command('self._host.chip.adc.amux.src.keys()'))
        self.amux_src = ['No source'] + self.amux_src

        def amux_src_selected(*args):
            pass

        self.adcBox = p.Page(parent, borderwidth=2, relief=tk.RIDGE, pady=10)
        amuxPage = p.Page(self.adcBox)
        valuePage = p.Page(self.adcBox)

        self.selected_amux_src = tk.StringVar()
        self.amux_src_menu = ttk.Combobox(amuxPage, values=self.amux_src, textvariable=self.selected_amux_src, validatecommand=amux_src_selected, state='readonly')
        self.amux_src_menu.current(0)
        self.selected_amux_src.set(self.amux_src[0])
        self.amux_src_menu.pack(side="top", anchor="ne", fill="both", expand=True)

        self.adcValue = tk.StringVar()
        self.adcValue.set('-')
        self.valueLabel = tk.Label(valuePage, fg='white', text=self.adcValue.get(), background=var._BACKGROUND, font=("Arial", 25), width=8, height=2)
        self.valueLabel.pack(side="bottom", anchor="ne", fill="both", expand=False)
        valuePage.pack(side="bottom", anchor="ne", fill="y", expand=True)

        amuxPage.pack(side="top", anchor="nw", fill="none", expand=False)
        self.adcBox.pack(side="left", anchor="nw", fill="none")

    def remove(self):
        self.adcBox.destroy()

    def poll(self):
        amux_src = self.selected_amux_src.get()
        if amux_src != 'No source':
            adc_value = self.main_view.gui_data.read_adc(amux_src)
            self.adcValue.set('{:f}'.format(adc_value))
            self.valueLabel.configure(text=self.adcValue.get())
        else:
            self.adcValue.set('-')
            self.valueLabel.configure(text=self.adcValue.get())