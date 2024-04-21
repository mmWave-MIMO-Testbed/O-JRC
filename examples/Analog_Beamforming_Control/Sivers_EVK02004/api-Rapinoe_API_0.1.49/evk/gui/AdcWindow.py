import evk.gui.Page as p
import tkinter as tk
import tkinter.ttk as ttk

import evk.gui.AdcView
import evk.gui.actions.adc_actions as adc_actions

ADC_VIEWS_PER_ROW = 7

class AdcWindow():

    def __init__(self, parent, gui_handler, dev, *args, **kwargs):
        self.gui_handler = gui_handler
        self.host = gui_handler.host
        self.dev = dev
        self.parent = parent
        self.adc_view = [] 
        self.adcRow = []

        adc_control_frame = p.Page(parent)
        adc_enable_button = tk.Button(adc_control_frame, text='Enable', font=("ariel", "12", "normal"), command=self._adc_enable)
        adc_enable_button.pack(side="top", fill="none", anchor=tk.CENTER, padx=10, pady=10)
        adc_control_frame.pack(side="top", fill="none", anchor=tk.CENTER)

        buttonRow = p.Page(parent)
        self.adcRow.append(p.Page(parent))

        self._img0 = tk.PhotoImage(file="evk/gui/images/add_view.png")
        self._img1 = tk.PhotoImage(file="evk/gui/images/remove_view.png")

        addViewButton = ttk.Button(buttonRow, image=self._img0, text='Add', command=self.add_adc_view)
        removeViewButton = ttk.Button(buttonRow, image=self._img1, text='Remove', command=self.remove_adc_view)
        buttonRow.pack(side="top")
        addViewButton.pack(side="left", fill="none", anchor="nw")
        removeViewButton.pack(side="top", fill="none", anchor="nw")
        self.adcRow[0].pack(side="top", anchor="nw", fill="both", expand=True)

    def add_adc_view(self):
        row = len(self.adc_view) // ADC_VIEWS_PER_ROW
        if row > len(self.adcRow)-1:
            # Create new row
            self.adcRow.append(p.Page(self.parent))
            self.adcRow[len(self.adcRow)-1].pack(side="top", anchor="nw", fill="both", expand=True)

        self.adc_view.append(evk.gui.AdcView.AdcView(self.adcRow[row], self.gui_handler, self.dev))

    def remove_adc_view(self):
        if len(self.adc_view) > 0:
            self.adc_view.pop().remove()

    def poll(self):
        for i in range(len(self.adc_view)):
            self.adc_view[i].poll()

    def _adc_enable(self):
        aa = adc_actions.AdcActions(self.host)
        aa.enable(self.dev)

