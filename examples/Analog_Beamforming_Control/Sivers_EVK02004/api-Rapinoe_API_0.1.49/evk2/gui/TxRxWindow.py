import Page as p
import tkinter as tk
import tkinter.ttk as ttk

import TxView
import RxView
import GeneralView


class TxRxWindow():

    def __init__(self, parent, gui_data, dev, main_view, *args, **kwargs):
        self.gui_data = gui_data
        self.dev = dev
        self.parent = parent
        #self.main_page = p.Page(parent, borderwidth=2, relief=tk.RIDGE, pady=10)
        self.main_page = p.Page(self.parent)
        self.general_view = GeneralView.GeneralView(self.main_page, self.gui_data, self.dev, self)
        self.tx_view = TxView.TxView(self.main_page, self.gui_data, self.dev, main_view)
        self.rx_view = RxView.RxView(self.main_page, self.gui_data, self.dev, main_view)
        self.main_page.pack(expand=True, fill='both')
    def reset(self):
        self.tx_view.reset()
        self.rx_view.reset()