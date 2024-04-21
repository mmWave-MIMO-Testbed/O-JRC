import evk.gui.Page as p
import tkinter as tk
import tkinter.ttk as ttk

import evk.gui.TxView
import evk.gui.RxView
import evk.gui.GeneralView


class TxRxWindow():

    def __init__(self, parent, gui_handler, dev, main_view, *args, **kwargs):
        self.gui_handler = gui_handler
        self.host = gui_handler.host
        self.dev = dev
        self.parent = parent
        #self.main_page = p.Page(parent, borderwidth=2, relief=tk.RIDGE, pady=10)
        self.main_page = p.Page(self.parent)
        self.general_view = evk.gui.GeneralView.GeneralView(self.main_page, self.gui_handler, self.dev, self)
        self.tx_view = evk.gui.TxView.TxView(self.main_page, self.gui_handler, self.dev, main_view)
        self.rx_view = evk.gui.RxView.RxView(self.main_page, self.gui_handler, self.dev, main_view)
        self.main_page.pack(expand=True, fill='both')

    def reset(self):
        self.tx_view.reset()
        self.rx_view.reset()